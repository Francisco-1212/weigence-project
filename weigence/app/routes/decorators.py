"""
Decoradores para control de acceso por roles
Utiliza la configuración centralizada de app/config/roles_permisos.py
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from app.config.roles_permisos import (
    obtener_permisos_rol,
    usuario_puede_realizar_accion,
    ROLES_DISPONIBLES
)

def requiere_rol(*roles_permitidos):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados
    
    Uso:
        @requiere_rol('administrador', 'jefe')
        def mi_ruta():
            pass
            
    Args:
        *roles_permitidos: Roles que tienen permiso de acceso
    """
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # ========== VERIFICACIÓN 1: ¿Usuario está logueado? ==========
            if not session.get('usuario_logueado'):
                print(f"[DECORADOR] ❌ Usuario no autenticado intentando acceder a {request.path}")
                flash('Por favor inicia sesión', 'error')
                
                # Si es petición AJAX, devolver JSON
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'No autenticado',
                        'code': 401
                    }), 401
                
                return redirect(url_for('main.login'))
            
            # ========== VERIFICACIÓN 2: ¿Rol está en los permitidos? ==========
            rol_usuario = session.get('usuario_rol', '').lower()
            usuario_id = session.get('usuario_id', 'desconocido')
            
            # Validar que el rol es conocido
            if rol_usuario not in ROLES_DISPONIBLES:
                print(f"[DECORADOR] ⚠️ Rol desconocido '{rol_usuario}' para usuario {usuario_id}")
                flash('Su rol no es válido. Contáctese con administración', 'error')
                return redirect(url_for('main.dashboard'))
            
            # Validar que tiene permisos
            if rol_usuario not in roles_permitidos:
                print(f"[DECORADOR] ❌ Usuario {usuario_id} ({rol_usuario}) rechazado. Requerido: {roles_permitidos}")
                flash(f'Acceso denegado. Se requiere uno de estos roles: {", ".join(roles_permitidos)}', 'error')
                
                # Si es petición AJAX, devolver JSON
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': 'Acceso denegado',
                        'code': 403,
                        'rol_requerido': list(roles_permitidos),
                        'rol_usuario': rol_usuario
                    }), 403
                
                return redirect(url_for('main.dashboard'))
            
            print(f"[DECORADOR] ✅ Acceso concedido a {usuario_id} ({rol_usuario}) en {request.path}")
            return f(*args, **kwargs)
        
        return decorated_function
    return decorador


def requiere_autenticacion(f):
    """
    Decorador que requiere que el usuario esté autenticado
    (Sin restricciones de rol específico)
    
    Uso:
        @requiere_autenticacion
        def mi_ruta():
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # ========== VERIFICACIÓN: ¿Usuario está logueado? ==========
        if not session.get('usuario_logueado'):
            usuario_id = session.get('usuario_id', 'desconocido')
            print(f"[DECORADOR-AUTH] ❌ Usuario no autenticado")
            flash('Por favor inicia sesión', 'error')
            
            # Si es petición AJAX, devolver JSON
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'No autenticado',
                    'code': 401
                }), 401
            
            return redirect(url_for('main.login'))
        
        usuario_id = session.get('usuario_id', 'desconocido')
        print(f"[DECORADOR-AUTH] ✅ Usuario autenticado: {usuario_id}")
        return f(*args, **kwargs)
    
    return decorated_function


def puede_realizar_accion(seccion, accion):
    """
    Decorador que verifica si el usuario puede realizar una acción específica
    en una sección determinada
    
    Uso:
        @bp.route('/usuarios/<rut>', methods=['DELETE'])
        @puede_realizar_accion('usuarios', 'eliminar')
        def eliminar_usuario(rut):
            pass
            
    Args:
        seccion (str): La sección del sistema (usuarios, inventario, etc)
        accion (str): La acción específica (crear, editar, eliminar, etc)
    """
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar autenticación
            if not session.get('usuario_logueado'):
                flash('Por favor inicia sesión', 'error')
                return redirect(url_for('main.login'))
            
            # Obtener rol del usuario
            rol_usuario = session.get('usuario_rol', '').lower()
            usuario_id = session.get('usuario_id', 'desconocido')
            
            # Verificar si puede realizar la acción
            if not usuario_puede_realizar_accion(rol_usuario, seccion, accion):
                print(f"[DECORADOR-ACCION] ❌ {usuario_id} ({rol_usuario}) no puede {accion} en {seccion}")
                flash(f'No tiene permisos para {accion} en esta sección', 'error')
                
                if request.is_json or request.path.startswith('/api/'):
                    return jsonify({
                        'success': False,
                        'error': f'No tiene permisos para {accion}',
                        'code': 403
                    }), 403
                
                return redirect(url_for('main.dashboard'))
            
            print(f"[DECORADOR-ACCION] ✅ {usuario_id} puede {accion} en {seccion}")
            return f(*args, **kwargs)
        
        return decorated_function
    return decorador

