"""
Endpoint de debug para verificar el contenido de la sesion.
Accede a: http://localhost:5000/debug-sesion
"""

from flask import Blueprint, jsonify, session, render_template

debug_bp = Blueprint("debug", __name__)


@debug_bp.route("/debug-sesion")
def debug_sesion():
    """Devuelve el contenido actual de la sesion."""
    return jsonify(
        {
            "session_data": {
                "usuario_logueado": session.get("usuario_logueado"),
                "usuario_nombre": session.get("usuario_nombre"),
                "usuario_rol": session.get("usuario_rol"),
                "usuario_id": session.get("usuario_id"),
                "usuario_correo": session.get("usuario_correo"),
                "recordarme_activado": session.get("recordarme_activado"),
            },
            "mensaje": "Si ves todo vacio/None, significa que no hay sesion activa. Inicia sesion primero.",
        }
    )


@debug_bp.route("/debug-sesion-visual")
def debug_sesion_visual():
    """Version visual del debug de sesion."""
    return render_template("pagina/debug_sesion.html")


@debug_bp.route("/debug-usuario")
def debug_usuario():
    """Debug detallado del usuario actual."""
    return render_template("pagina/debug_usuario.html")


# Exportar para usar en app/__init__.py
debug_blueprint = debug_bp
