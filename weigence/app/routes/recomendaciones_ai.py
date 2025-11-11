"""Rutas para recomendaciones IA y notificaciones."""
import logging
from flask import request
from . import bp
from app.utils.api_response import json_response
from app.ia import generar_recomendacion_v2
from app.ia.ia_messages import get_header_message
from .utils import requiere_login, obtener_notificaciones

# Configurar logger
logger = logging.getLogger(__name__)

@bp.route('/api/recomendacion/<contexto>', methods=['GET', 'POST'])
def api_recomendacion(contexto: str):
    """
    Endpoint para obtener recomendaciones de IA según el contexto.
    
    Args:
        contexto: Página o sección actual (dashboard, inventario, ventas, etc)
    """
    try:
        logger.info("[Recomendación] Generando para contexto: %s", contexto)
        
        # Obtener datos del POST o query params
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
        else:
            data = request.args.to_dict()
        
        # Generar recomendación
        recomendacion = generar_recomendacion_v2(
            contexto=contexto,
            data=data
        )
        
        if not isinstance(recomendacion, dict):
            logger.error("[Recomendación] Respuesta inválida: %s", type(recomendacion))
            return json_response(
                "Error al generar recomendación",
                ok=False,
                status_code=500
            )
            
        logger.info("[Recomendación] Generada exitosamente para %s", contexto)
        
        # Asegurarse de que estén todos los campos requeridos por el frontend
        campos_requeridos = {
            "mensaje": recomendacion.get("mensaje", ""),
            "mensaje_detallado": recomendacion.get("detalle", ""),
            "titulo": recomendacion.get("titulo", ""),
            "solucion": recomendacion.get("solucion", ""),
            "severidad": recomendacion.get("severidad", "info"),
            "score": float(recomendacion.get("score", 0)),
            "confianza": float(recomendacion.get("confianza", 0)),
            "insight_key": recomendacion.get("insight_key", ""),
            "ok": True
        }
        
        return json_response(
            mensaje=campos_requeridos["mensaje"],
            ok=True,
            **campos_requeridos
        )
        
    except Exception as e:
        logger.error("[Recomendación] Error: %s", str(e), exc_info=True)
        return json_response(
            f"Error al generar recomendación: {str(e)}",
            ok=False,
            error=str(e),
            status_code=500
        )

@bp.route('/api/recomendacion/header')
def api_recomendacion_header():
    """Endpoint para obtener recomendaciones breves para el header."""
    try:
        # Obtener página actual
        page = request.args.get('page', 'dashboard')
        logger.info("[Header] Generando recomendación para página: %s", page)
        
        # Obtener datos de contexto
        data = request.get_json() if request.is_json else {}
        
        # Obtener mensaje apropiado
        mensaje = get_header_message(page, data)
        
        logger.info("[Header] Mensaje generado exitosamente")
        return json_response(mensaje)
        
    except Exception as e:
        logger.error("[Header] Error: %s", str(e), exc_info=True)
        return json_response(
            "No hay recomendaciones disponibles",
            ok=False,
            status_code=500
        )

@bp.route('/api/notificaciones')
def api_notificaciones():
    """Endpoint para obtener notificaciones activas."""
    try:
        logger.info("[Notificaciones] Recuperando notificaciones activas")
        
        # Obtener notificaciones usando la función existente
        alertas, grupos = obtener_notificaciones()
        
        return json_response(
            "Notificaciones recuperadas",
            ok=True,
            notificaciones=alertas,
            grupos=grupos
        )
        
    except Exception as e:
        logger.error("[Notificaciones] Error: %s", str(e), exc_info=True)
        return json_response(
            "No se pudieron recuperar las notificaciones",
            ok=False,
            status_code=500
        )