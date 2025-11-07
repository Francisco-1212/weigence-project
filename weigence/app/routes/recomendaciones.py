"""Routes that expose the IA engine."""
from __future__ import annotations

import json
from typing import List

from flask import Response, request

from . import bp
from app.ia import Recommendation, ia_service
from app.ia_logger import registrar_ia


def _serialize(recomendaciones: List[Recommendation]) -> str:
    """Serialize recommendations ensuring UTF-8 compatibility."""

    payload = []
    for rec in recomendaciones:
        item = {
            "mensaje": rec.mensaje,
            "nivel": rec.nivel,
        }
        if rec.categoria:
            item["categoria"] = rec.categoria
        payload.append(item)
    return json.dumps(payload, ensure_ascii=False)


@bp.route("/api/ia/header", methods=["GET"])
def ia_header() -> Response:
    """Return global recommendations for the header component."""

    try:
        contexto = request.args.get("contexto")
        recomendaciones = ia_service.build_header_recommendations(contexto)
        return Response(
            _serialize(recomendaciones),
            mimetype="application/json; charset=utf-8",
        )
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("[ia_header]", exc)
        return Response(
            json.dumps(
                [
                    {
                        "mensaje": "Diagnóstico no disponible en este momento.",
                        "nivel": "advertencia",
                    }
                ],
                ensure_ascii=False,
            ),
            mimetype="application/json; charset=utf-8",
        )


@bp.route("/api/recomendaciones", methods=["GET"])
def ia_contextual() -> Response:
    """Return contextualised recommendations for a specific module."""

    contexto = (request.args.get("contexto") or "general").lower()
    try:
        recomendaciones = ia_service.build_contextual_recommendations(contexto)
        return Response(
            _serialize(recomendaciones),
            mimetype="application/json; charset=utf-8",
        )
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("[ia_contextual]", exc)
        return Response(
            json.dumps(
                [
                    {
                        "mensaje": "Recomendaciones no disponibles para este módulo.",
                        "nivel": "advertencia",
                    }
                ],
                ensure_ascii=False,
            ),
            mimetype="application/json; charset=utf-8",
        )


@bp.route("/api/ia/auditoria", methods=["GET"])
def ia_auditoria() -> Response:
    """Return the interpretative audit analysis and register a snapshot."""

    try:
        if not registrar_ia("auditoria"):
            raise RuntimeError("No se pudo registrar la métrica de auditoría")
        recomendaciones = ia_service.interpretar_auditoria()
        return Response(
            _serialize(recomendaciones),
            mimetype="application/json; charset=utf-8",
        )
    except Exception as exc:  # pragma: no cover - diagnostic output
        print("[ia_auditoria]", exc)
        return Response(
            json.dumps(
                [
                    {
                        "mensaje": "Error al generar recomendaciones automáticas.",
                        "nivel": "critico",
                    }
                ],
                ensure_ascii=False,
            ),
            mimetype="application/json; charset=utf-8",
        )
