"""Utilidades para respuestas JSON consistentes."""
from typing import Any, Dict, Optional
from flask import jsonify

class APIResponse:
    """Clase para generar respuestas JSON consistentes."""
    
    @staticmethod
    def success(mensaje: str, **extra: Any) -> Dict:
        """Genera una respuesta exitosa."""
        response = {
            "ok": True,
            "mensaje": mensaje
        }
        response.update(extra)
        return response

    @staticmethod
    def error(mensaje: str = "No fue posible generar la recomendación.", **extra: Any) -> Dict:
        """Genera una respuesta de error."""
        response = {
            "ok": False,
            "mensaje": mensaje
        }
        response.update(extra)
        return response

def json_response(
    mensaje: str,
    ok: bool = True,
    status_code: int = 200,
    **extra: Any
) -> tuple:
    """Wrapper para respuestas JSON con código de estado."""
    if ok:
        return jsonify(APIResponse.success(mensaje, **extra)), status_code
    return jsonify(APIResponse.error(mensaje, **extra)), status_code