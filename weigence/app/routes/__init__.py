from flask import Blueprint

# Blueprint principal
bp = Blueprint("main", __name__, url_prefix="")

# importa todas tus rutas aquí
from . import (
    login, dashboard, inventario, ventas, movimientos, alertas, 
    api_status, auditoria, historial, perfil,
    recomendaciones_ai, usuarios
)
