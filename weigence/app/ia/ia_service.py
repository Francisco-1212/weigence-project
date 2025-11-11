from __future__ import annotations

import logging
from typing import Any, Dict

from .ia_contexts import IAContextBuilder
from .ia_engine import EngineInsight, IAEngine, engine as default_engine
from .ia_formatter import IAFormatter
from .ia_logger import AuditLogger, audit_logger
from .ia_messages import get_header_message
from .ia_snapshots import IASnapshot, SnapshotBuilder, snapshot_builder

logger = logging.getLogger(__name__)


class IAService:
    """Coordinates the different layers of the IA engine."""

    _PROFILE_MAP = {
        "auditoria": "perfil_operativo",
        "operaciones": "perfil_operativo",
        "comercial": "perfil_comercial",
        "ventas": "perfil_comercial",
        "inventario": "perfil_inventario",
    }
    _VALID_SEVERITIES = {"info", "warning", "critical"}

    def __init__(
        self,
        *,
        engine: IAEngine | None = None,
        formatter: IAFormatter | None = None,
        builder: SnapshotBuilder | None = None,
        logger_: AuditLogger | None = None,
        context_builder: IAContextBuilder | None = None,
        default_profile: str = "perfil_operativo",
    ) -> None:
        self._engine = engine or default_engine
        self._formatter = formatter or IAFormatter(self._engine.templates)
        self._builder = builder or snapshot_builder
        self._logger = logger_ or audit_logger
        self._context_builder = context_builder or IAContextBuilder()
        self._default_profile = default_profile

    def generar_recomendacion(
        self,
        contexto: str | None = None,
        *,
        perfil: str | None = None,
        data: Dict[str, Any] | None = None,
        modo: str = "default",
    ) -> Dict[str, Any]:
        """Genera la recomendación IA para el módulo solicitado."""

        contexto_key = (contexto or "dashboard").strip().lower() or "dashboard"
        perfil_ia = self._resolver_perfil(contexto_key, perfil)

        logger.debug(
            "[IAService] Generando snapshot para contexto=%s perfil=%s", contexto_key, perfil_ia
        )

        base_snapshot = self._builder.build(contexto=contexto_key)
        merged_snapshot = base_snapshot.merge(data)
        context_data = self._context_builder.get_context_data(contexto_key, merged_snapshot)
        final_snapshot = merged_snapshot.merge(context_data)

        insight = self._engine.evaluate(final_snapshot, profile=perfil_ia)
        logger.debug(
            "[IAService] Insight calculado: key=%s severity=%s score=%.3f",
            insight.key,
            insight.severity,
            insight.score,
        )

        resultado = self._formatter.render(insight, final_snapshot)
        resultado.update(
            {
                "score": round(float(insight.score), 3),
                "confianza": round(float(insight.confidence), 3),
                "insight_key": insight.key,
                "contexto": contexto_key,
                "perfil_ia": perfil_ia,
                "timestamp": base_snapshot.generated_at.isoformat(),
            }
        )

        resultado = self._normalizar_payload(resultado)

        if modo == "header":
            header_message = get_header_message(
                contexto_key,
                {
                    "n_alerts": int(final_snapshot.critical_alerts + final_snapshot.warning_alerts),
                    "mensaje": resultado["mensaje"],
                },
            )
            resultado["mensaje"] = header_message
            resultado["mensaje_resumen"] = header_message
            resultado.setdefault("detalle", resultado["mensaje_detallado"])

        metadata = self._construir_metadata(insight, final_snapshot)
        self._logger.registrar_evento(
            tipo=contexto_key,
            severidad=resultado["severidad"],
            titulo=resultado["titulo"],
            mensaje=resultado["mensaje"],
            solucion=resultado["solucion"],
            metadata=metadata,
            confianza=insight.confidence,
        )

        return resultado

    def _resolver_perfil(self, contexto: str, perfil: str | None) -> str:
        if perfil:
            return perfil
        return self._PROFILE_MAP.get(contexto, self._default_profile)

    def _normalizar_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        campos = {
            "titulo": "Diagnóstico operativo",
            "mensaje_resumen": "Sin resumen disponible.",
            "mensaje_detallado": "Detalle no disponible.",
            "mensaje": "Sin mensaje disponible.",
            "detalle": "Detalle no disponible.",
            "solucion": "Revisar manualmente el módulo y ejecutar nuevamente el motor.",
            "severidad": "info",
        }
        datos = dict(payload or {})

        def _texto(clave: str, fallback: str) -> str:
            valor = datos.get(clave)
            if isinstance(valor, str):
                valor = valor.strip()
                return valor or fallback
            if valor is None:
                return fallback
            return str(valor)

        titulo = _texto("titulo", campos["titulo"])
        resumen = _texto("mensaje_resumen", "")
        mensaje = _texto("mensaje", resumen or campos["mensaje"])
        detalle_detallado = _texto("mensaje_detallado", "")
        detalle = _texto("detalle", detalle_detallado or mensaje)
        solucion = _texto("solucion", campos["solucion"])
        severidad = _texto("severidad", campos["severidad"]).lower()
        if severidad not in self._VALID_SEVERITIES:
            severidad = "info"

        datos.update(
            {
                "titulo": titulo,
                "mensaje_resumen": resumen or mensaje or campos["mensaje_resumen"],
                "mensaje": mensaje or campos["mensaje"],
                "mensaje_detallado": detalle_detallado or detalle or campos["mensaje_detallado"],
                "detalle": detalle or mensaje,
                "solucion": solucion,
                "severidad": severidad,
            }
        )

        datos["score"] = float(datos.get("score", 0.0) or 0.0)
        datos["confianza"] = float(datos.get("confianza", 0.0) or 0.0)
        datos.setdefault("insight_key", "stable_outlook")
        return datos

    def _construir_metadata(self, insight: EngineInsight, snapshot: IASnapshot) -> Dict[str, float]:
        metadata: Dict[str, float] = {
            clave: float(valor)
            for clave, valor in insight.data_points.items()
            if isinstance(valor, (int, float))
        }
        metadata.update({
            "score": float(insight.score),
            "confidence": float(insight.confidence),
            "movements_per_hour": float(snapshot.movements_per_hour or 0.0),
            "inactivity_hours": float(snapshot.inactivity_hours or 0.0),
            "signal_strength": float(snapshot.signal_strength or 0.0),
        })
        return metadata


def generar_recomendacion(
    contexto: str | None = None,
    *,
    perfil: str | None = None,
    data: Dict[str, Any] | None = None,
    modo: str = "default",
) -> Dict[str, Any]:
    """Convenience wrapper that uses the default IA service."""

    service = IAService()
    return service.generar_recomendacion(
        contexto=contexto,
        perfil=perfil,
        data=data,
        modo=modo,
    )


__all__ = ["IAService", "generar_recomendacion"]
