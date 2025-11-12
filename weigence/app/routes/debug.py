"""
Endpoint de debug para verificar qué hay en la sesión
Accede a: http://localhost:5000/debug-sesion
"""

from flask import Blueprint, jsonify, session

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug-sesion')
def debug_sesion():
    """Devuelve el contenido actual de la sesión"""
    return jsonify({
        "session_data": {
            "usuario_logueado": session.get("usuario_logueado"),
            "usuario_nombre": session.get("usuario_nombre"),
            "usuario_rol": session.get("usuario_rol"),  # ← AQUÍ VER SI EXISTE
            "usuario_id": session.get("usuario_id"),
            "usuario_correo": session.get("usuario_correo"),
            "recordarme_activado": session.get("recordarme_activado"),
        },
        "mensaje": "Si ves todo vacío/None, significa que no hay sesión activa. Inicia sesión primero."
    })

# Exportar para usar en app/__init__.py
debug_blueprint = debug_bp
