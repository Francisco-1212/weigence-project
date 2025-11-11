"""Modular IA engine with configurable rules and scoring."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

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
class EngineInsight:
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
    """Loads rules and templates from JSON files."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> Dict[str, object]:
        if not self._path.exists():
            raise FileNotFoundError(f"No se encontró la configuración IA en {self._path}")

        contenido = self._path.read_text(encoding="utf-8")
        return json.loads(contenido)


class IAEngine:
    """Evaluates configurable rules against IASnapshot metrics."""

    _DEFAULT_THRESHOLDS = {"warning": 0.45, "critical": 0.7}

    def __init__(self, config_path: Optional[Path] = None) -> None:
        base_path = Path(__file__).resolve().parent / "config" / "ia_engine.json"
        self._config_path = config_path or base_path
        raw_config = ConfigLoader(self._config_path).load()
        self._profiles: Dict[str, dict] = raw_config.get("profiles", {})  # type: ignore[assignment]
        self._templates: Dict[str, dict] = raw_config.get("templates", {})  # type: ignore[assignment]
        self._thresholds = {
            **self._DEFAULT_THRESHOLDS,
            **raw_config.get("score_thresholds", {}),  # type: ignore[arg-type]
        }

        if not self._profiles:
            raise ValueError("La configuración del motor IA no define perfiles.")

    @property
    def templates(self) -> Dict[str, dict]:
        return self._templates

    def evaluate(self, snapshot: IASnapshot, *, profile: str) -> EngineInsight:
        perfil_cfg = self._profiles.get(profile)
        if not perfil_cfg:
            logger.warning(
                "[IAEngine] Perfil '%s' no encontrado, usando perfil_operativo por defecto",
                profile,
            )
            perfil_cfg = self._profiles.get("perfil_operativo", next(iter(self._profiles.values())))
            profile = "perfil_operativo"

        metricas = self._extraer_metricas(snapshot)
        reglas = [self._parse_regla(item) for item in perfil_cfg.get("rules", [])]

        mejor: Optional[EngineInsight] = None
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
                name=str(metric["name"]),
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
    ) -> Optional[EngineInsight]:
        contributions: List[float] = []
        drivers: List[str] = []

        for config in regla.metrics:
            valor = metricas.get(config.name)
            if valor is None:
                continue

            score = self._calcular_contribucion(valor, config)
            if score <= 0:
                continue

            contributions.append(score * config.weight)
            if config.phrase:
                try:
                    drivers.append(config.phrase.format(valor=valor))
                except Exception:  # pragma: no cover - defensa
                    drivers.append(config.phrase)

        if not contributions:
            return None

        score_total = sum(contributions)
        if score_total < regla.minimum_score:
            return None

        severity = self._clasificar_severidad(score_total, regla.severity_thresholds)
        confidence = min(1.0, max(0.0, score_total))
        data_points = {metric.name: metricas.get(metric.name, 0.0) for metric in regla.metrics}

        extra = self._aplicar_modificadores(regla.modifiers, metricas, snapshot)
        summary = regla.summary.format(**{**metricas, **extra}) if regla.summary else ""

        return EngineInsight(
            key=regla.key,
            template=regla.template,
            severity=severity,
            profile=profile,
            score=score_total,
            confidence=confidence,
            summary=summary,
            drivers=drivers,
            data_points=data_points,
            extra_context=extra,
        )

    def _calcular_contribucion(self, valor: float, config: MetricRule) -> float:
        direction = config.direction.lower()
        threshold = config.threshold
        delta = valor - threshold

        if direction == "below":
            delta = threshold - valor
        elif direction == "between":
            rango = abs(threshold - config.scale)
            if rango == 0:
                return 0.0
            delta = max(0.0, 1 - abs(valor - threshold) / rango)
        else:
            delta = valor - threshold

        score = max(0.0, delta / max(abs(threshold) or 1.0, 1.0))
        score = min(score * config.scale, config.clamp)
        return score

    def _clasificar_severidad(self, score: float, custom: Dict[str, float]) -> str:
        thresholds = {**self._thresholds, **custom}
        if score >= thresholds.get("critical", 0.8):
            return "critical"
        if score >= thresholds.get("warning", 0.5):
            return "warning"
        return "info"

    def _aplicar_modificadores(
        self,
        modifiers: Iterable[Dict[str, object]],
        metricas: Dict[str, float],
        snapshot: IASnapshot,
    ) -> Dict[str, float]:
        extra: Dict[str, float] = {}
        for modifier in modifiers:
            tipo = modifier.get("type")
            if tipo == "add_metric":
                nombre = modifier.get("name")
                origen = modifier.get("source")
                if isinstance(nombre, str) and isinstance(origen, str):
                    extra[nombre] = float(metricas.get(origen, 0.0))
            elif tipo == "snapshot_field":
                nombre = modifier.get("name")
                campo = modifier.get("field")
                if isinstance(nombre, str) and isinstance(campo, str):
                    extra[nombre] = float(getattr(snapshot, campo, 0.0) or 0.0)
        return extra

    def _fallback(
        self,
        perfil_cfg: dict,
        metricas: Dict[str, float],
        snapshot: IASnapshot,
        profile: str,
    ) -> EngineInsight:
        template = perfil_cfg.get("fallback_template", "estado_estable")
        summary = perfil_cfg.get("fallback_summary", "Sin anomalías relevantes detectadas")
        drivers = perfil_cfg.get("fallback_drivers", [])
        if not isinstance(drivers, list):
            drivers = []

        return EngineInsight(
            key=str(perfil_cfg.get("fallback_key", "stable_outlook")),
            template=str(template),
            severity="info",
            profile=profile,
            score=metricas.get("signal_strength", 0.1),
            confidence=0.45,
            summary=str(summary),
            drivers=[str(item) for item in drivers if item],
            data_points=metricas,
            extra_context={},
        )

    def _extraer_metricas(self, snapshot: IASnapshot) -> Dict[str, float]:
        return {
            "trend_percent": float(snapshot.sales_trend_percent or 0.0),
            "sales_anomaly_score": float(snapshot.sales_anomaly_score or 0.0),
            "sales_volatility": float(snapshot.sales_volatility or 0.0),
            "last_sale_total": float(snapshot.last_sale_total or 0.0),
            "baseline_sale": float(snapshot.baseline_sale or 0.0),
            "weight_volatility": float(snapshot.weight_volatility or 0.0),
            "weight_change_rate": float(snapshot.weight_change_rate or 0.0),
            "last_weight": float(snapshot.last_weight or 0.0),
            "critical_alerts": float(snapshot.critical_alerts or 0),
            "warning_alerts": float(snapshot.warning_alerts or 0),
            "info_alerts": float(snapshot.info_alerts or 0),
            "alerts_total": float(sum(snapshot.alerts_summary.values())),
            "movements_per_hour": float(snapshot.movements_per_hour or 0.0),
            "inactivity_hours": float(snapshot.inactivity_hours or 0.0),
            "signal_strength": float(snapshot.signal_strength or 0.0),
        }


engine = IAEngine()
