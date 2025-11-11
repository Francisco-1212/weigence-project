"""Rutas para recomendaciones IA y notificaciones."""
import logging
from typing import Any, Dict

from flask import jsonify, request

from . import bp
from app.ia import generar_recomendacion
from .utils import obtener_notificaciones

# Configurar logger
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
        "error": {
            "message": message,
            "detail": detail,
        },
    }
    return jsonify(payload), status


@bp.route('/api/recomendacion/<contexto>', methods=['GET', 'POST'])
def api_recomendacion(contexto: str):
    """Endpoint para obtener recomendaciones de IA según el contexto."""

    try:
        logger.info("[Recomendación] Generando para contexto: %s", contexto)

        if request.method == 'POST':
            data = _parse_payload(request.get_json(silent=True))
        else:
            data = _parse_payload(request.args.to_dict())

        recomendacion = generar_recomendacion(contexto=contexto, data=data)
        return _success_response(recomendacion)

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("[Recomendación] Error: %s", str(exc))
        return _error_response("Error al generar recomendación", detail=str(exc))


@bp.route('/api/recomendacion/header')
def api_recomendacion_header():
    """Endpoint para obtener recomendaciones breves para el header."""

    try:
        page = request.args.get('page', 'dashboard')
        body_data = request.get_json(silent=True)
        data = _parse_payload(body_data if isinstance(body_data, dict) else {})

        recomendacion = generar_recomendacion(contexto=page, data=data, modo="header")
        return _success_response(recomendacion)

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("[Header] Error: %s", str(exc))
        return _error_response("No hay recomendaciones disponibles", detail=str(exc))


@bp.route('/api/notificaciones')
def api_notificaciones():
    """Endpoint para obtener notificaciones activas."""

    try:
        logger.info("[Notificaciones] Recuperando notificaciones activas")
        alertas, grupos = obtener_notificaciones()
        return jsonify({
            "ok": True,
            "mensaje": "Notificaciones recuperadas",
            "notificaciones": alertas,
            "grupos": grupos,
        })

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("[Notificaciones] Error: %s", str(exc))
        return _error_response("No se pudieron recuperar las notificaciones", detail=str(exc))
