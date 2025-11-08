"""Service orchestrating the IA Engine v2 pipeline."""
from __future__ import annotations

import logging
from typing import Dict

from .ia_engine_v2 import EngineV2Insight, IAEngineV2
from .ia_formatter_v2 import IAFormatterV2
from .ia_logger import AuditLogger, audit_logger
from .ia_snapshots import SnapshotBuilder, snapshot_builder

logger = logging.getLogger(__name__)


class IAServiceV2:
    """Coordinates the modular engine, formatter and logging stack."""

    _PROFILE_MAP = {
        "auditoria": "perfil_operativo",
        "operaciones": "perfil_operativo",
        "comercial": "perfil_comercial",
        "ventas": "perfil_comercial",
        "inventario": "perfil_inventario",
    }

    def __init__(
        self,
        *,
        engine: IAEngineV2 | None = None,
        formatter: IAFormatterV2 | None = None,
        builder: SnapshotBuilder | None = None,
        logger_: AuditLogger | None = None,
        default_profile: str = "perfil_operativo",
    ) -> None:
        self._engine = engine or IAEngineV2()
        self._formatter = formatter or IAFormatterV2(self._engine.templates)
        self._builder = builder or snapshot_builder
        self._logger = logger_ or audit_logger
        self._default_profile = default_profile

    def generar_recomendacion_auditoria(
        self, contexto: str | None = None, perfil: str | None = None
    ) -> Dict[str, str]:
        """Produce la recomendación IA v2 garantizando el contrato del endpoint."""

        perfil_ia = self._resolver_perfil(contexto, perfil)
        logger.debug(
            "[IAServiceV2] Generando snapshot para contexto=%s perfil=%s",
            contexto,
            perfil_ia,
        )

        snapshot = self._builder.build(contexto=contexto)
        insight = self._engine.evaluate(snapshot, profile=perfil_ia)
        logger.debug(
            "[IAServiceV2] Insight v2 calculado key=%s severity=%s score=%.3f",
            insight.key,
            insight.severity,
            insight.score,
        )

        resultado = self._formatter.render(insight, snapshot)
        resultado.setdefault("mensaje", resultado.get("mensaje_resumen", ""))
        resultado.setdefault("detalle", resultado.get("mensaje_detallado", ""))
        resultado.setdefault("perfil_ia", perfil_ia)
        resultado.setdefault("score", f"{insight.score:.3f}")
        resultado.setdefault("confianza", f"{insight.confidence:.2f}")
        resultado.setdefault("insight_key", insight.key)

        metadata = self._construir_metadata(insight)
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

    def _resolver_perfil(self, contexto: str | None, perfil: str | None) -> str:
        if perfil:
            return perfil
        if not contexto:
            return self._default_profile
        return self._PROFILE_MAP.get(contexto.lower(), self._default_profile)

    def _construir_metadata(self, insight: EngineV2Insight) -> Dict[str, float]:
        metadata: Dict[str, float] = {
            clave: float(valor)
            for clave, valor in insight.data_points.items()
            if isinstance(valor, (int, float))
        }
        metadata.update({
            "score": float(insight.score),
            "confidence": float(insight.confidence),
        })
        return metadata


def generar_recomendacion_auditoria_v2(
    contexto: str | None = None, *, perfil: str | None = None
) -> Dict[str, str]:
    servicio = IAServiceV2()
    return servicio.generar_recomendacion_auditoria(contexto=contexto, perfil=perfil)


__all__ = ["IAServiceV2", "generar_recomendacion_auditoria_v2"]
