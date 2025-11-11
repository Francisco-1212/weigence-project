"""Routes that expose the IA engine."""
from __future__ import annotations

import json

from flask import Response, request

from . import bp
from app.ia import generar_recomendacion_v2


def _response(payload: dict) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False),
        mimetype="application/json; charset=utf-8",
    )


@bp.route("/api/ia/auditoria", methods=["GET"])
def ia_auditoria() -> Response:
    """Return the IA engine recommendation for audit workflows."""

    contexto = (request.args.get("contexto") or "auditoria").lower()
    try:
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
        return _response(fallback)


@bp.route("/api/ia/preview", methods=["GET"])
def ia_preview() -> Response:
    """Developer friendly endpoint returning the same recommendation payload."""

    return ia_auditoria()
