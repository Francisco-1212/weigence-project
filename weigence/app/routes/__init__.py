from flask import Blueprint

bp = Blueprint("main", __name__)

from . import (
    login,
    dashboard,
    inventario,
    ventas,
    movimientos,
    alertas,
    api_status,
    auditoria,
    historial,
    perfil,
    recomendaciones_ai,
    usuarios,
    chat_ui,
    test_routes
)
