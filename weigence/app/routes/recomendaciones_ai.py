"""Rutas para recomendaciones IA y notificaciones (versión corregida)."""
import logging
from typing import Any, Dict
from flask import jsonify, request, render_template
from . import bp
from .utils import obtener_notificaciones
from .decorators import requiere_rol

from app.ia.ia_service import generar_recomendacion



logger = logging.getLogger(__name__)


def _parse_payload(source: Dict[str, Any] | None) -> Dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    return {k: v for k, v in source.items() if v is not None}


def _convert_to_json_serializable(obj):
    """Convierte tipos no serializables (numpy, pandas) a tipos nativos de Python."""
    # Importar solo si están disponibles
    try:
        import numpy as np
        has_numpy = True
    except ImportError:
        has_numpy = False
    
    try:
        import pandas as pd
        has_pandas = True
    except ImportError:
        has_pandas = False
    
    if isinstance(obj, dict):
        return {k: _convert_to_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_json_serializable(item) for item in obj]
    elif has_numpy:
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, (np.bool_, np.bool)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
    
    if has_pandas and pd.isna(obj):
        return None
    
    return obj


def _success_response(recomendacion: Dict[str, Any]) -> tuple:
    # Convertir valores no serializables antes de jsonify
    recomendacion_limpia = _convert_to_json_serializable(recomendacion)
    payload = {
        "ok": True,
        "mensaje": recomendacion_limpia.get("mensaje", "Recomendación generada."),
        "data": recomendacion_limpia,
    }
    return jsonify(payload), 200


def _error_response(message: str, *, status: int = 500, detail: str | None = None) -> tuple:
    payload = {
        "ok": False,
        "error": {"message": message, "detail": detail},
    }
    return jsonify(payload), status


# ============================================================
# === ENDPOINT PRINCIPAL DE RECOMENDACIONES CONTEXTUALES ===
# ============================================================

@bp.route('/api/recomendacion/<contexto>', methods=['GET', 'POST'])
@requiere_rol('supervisor', 'administrador')
def api_recomendacion(contexto: str):
    """Endpoint general para obtener recomendaciones IA según el contexto."""
    try:
        logger.info("[Recomendación] Solicitada para contexto: %s", contexto)

        if request.method == 'POST':
            data = _parse_payload(request.get_json(silent=True))
        else:
            data = _parse_payload(request.args.to_dict())

        # Detecta si es modo auditoría
        modo = "auditoria" if contexto.strip().lower() == "auditoria" else "default"

        recomendacion = generar_recomendacion(contexto=contexto, data=data, modo=modo)
        return _success_response(recomendacion)

    except Exception as exc:
        logger.exception("[Recomendación] Error: %s", str(exc))
        return _error_response("Error al generar recomendación", detail=str(exc))


# ============================================================
# === ENDPOINT HEADER IA (MENSAJE CORTO) ===
# ============================================================

@bp.route('/api/recomendacion/header')
def api_recomendacion_header():
    """Devuelve un array de mensajes IA para el header según la página."""
    try:
        import inspect, sys

        page = request.args.get('page', 'dashboard')
        print(f"[HEADER API] 🔄 Generando recomendación para página: {page}")
        body_data = request.get_json(silent=True)
        data = _parse_payload(body_data if isinstance(body_data, dict) else {})

        recomendaciones = generar_recomendacion(contexto=page, data=data, modo="header")
        print(f"[HEADER API] ✅ Recomendación generada para {page}")
        
        # Si es un array (nuevo formato), devolverlo directamente
        if isinstance(recomendaciones, list):
            recomendaciones_limpias = _convert_to_json_serializable(recomendaciones)
            return jsonify({
                "ok": True,
                "data": {"mensajes": recomendaciones_limpias},
                "mensaje": f"{len(recomendaciones_limpias)} mensajes disponibles"
            })
        
        # Si es un objeto (compatibilidad con formato antiguo), convertir a array
        recomendacion_limpia = _convert_to_json_serializable(recomendaciones)
        # Convertir objeto a formato de mensajes
        mensaje_obj = {
            "mensaje": recomendacion_limpia.get("mensaje", "Sin recomendaciones"),
            "severidad": recomendacion_limpia.get("severidad", "info"),
            "detalle": recomendacion_limpia.get("detalle", "")
        }
        return jsonify({
            "ok": True,
            "data": {"mensajes": [mensaje_obj]},
            "mensaje": "1 mensaje disponible"
        })

    except Exception as exc:
        print("[DEBUG] Error en api_recomendacion_header:", exc)
        import traceback
        traceback.print_exc()
        return _error_response("Error al generar recomendaciones", detail=str(exc))



# ============================================================
# === ENDPOINT NOTIFICACIONES ===
# ============================================================

@bp.route('/api/notificaciones')
def api_notificaciones():
    """Devuelve notificaciones activas del sistema."""
    try:
        logger.info("[Notificaciones] Recuperando notificaciones activas")
        alertas, grupos = obtener_notificaciones()
        return jsonify({
            "ok": True,
            "mensaje": "Notificaciones recuperadas",
            "notificaciones": alertas,
            "grupos": grupos,
        })
    except Exception as exc:
        logger.exception("[Notificaciones] Error: %s", str(exc))
        return _error_response("No se pudieron recuperar las notificaciones", detail=str(exc))


# ============================================================
# === PÁGINA DE RECOMENDACIONES (GET) ===
# ============================================================
@bp.route('/recomendaciones', methods=['GET'])
@requiere_rol('supervisor', 'administrador')
def recomendaciones():
    """Página con interfaz de recomendaciones IA"""
    from flask import session
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'recomendaciones':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó a Recomendaciones IA")
        session['last_page'] = 'recomendaciones'
    return render_template('pagina/recomendaciones.html')
