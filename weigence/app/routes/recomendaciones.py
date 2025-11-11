"""Routes that expose the IA engine."""
from __future__ import annotations

import json
from typing import Any, Mapping

from flask import Response, current_app, request

from . import bp
from app.ia import generar_recomendacion_v2

_DEFAULT_PAYLOAD = {
    "titulo": "Diagnóstico operativo",
    "mensaje": "Sin mensaje disponible.",
    "detalle": "Detalle no disponible.",
    "solucion": "Revisar manualmente el módulo y ejecutar nuevamente el motor.",
    "severidad": "info",
    "mensaje_resumen": "Sin resumen disponible.",
    "mensaje_detallado": "Detalle no disponible.",
}

_VALID_SEVERITIES = {"info", "warning", "critical"}


def _response(payload: dict, *, status: int = 200) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8",
    )


def _coerce_text(value: Any, fallback: str) -> str:
    if isinstance(value, str):
        value = value.strip()
        return value or fallback
    if value is None:
        return fallback
    return str(value)


def _normalizar_payload(data: Mapping[str, Any] | None) -> dict:
    if not isinstance(data, Mapping):
        raise ValueError("El motor IA devolvió un formato inválido.")

    resultado = {**_DEFAULT_PAYLOAD, **dict(data)}

    titulo = _coerce_text(resultado.get("titulo"), _DEFAULT_PAYLOAD["titulo"])
    mensaje_resumen = _coerce_text(
        resultado.get("mensaje_resumen"), resultado.get("mensaje", _DEFAULT_PAYLOAD["mensaje"])
    )
    mensaje = _coerce_text(resultado.get("mensaje"), mensaje_resumen)
    detalle = _coerce_text(
        resultado.get("detalle"),
        _coerce_text(resultado.get("mensaje_detallado"), mensaje),
    )
    solucion = _coerce_text(resultado.get("solucion"), _DEFAULT_PAYLOAD["solucion"])
    severidad = _coerce_text(resultado.get("severidad"), _DEFAULT_PAYLOAD["severidad"]).lower()
    if severidad not in _VALID_SEVERITIES:
        severidad = "info"

    resultado.update(
        {
            "titulo": titulo,
            "mensaje": mensaje,
            "detalle": detalle,
            "solucion": solucion,
            "severidad": severidad,
            "mensaje_resumen": mensaje_resumen or mensaje,
            "mensaje_detallado": _coerce_text(
                resultado.get("mensaje_detallado"), detalle or mensaje
            ),
        }
    )
    return resultado


def _sanitizar_contexto(raw_context: str | None) -> str:
    contexto = (raw_context or "auditoria").strip().lower()
    return contexto or "auditoria"


@bp.route("/api/ia/auditoria", methods=["GET"])
def ia_auditoria() -> Response:
    """Return the IA engine recommendation for audit workflows."""

    contexto = _sanitizar_contexto(request.args.get("contexto"))
    try:
# <<<<<<< HEAD
        # Obtener datos adicionales del request
        data = json.loads(request.args.get('data', '{}')) if request.args.get('data') else None
        
        recomendacion = generar_recomendacion_v2(
            contexto=contexto,
            data=data
        )
        return _response(recomendacion)
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("[ia_auditoria]", exc)
        fallback = {        
            "titulo": "Diagnóstico no disponible",
            "mensaje": "No fue posible calcular una recomendación automática en este momento.",
            "solucion": "Reintentar en unos minutos y validar manualmente los sensores críticos.",
            "severidad": "warning",
        }
        recomendacion = generar_recomendacion_auditoria(contexto=contexto) 
        payload = _normalizar_payload(recomendacion)
    except Exception as exc:  # pragma: no cover - defensive logging
        current_app.logger.exception(
            "[ia_auditoria] Error al obtener recomendación IA", extra={"contexto": contexto}
        )
        error_payload = {
            "message": "No fue posible calcular una recomendación automática en este momento.",
            "context": contexto,
            "code": "ia_unavailable",
            "detail": str(exc),
        }
        return _response({"ok": False, "error": error_payload}, status=503)

    return _response({"ok": True, "data": payload})


@bp.route("/api/ia/preview", methods=["GET"])
def ia_preview() -> Response:
    """Developer friendly endpoint returning the same recommendation payload."""

    return ia_auditoria()
