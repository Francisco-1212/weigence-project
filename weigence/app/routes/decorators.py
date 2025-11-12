"""
Decoradores para control de acceso por roles
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request

def requiere_rol(*roles_permitidos):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados
    
    Uso:
        @requiere_rol('administrador', 'jefe')
        def mi_ruta():
            pass
    """
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar que el usuario está logueado
            if not session.get('usuario_logueado'):
                flash('Por favor inicia sesión', 'error')
                return redirect(url_for('main.login'))
            
            # Obtener rol actual
            rol_usuario = session.get('usuario_rol', '')
            
            # Verificar que el rol está en los permitidos
            if rol_usuario not in roles_permitidos:
                flash(f'Acceso denegado. Se requiere rol: {", ".join(roles_permitidos)}', 'error')
                
                # Si es petición AJAX, devolver JSON
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'Acceso denegado',
                        'rol_requerido': list(roles_permitidos),
                        'rol_usuario': rol_usuario
                    }), 403
                
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorador


def requiere_autenticacion(f):
    """
    Decorador simple que requiere que el usuario esté autenticado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('usuario_logueado'):
            flash('Por favor inicia sesión', 'error')
            
            # Si es petición AJAX, devolver JSON
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'No autenticado'
                }), 401
            
            return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    
    return decorated_function
