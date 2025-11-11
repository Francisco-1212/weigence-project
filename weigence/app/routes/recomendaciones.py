import json
from typing import Any, Dict

from flask import Response, current_app, jsonify, request

from . import bp
from app.ia import generar_recomendacion


def _build_success_payload(recomendacion: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ok": True,
        "mensaje": recomendacion.get("mensaje", "Recomendación generada."),
        "data": recomendacion,
    }


@bp.route("/api/ia/auditoria", methods=["GET"])
def ia_auditoria() -> Response:
    """Return the IA engine recommendation for audit workflows."""

    contexto = (request.args.get("contexto") or "auditoria").strip().lower() or "auditoria"
    raw_data = request.args.get("data")
    extra_data: Dict[str, Any] = {}
    if raw_data:
        try:
            extra_data = json.loads(raw_data)
        except json.JSONDecodeError:
            current_app.logger.warning("[ia_auditoria] payload 'data' inválido", exc_info=False)

    try:
        recomendacion = generar_recomendacion(
            contexto=contexto,
            data=extra_data,
            modo="auditoria",
        )
        return jsonify(_build_success_payload(recomendacion))
    except Exception as exc:  # pragma: no cover - defensive logging
        current_app.logger.exception(
            "[ia_auditoria] Error al obtener recomendación IA",
            extra={"contexto": contexto},
        )
        error_payload = {
            "message": "No fue posible calcular una recomendación automática en este momento.",
            "context": contexto,
            "code": "ia_unavailable",
            "detail": str(exc),
        }
        return jsonify({"ok": False, "error": error_payload}), 503


@bp.route("/api/ia/preview", methods=["GET"])
def ia_preview() -> Response:
    """Developer friendly endpoint returning the same recommendation payload."""

    return ia_auditoria()
