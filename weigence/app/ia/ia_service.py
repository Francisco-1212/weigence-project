"""Public entry point for the IA recommendation engine."""
from __future__ import annotations

import logging
from typing import Dict

from .ia_engine import IAEngine, engine
from .ia_formatter import IAFormatter, formatter
from .ia_logger import AuditLogger, audit_logger
from .ia_snapshots import SnapshotBuilder, snapshot_builder

logger = logging.getLogger(__name__)


class IAService:
    """Coordinates the different layers of the IA engine."""

    def __init__(
        self,
        *,
        engine_: IAEngine | None = None,
        formatter_: IAFormatter | None = None,
        builder: SnapshotBuilder | None = None,
        logger: AuditLogger | None = None,
    ) -> None:
        self._engine = engine_ or engine
        self._formatter = formatter_ or formatter
        self._builder = builder or snapshot_builder
        self._logger = logger or audit_logger

    def generar_recomendacion_auditoria(self, contexto: str | None = None) -> Dict[str, str]:
        """Genera y registra una recomendación IA para el módulo solicitado."""

        snapshot = self._builder.build(contexto=contexto)
        insight = self._engine.evaluate(snapshot)
        resultado = self._formatter.render(insight, snapshot)

        logger.info(
            "[IA] Interpretación completada, resultado: %s",
            resultado.get("titulo", "sin título"),
        )

        metadata = {
            "trend_percent": float(
                insight.data_points.get("trend_percent", snapshot.sales_trend_percent) or 0.0
            ),
            "weight_volatility": float(
                insight.data_points.get("weight_volatility", snapshot.weight_volatility) or 0.0
            ),
            "weight_change": float(
                insight.data_points.get("weight_change", snapshot.weight_change_rate) or 0.0
            ),
            "signal_strength": float(
                insight.data_points.get("signal_strength", snapshot.signal_strength) or 0.0
            ),
            "inventory_pressure": float(
                insight.data_points.get("weight_change", snapshot.weight_change_rate) or 0.0
            ),
        }
        self._logger.registrar_evento(
            tipo=contexto or "auditoria",
            severidad=resultado["severidad"],
            titulo=resultado["titulo"],
            mensaje=resultado["mensaje"],
            solucion=resultado["solucion"],
            metadata=metadata,
            confianza=insight.confidence,
        )
        return resultado


def generar_recomendacion_auditoria(contexto: str | None = None) -> Dict[str, str]:
    """Convenience wrapper that uses the default IA service."""

    service = IAService()
    return service.generar_recomendacion_auditoria(contexto=contexto)


__all__ = ["IAService", "generar_recomendacion_auditoria"]
