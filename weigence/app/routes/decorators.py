
from functools import wraps

from flask import jsonify, redirect, request, session, url_for, make_response

from app.config.roles_permisos import ROLES_DISPONIBLES, usuario_puede_realizar_accion


def requiere_rol(*roles_permitidos):
    """
    Requiere que el usuario tenga uno de los roles especificados.
    Incluye validación de sesión robusta y headers anti-caché.
    """
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Validar sesión activa
            if not session.get("usuario_logueado"):
                session.clear()  # Limpiar sesión inválida
                print(f"[DECORADOR] Usuario no autenticado intentando acceder a {request.path}")
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": "No autenticado", "code": 401}), 401
                return redirect(url_for("main.login"))

            # Validar datos esenciales de sesión
            if not session.get('usuario_id') or not session.get('usuario_nombre'):
                session.clear()
                print(f"[DECORADOR] Sesión incompleta - redirigiendo al login")
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": "Sesión inválida", "code": 401}), 401
                return redirect(url_for("main.login"))

            rol_usuario = session.get("usuario_rol", "").lower()
            usuario_id = session.get("usuario_id", "desconocido")

            if rol_usuario not in ROLES_DISPONIBLES:
                print(f"[DECORADOR] Rol desconocido '{rol_usuario}' para usuario {usuario_id}")
                return redirect(url_for("main.dashboard"))

            if rol_usuario not in roles_permitidos:
                print(f"[DECORADOR] Usuario {usuario_id} ({rol_usuario}) rechazado. Requerido: {roles_permitidos}")
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({
                        "success": False,
                        "error": "Acceso denegado",
                        "code": 403,
                        "rol_requerido": list(roles_permitidos),
                        "rol_usuario": rol_usuario,
                    }), 403
                return redirect(url_for("main.dashboard"))

            print(f"[DECORADOR] Acceso concedido a {usuario_id} ({rol_usuario}) en {request.path}")
            
            # Ejecutar función protegida
            response = make_response(f(*args, **kwargs))
            
            # Agregar headers anti-caché para páginas HTML
            if not (request.is_json or request.path.startswith("/api/")):
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            
            return response

        return decorated_function

    return decorador


def requiere_autenticacion(f):
    """Requiere usuario autenticado (sin restricciones de rol)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("usuario_logueado"):
            print("[DECORADOR-AUTH] Usuario no autenticado")
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "No autenticado", "code": 401}), 401
            return redirect(url_for("main.login"))

        usuario_id = session.get("usuario_id", "desconocido")
        print(f"[DECORADOR-AUTH] Usuario autenticado: {usuario_id}")
        return f(*args, **kwargs)

    return decorated_function


def puede_realizar_accion(seccion, accion):
    """Verifica si el usuario puede realizar una accion especifica en una seccion."""
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get("usuario_logueado"):
                return redirect(url_for("main.login"))

            rol_usuario = session.get("usuario_rol", "").lower()
            usuario_id = session.get("usuario_id", "desconocido")

            if not usuario_puede_realizar_accion(rol_usuario, seccion, accion):
                print(f"[DECORADOR-ACCION] {usuario_id} ({rol_usuario}) no puede {accion} en {seccion}")
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": f"No tiene permisos para {accion}", "code": 403}), 403
                return redirect(url_for("main.dashboard"))

            print(f"[DECORADOR-ACCION] {usuario_id} puede {accion} en {seccion}")
            return f(*args, **kwargs)

        return decorated_function

    return decorador
