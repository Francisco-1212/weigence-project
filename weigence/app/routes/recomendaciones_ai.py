"""Rutas para recomendaciones IA y notificaciones (versión corregida)."""
import logging
from typing import Any, Dict
from flask import jsonify, request
from . import bp
from .utils import obtener_notificaciones

from app.ia.ia_service import generar_recomendacion



logger = logging.getLogger(__name__)


def _parse_payload(source: Dict[str, Any] | None) -> Dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    return {k: v for k, v in source.items() if v is not None}


def _success_response(recomendacion: Dict[str, Any]) -> tuple:
    payload = {
        "ok": True,
        "mensaje": recomendacion.get("mensaje", "Recomendación generada."),
        "data": recomendacion,
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
    """Devuelve un mensaje IA breve para el header según la página."""
    try:
        import inspect, sys

        page = request.args.get('page', 'dashboard')
        body_data = request.get_json(silent=True)
        data = _parse_payload(body_data if isinstance(body_data, dict) else {})

        recomendacion = generar_recomendacion(contexto=page, data=data, modo="header")
        return _success_response(recomendacion)

    except Exception as exc:
        print("[DEBUG] Error:", exc)
        return _error_response("Error durante depuración", detail=str(exc))

        return _success_response(recomendacion)



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
