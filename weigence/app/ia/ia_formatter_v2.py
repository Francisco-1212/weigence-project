"""Formatter v2 capable of composing narratives from configurable modules."""
from __future__ import annotations

import logging
import random
from typing import Dict, List

from .ia_engine_v2 import EngineV2Insight
from .ia_snapshots import IASnapshot


logger = logging.getLogger(__name__)


class IAFormatterV2:
    """Builds consistent outputs from the modular engine using templates."""

    def __init__(self, templates: Dict[str, dict]) -> None:
        self._templates = templates
        self._rng = random.SystemRandom()
        self._default_key = "estado_estable"

    def render(self, insight: EngineV2Insight, snapshot: IASnapshot) -> Dict[str, str]:
        template = self._templates.get(insight.template) or self._templates.get(
            self._default_key, {}
        )

        if not template:
            logger.warning(
                "[IAFormatterV2] Plantilla '%s' no encontrada, se utilizará fallback",
                insight.template,
            )
            template = self._templates.get(self._default_key, {})

        contexto = self._construir_contexto(insight, snapshot)
        titulo = self._elegir(template.get("titles", []), "Recomendación operativa")
        resumen = self._construir_mensaje(template.get("summary_modules", []), contexto, minimo=1)
        detalle_modulos = self._construir_mensaje(
            template.get("detail_modules", []), contexto, minimo=2
        )
        solucion = self._elegir(
            template.get("solutions", []),
            "Mantener monitoreo y validar manualmente los indicadores clave.",
        )

        resumen = resumen or insight.summary or "Sin novedades destacadas."
        detalle_base = detalle_modulos or insight.summary or resumen

        drivers = [d for d in insight.drivers if d]
        if drivers:
            drivers_text = "\n".join(f"- {driver}" for driver in drivers)
            detalle = (
                f"{detalle_base}\n\nIndicadores destacados:\n{drivers_text}\n"
                f"\nPerfil IA: {insight.profile} | Score: {insight.score:.2f}"
            )
        else:
            detalle = (
                f"{detalle_base}\n\nPerfil IA: {insight.profile} | Score: {insight.score:.2f}"
            )

        resultado = {
            "titulo": titulo,
            "mensaje_resumen": resumen,
            "mensaje_detallado": detalle,
            "mensaje": resumen,
            "detalle": detalle,
            "solucion": solucion,
            "severidad": insight.severity,
        }

        return self._validar(resultado)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _construir_contexto(
        self, insight: EngineV2Insight, snapshot: IASnapshot
    ) -> Dict[str, float]:
        contexto = {
            "trend_percent": float(snapshot.sales_trend_percent or 0.0) * 100,
            "sales_anomaly_score": float(snapshot.sales_anomaly_score or 0.0),
            "sales_volatility": float(snapshot.sales_volatility or 0.0),
            "movements_per_hour": float(snapshot.movements_per_hour or 0.0),
            "inactivity_hours": float(snapshot.inactivity_hours or 0.0),
            "weight_change_rate": float(snapshot.weight_change_rate or 0.0),
            "weight_volatility": float(snapshot.weight_volatility or 0.0),
            "signal_strength": float(snapshot.signal_strength or 0.0),
            "critical_alerts": int(snapshot.critical_alerts or 0),
            "warning_alerts": int(snapshot.warning_alerts or 0),
            "sales_window_hours": int(snapshot.sales_window_hours or 0),
            "movement_window_hours": int(snapshot.movement_window_hours or 0),
        }
        contexto.update({k: float(v) for k, v in insight.data_points.items()})
        contexto.update({k: float(v) for k, v in insight.extra_context.items()})
        return contexto

    def _construir_mensaje(
        self,
        modulos: List[str],
        contexto: Dict[str, float],
        minimo: int = 1,
        maximo: int | None = None,
    ) -> str:
        if not modulos:
            return ""

        maximo = maximo or min(len(modulos), max(minimo, 2))
        seleccion = self._rng.sample(modulos, k=min(len(modulos), maximo))
        seleccion = seleccion[: max(len(seleccion), minimo)]

        mensajes: List[str] = []
        for modulo in seleccion:
            try:
                mensajes.append(modulo.format(**contexto))
            except Exception as exc:  # pragma: no cover - defensivo
                logger.exception("[IAFormatterV2] Error formateando módulo '%s': %s", modulo, exc)
        return " ".join(fragmento.strip() for fragmento in mensajes if fragmento)

    def _elegir(self, opciones: List[str], fallback: str) -> str:
        if not opciones:
            return fallback
        texto = self._rng.choice(opciones).strip()
        return texto or fallback

    def _validar(self, payload: Dict[str, str]) -> Dict[str, str]:
        campos = {
            "titulo": "Diagnóstico IA",
            "mensaje_resumen": "Sin resumen disponible.",
            "mensaje_detallado": "No se generó detalle adicional.",
            "solucion": "Verificar manualmente el módulo evaluado.",
        }
        for clave, defecto in campos.items():
            if not payload.get(clave):
                payload[clave] = defecto
        payload.setdefault("mensaje", payload["mensaje_resumen"])
        payload.setdefault("detalle", payload["mensaje_detallado"])
        payload.setdefault("severidad", "info")
        return payload


__all__ = ["IAFormatterV2"]
