from flask import Blueprint

# Blueprint normal; no cambies el nombre ni lo borres
bp = Blueprint("main", __name__, url_prefix="")

# importa todas tus rutas aquí
from . import login, dashboard, inventario, ventas, movimientos, alertas, api_status, auditoria

