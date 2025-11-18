from __future__ import annotations

import logging
from typing import Any, Dict

from .ia_contexts import IAContextBuilder
from .ia_engine import EngineInsight, IAEngine, engine as default_engine
from .ia_formatter import IAFormatter
from .ia_logger import AuditLogger, audit_logger
from .ia_messages import get_header_message
from .ia_snapshots import IASnapshot, SnapshotBuilder, snapshot_builder
from .ia_ml_anomalies import detect_anomalies

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

        # 🤖 DETECCIÓN DE ANOMALÍAS CON ML
        ml_insights = detect_anomalies(final_snapshot)
        logger.debug(
            "[IAService] ML Anomaly Detection: is_anomaly=%s, score=%.3f, severity=%s",
            ml_insights.get('is_anomaly'),
            ml_insights.get('anomaly_score'),
            ml_insights.get('severity')
        )

        insight = self._engine.evaluate(final_snapshot, profile=perfil_ia)
        logger.debug(
            "[IAService] Insight calculado: key=%s severity=%s score=%.3f",
            insight.key,
            insight.severity,
            insight.score,
        )

        resultado = self._formatter.render(insight, final_snapshot)
        
        # 🔥 ENRIQUECER CON INSIGHTS DE ML
        resultado = self._enriquecer_con_ml(resultado, ml_insights, final_snapshot)
        
        # Generar resumen amigable de la situación
        resumen_situacion = self._generar_resumen_situacion(final_snapshot)
        insights_cards = self._generar_insights_cards(final_snapshot, ml_insights)
        
        resultado.update(
            {
                "score": round(float(insight.score), 3),
                "confianza": round(float(insight.confidence), 3),
                "insight_key": insight.key,
                "contexto": contexto_key,
                "perfil_ia": perfil_ia,
                "timestamp": base_snapshot.generated_at.isoformat(),
                # Añadir insights de ML
                "ml_anomaly_detected": ml_insights.get('is_anomaly', False),
                "ml_anomaly_score": round(ml_insights.get('anomaly_score', 0.0), 3),
                "ml_severity": ml_insights.get('severity', 'low'),
                "situacion_actual": resumen_situacion,
                "ml_insights_cards": insights_cards,
            }
        )

        resultado = self._normalizar_payload(resultado)

        # 💬 Sobrescribir con mensaje simple si hay anomalía ML
        if ml_insights.get('is_anomaly'):
            resultado["mensaje_resumen"] = resumen_situacion
            resultado["mensaje"] = resumen_situacion

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

    def _generar_resumen_situacion(self, snapshot: "IASnapshot") -> str:
        """Genera un resumen conversacional de la situación actual."""
        partes = []
        
        # Alertas
        if snapshot.critical_alerts > 0:
            partes.append(f"{snapshot.critical_alerts} alertas críticas")
        if snapshot.warning_alerts > 0:
            partes.append(f"{snapshot.warning_alerts} advertencias")
        
        # Ventas
        if abs(snapshot.sales_trend_percent) > 5:
            direccion = "subieron" if snapshot.sales_trend_percent > 0 else "bajaron"
            partes.append(f"ventas {direccion} {abs(snapshot.sales_trend_percent):.0f}%")
        
        # Actividad
        if snapshot.inactivity_hours > 2:
            partes.append(f"{snapshot.inactivity_hours:.0f}h sin movimientos")
        elif snapshot.movements_per_hour < 0.5:
            partes.append("poca actividad")
        
        if not partes:
            return "Operación funcionando normalmente."
        
        return "Detecté " + ", ".join(partes) + "."
    
    def _generar_insights_cards(self, snapshot: "IASnapshot", ml_insights: Dict[str, Any]) -> list:
        """Genera tarjetas individuales de insights para el carrusel."""
        
        # 🎯 Si ML generó hallazgos, usarlos directamente
        ml_findings = ml_insights.get('findings', [])
        if ml_findings:
            cards = []
            for finding in ml_findings:
                cards.append({
                    "tipo": "ml_finding",
                    "icono": finding.get('emoji', '🔍'),
                    "titulo": finding.get('title', 'Hallazgo detectado'),
                    "descripcion": finding.get('description', 'El sistema identificó un patrón.'),
                    "accion": None  # Por ahora sin acciones específicas
                })
            return cards
        
        # 🔄 Fallback: lógica anterior si ML no generó hallazgos
        cards = []
        
        # Card 1: Alertas si hay críticas
        if snapshot.critical_alerts >= 3:
            cards.append({
                "tipo": "alertas",
                "icono": "🚨",
                "titulo": f"{snapshot.critical_alerts} alertas rojas activas",
                "descripcion": f"Tienes {snapshot.critical_alerts} alertas críticas que necesitan atención. Revisa la sección de alertas.",
                "accion": None
            })
        
        # Card 2: Ventas si hay caída significativa
        if snapshot.sales_trend_percent < -30:
            cards.append({
                "tipo": "ventas",
                "icono": "📉",
                "titulo": f"Ventas cayeron {abs(snapshot.sales_trend_percent):.0f}%",
                "descripcion": f"Las ventas están {abs(snapshot.sales_trend_percent):.0f}% más bajas que ayer. Puede ser falta de stock o problema técnico.",
                "accion": None
            })
        
        # Card 3: Inactividad si es prolongada
        if snapshot.inactivity_hours >= 3:
            cards.append({
                "tipo": "inactividad",
                "icono": "⏱️",
                "titulo": f"{snapshot.inactivity_hours:.0f}h sin movimientos",
                "descripcion": f"Llevan {snapshot.inactivity_hours:.0f} horas sin registrar movimientos. Verifica sensores y conectividad.",
                "accion": None
            })
        
        # Si no hay nada especial, agregar card positiva
        if not cards:
            cards.append({
                "tipo": "normal",
                "icono": "✅",
                "titulo": "Todo funciona normal",
                "descripcion": "No se detectaron problemas. La operación está dentro de lo esperado.",
                "accion": None
            })
        
        return cards
    
    def _enriquecer_con_ml(
        self,
        resultado: Dict[str, Any],
        ml_insights: Dict[str, Any],
        snapshot: "IASnapshot",
    ) -> Dict[str, Any]:
        """
        Enriquece la recomendación con insights de ML.
        Si ML detecta anomalía severa, puede elevar la severidad.
        """
        if not ml_insights.get('is_anomaly'):
            return resultado
        
        ml_severity = ml_insights.get('severity', 'low')
        ml_actions = ml_insights.get('recommended_actions', [])
        
        # Si ML detecta anomalía HIGH y el motor dice INFO, elevar a WARNING
        if ml_severity == 'high' and resultado.get('severidad') == 'info':
            resultado['severidad'] = 'warning'
            logger.info("[ML] Elevando severidad de info → warning por anomalía ML detectada")
        
        # Añadir acciones de ML a la solución
        if ml_actions:
            solucion_actual = resultado.get('solucion', '')
            ml_actions_text = "\n\n🤖 Insights ML adicionales:\n" + "\n".join(f"• {action}" for action in ml_actions[:2])
            resultado['solucion'] = solucion_actual + ml_actions_text
        
        # Añadir badge de ML al título si anomalía es severa
        if ml_severity in ['medium', 'high']:
            titulo_actual = resultado.get('titulo', '')
            if '🤖' not in titulo_actual:
                resultado['titulo'] = f"🤖 {titulo_actual}"
        
        return resultado

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
