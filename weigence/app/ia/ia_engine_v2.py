"""Modular IA engine (v2) with configurable rules and scoring."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

from .ia_snapshots import IASnapshot

logger = logging.getLogger(__name__)


@dataclass
class MetricRule:
    """Configuration for a metric-based contribution."""

    name: str
    threshold: float
    weight: float = 1.0
    direction: str = "above"
    scale: float = 1.0
    phrase: str | None = None
    clamp: float = 1.0


@dataclass
class RuleConfig:
    """Higher level rule definition bound to a template."""

    key: str
    template: str
    summary: str
    metrics: List[MetricRule] = field(default_factory=list)
    modifiers: List[Dict[str, object]] = field(default_factory=list)
    severity_thresholds: Dict[str, float] = field(default_factory=dict)
    minimum_score: float = 0.0


@dataclass
class EngineV2Insight:
    """Insight result produced by the modular engine."""

    key: str
    template: str
    severity: str
    profile: str
    score: float
    confidence: float
    summary: str
    drivers: List[str]
    data_points: Dict[str, float]
    extra_context: Dict[str, float] = field(default_factory=dict)


class ConfigLoader:
    """Loads rules and templates from JSON or YAML files."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> Dict[str, object]:
        if not self._path.exists():
            raise FileNotFoundError(f"No se encontró la configuración IA v2 en {self._path}")

        contenido = self._path.read_text(encoding="utf-8")
        if self._path.suffix.lower() in {".yaml", ".yml"}:
            try:
                import yaml  # type: ignore
            except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
                raise RuntimeError(
                    "Se requiere PyYAML para cargar configuraciones YAML del motor IA v2."
                ) from exc
            return yaml.safe_load(contenido)  # type: ignore[no-any-return]
        return json.loads(contenido)


class IAEngineV2:
    """Evaluates configurable rules against IASnapshot metrics."""

    _DEFAULT_THRESHOLDS = {"warning": 0.45, "critical": 0.7}

    def __init__(self, config_path: Optional[Path] = None) -> None:
        base_path = Path(__file__).resolve().parent / "config" / "ia_engine_v2.json"
        self._config_path = config_path or base_path
        raw_config = ConfigLoader(self._config_path).load()
        self._profiles: Dict[str, dict] = raw_config.get("profiles", {})  # type: ignore[assignment]
        self._templates: Dict[str, dict] = raw_config.get("templates", {})  # type: ignore[assignment]
        self._thresholds = {
            **self._DEFAULT_THRESHOLDS,
            **raw_config.get("score_thresholds", {}),  # type: ignore[arg-type]
        }

        if not self._profiles:
            raise ValueError("La configuración del motor IA v2 no define perfiles.")

    @property
    def templates(self) -> Dict[str, dict]:
        return self._templates

    def evaluate(self, snapshot: IASnapshot, *, profile: str) -> EngineV2Insight:
        perfil_cfg = self._profiles.get(profile)
        if not perfil_cfg:
            logger.warning(
                "[IAEngineV2] Perfil '%s' no encontrado, usando perfil_operativo por defecto",
                profile,
            )
            perfil_cfg = self._profiles.get("perfil_operativo", next(iter(self._profiles.values())))
            profile = "perfil_operativo"

        metricas = self._extraer_metricas(snapshot)
        reglas = [self._parse_regla(item) for item in perfil_cfg.get("rules", [])]

        mejor: Optional[EngineV2Insight] = None
        for regla in reglas:
            evaluacion = self._evaluar_regla(regla, metricas, snapshot, profile)
            if not evaluacion:
                continue
            if mejor is None or evaluacion.score > mejor.score:
                mejor = evaluacion

        if mejor is None:
            return self._fallback(perfil_cfg, metricas, snapshot, profile)

        return mejor

    # ------------------------------------------------------------------
    # Regla y métrica
    # ------------------------------------------------------------------
    def _parse_regla(self, data: dict) -> RuleConfig:
        metricas = [
            MetricRule(
                name=metric["name"],
                threshold=float(metric.get("threshold", 0.0)),
                weight=float(metric.get("weight", 1.0)),
                direction=str(metric.get("direction", "above")),
                scale=float(metric.get("scale", 1.0)),
                phrase=metric.get("phrase"),
                clamp=float(metric.get("clamp", 1.0)),
            )
            for metric in data.get("metrics", [])
        ]

        return RuleConfig(
            key=str(data.get("key")),
            template=str(data.get("template")),
            summary=str(data.get("summary", "")),
            metrics=metricas,
            modifiers=list(data.get("modifiers", [])),
            severity_thresholds=dict(data.get("severity", {})),
            minimum_score=float(data.get("minimum_score", 0.0)),
        )

    def _evaluar_regla(
        self,
        regla: RuleConfig,
        metricas: Dict[str, float],
        snapshot: IASnapshot,
        profile: str,
    ) -> Optional[EngineV2Insight]:
        if not regla.metrics:
            return None

        puntuacion_total = 0.0
        peso_total = 0.0
        drivers: List[str] = []
        data_points: Dict[str, float] = {}

        for metrica in regla.metrics:
            valor = metricas.get(metrica.name, 0.0)
            data_points[metrica.name] = valor
            aporte = self._puntuar_metrica(valor, metrica)
            if aporte <= 0:
                peso_total += metrica.weight
                continue
            peso_total += metrica.weight
            puntuacion_total += aporte * metrica.weight
            frase = metrica.phrase or self._frase_generica(metrica, valor)
            drivers.append(frase.format(value=valor, threshold=metrica.threshold))

        if peso_total <= 0:
            return None

        score_base = puntuacion_total / peso_total
        score_base = max(0.0, min(score_base, 1.0))

        modificadores = self._aplicar_modificadores(regla.modifiers, metricas, snapshot)
        score = max(0.0, min(score_base + modificadores, 1.0))

        if score < max(regla.minimum_score, 0.0):
            return None

        thresholds = {**self._thresholds, **regla.severity_thresholds}
        severity = self._resolver_severidad(score, thresholds)
        confidence = 0.5 + score / 2

        contexto_adicional = {
            "score": round(score, 3),
            "confidence": round(confidence, 3),
            "profile": profile,
        }

        return EngineV2Insight(
            key=regla.key,
            template=regla.template,
            severity=severity,
            profile=profile,
            score=score,
            confidence=confidence,
            summary=regla.summary,
            drivers=drivers,
            data_points=data_points,
            extra_context=contexto_adicional,
        )

    def _frase_generica(self, metrica: MetricRule, valor: float) -> str:
        nombre = metrica.name.replace("_", " ")
        if metrica.direction.lower() == "below":
            return f"{nombre} por debajo del umbral ({{value:.2f}} < {metrica.threshold:.2f})"
        if metrica.direction.lower() == "between":
            return f"{nombre} dentro de rango controlado"
        return f"{nombre} en nivel elevado ({{value:.2f}})"

    def _puntuar_metrica(self, valor: float, regla: MetricRule) -> float:
        escala = regla.scale if regla.scale not in (0, None) else 1.0
        direccion = regla.direction.lower()
        delta = 0.0

        if direccion == "above":
            delta = valor - regla.threshold
        elif direccion == "below":
            delta = regla.threshold - valor
        elif direccion == "outside":
            limite = abs(regla.threshold)
            if abs(valor) > limite:
                delta = abs(valor) - limite
        elif direccion == "between":
            limites = sorted((regla.threshold, regla.scale))
            escala = max(abs(limites[1] - limites[0]), 1.0)
            if limites[0] <= valor <= limites[1]:
                delta = min(valor - limites[0], limites[1] - valor)

        if delta <= 0:
            return 0.0

        normalizado = delta / (abs(escala) or 1.0)
        return max(0.0, min(normalizado, regla.clamp))

    def _aplicar_modificadores(
        self,
        modificadores: Sequence[Dict[str, object]],
        metricas: Dict[str, float],
        snapshot: IASnapshot,
    ) -> float:
        ajuste = 0.0
        for modificador in modificadores:
            tipo = str(modificador.get("type", "")).lower()
            peso = float(modificador.get("weight", 0.05))
            if tipo == "pattern_flag":
                bandera = str(modificador.get("flag"))
                if bandera and bandera in snapshot.pattern_flags:
                    ajuste += peso
            elif tipo == "metric_ratio":
                numerador = float(metricas.get(str(modificador.get("numerator")), 0.0))
                denominador = float(
                    metricas.get(str(modificador.get("denominator")), 1.0) or 1.0
                )
                if denominador == 0:
                    continue
                ratio = numerador / denominador
                umbral = float(modificador.get("threshold", 1.0))
                if ratio >= umbral:
                    ajuste += peso * min(ratio / (umbral or 1.0), 2.0)
            elif tipo == "co_presence":
                metric_list = modificador.get("metrics", [])
                if not isinstance(metric_list, Iterable):
                    continue
                umbral = float(modificador.get("threshold", 0.0))
                if all(metricas.get(str(nombre), 0.0) >= umbral for nombre in metric_list):
                    ajuste += peso

        return ajuste

    def _resolver_severidad(self, score: float, thresholds: Dict[str, float]) -> str:
        critico = thresholds.get("critical", self._DEFAULT_THRESHOLDS["critical"])
        advertencia = thresholds.get("warning", self._DEFAULT_THRESHOLDS["warning"])
        if score >= critico:
            return "critical"
        if score >= advertencia:
            return "warning"
        return "info"

    def _fallback(
        self,
        perfil_cfg: dict,
        metricas: Dict[str, float],
        snapshot: IASnapshot,
        profile: str,
    ) -> EngineV2Insight:
        template = str(perfil_cfg.get("fallback_template", "estado_estable"))
        drivers = ["Sin desviaciones significativas detectadas"]
        data_points = {
            "sales_trend_percent": metricas.get("sales_trend_percent", 0.0),
            "weight_volatility": metricas.get("weight_volatility", 0.0),
            "warning_alerts": metricas.get("warning_alerts", 0.0),
        }
        contexto_adicional = {
            "score": 0.0,
            "confidence": 0.5,
            "profile": profile,
        }

        return EngineV2Insight(
            key="estado_estable",
            template=template,
            severity="info",
            profile=profile,
            score=0.0,
            confidence=0.5,
            summary="Comportamiento operativo sin novedades relevantes",
            drivers=drivers,
            data_points=data_points,
            extra_context=contexto_adicional,
        )

    def _extraer_metricas(self, snapshot: IASnapshot) -> Dict[str, float]:
        metricas = {
            "sales_trend_percent": float(snapshot.sales_trend_percent or 0.0),
            "sales_anomaly_score": float(snapshot.sales_anomaly_score or 0.0),
            "sales_volatility": float(snapshot.sales_volatility or 0.0),
            "movements_per_hour": float(snapshot.movements_per_hour or 0.0),
            "inactivity_hours": float(snapshot.inactivity_hours or 0.0),
            "weight_volatility": float(snapshot.weight_volatility or 0.0),
            "weight_change_rate": float(snapshot.weight_change_rate or 0.0),
            "signal_strength": float(snapshot.signal_strength or 0.0),
            "critical_alerts": float(snapshot.critical_alerts or 0.0),
            "warning_alerts": float(snapshot.warning_alerts or 0.0),
            "sales_window_hours": float(snapshot.sales_window_hours or 0.0),
            "movement_window_hours": float(snapshot.movement_window_hours or 0.0),
        }

        # Ratios de apoyo para reglas combinadas
        if snapshot.weight_change_rate:
            metricas["sales_vs_inventory"] = float(
                abs(snapshot.sales_trend_percent or 0.0)
            ) + abs(snapshot.weight_change_rate)

        return metricas


__all__ = ["IAEngineV2", "EngineV2Insight"]
