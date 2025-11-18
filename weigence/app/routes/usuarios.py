"""
Rutas para gestión de usuarios (CRUD)
Accesible solo para administrador y jefe
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from . import bp
from .decorators import requiere_rol
from api.conexion_supabase import supabase
from app.utils.security import hash_password, validar_fortaleza_password, validar_email, validar_rut_chileno, sanitizar_input
import re
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Roles disponibles en el sistema
ROLES_DISPONIBLES = ['farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador']

# Permisos por rol (define qué secciones ve cada rol)
PERMISOS_POR_ROL = {
    'farmaceutico': ['dashboard', 'inventario', 'perfil'],
    'bodeguera': ['dashboard', 'inventario', 'movimientos', 'alertas', 'perfil'],
    'supervisor': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'alertas', 'perfil'],
    'jefe': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil'],
    'administrador': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil']
}


@bp.route('/usuarios', methods=['GET'])
@requiere_rol('administrador', 'jefe')
def usuarios():
    """Página principal de gestión de usuarios"""
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'usuarios':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó a Gestión de Usuarios")
        session['last_page'] = 'usuarios'
    try:
        # Obtener todos los usuarios
        response = supabase.table("usuarios").select("*").execute()
        usuarios_lista = response.data if response.data else []
        
        # Filtrar campos sensibles en la vista
        usuarios_publicos = []
        for u in usuarios_lista:
            usuario_publico = {
                'rut_usuario': u.get('rut_usuario'),
                'nombre': u.get('nombre'),
                'correo': u.get('correo'),
                'rol': u.get('rol'),
                'fecha_registro': u.get('fecha_registro'),
                'numero celular': u.get('numero celular')
            }
            usuarios_publicos.append(usuario_publico)
        
        return render_template('pagina/usuarios.html', usuarios=usuarios_publicos, roles=ROLES_DISPONIBLES)
    
    except Exception as e:
        print(f"[USUARIOS] Error al cargar lista de usuarios: {e}")
        flash(f'Error al cargar usuarios: {str(e)}', 'danger')
        return redirect(url_for('main.dashboard'))


@bp.route('/api/usuarios', methods=['GET'])
@requiere_rol('administrador', 'jefe')
def api_obtener_usuarios():
    """API para obtener lista de usuarios (formato JSON)"""
    try:
        response = supabase.table("usuarios").select("*").execute()
        usuarios_lista = response.data if response.data else []
        
        # Filtrar campos sensibles
        usuarios_publicos = []
        for u in usuarios_lista:
            usuario_publico = {
                'rut_usuario': u.get('rut_usuario'),
                'nombre': u.get('nombre'),
                'correo': u.get('correo'),
                'rol': u.get('rol'),
                'fecha_registro': u.get('fecha_registro'),
                'numero celular': u.get('numero celular')
            }
            usuarios_publicos.append(usuario_publico)
        
        return jsonify({
            'success': True,
            'data': usuarios_publicos,
            'total': len(usuarios_publicos)
        }), 200
    
    except Exception as e:
        print(f"[API-USUARIOS] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/usuarios/<rut>', methods=['GET'])
@requiere_rol('administrador', 'jefe')
def api_obtener_usuario(rut):
    """API para obtener un usuario específico"""
    try:
        response = supabase.table("usuarios").select("*").eq("rut_usuario", rut).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        usuario = response.data[0]
        
        # Filtrar campos sensibles
        usuario_publico = {
            'rut_usuario': usuario.get('rut_usuario'),
            'nombre': usuario.get('nombre'),
            'correo': usuario.get('correo'),
            'rol': usuario.get('rol'),
            'fecha_registro': usuario.get('fecha_registro'),
            'numero celular': usuario.get('numero celular')
        }
        
        return jsonify({
            'success': True,
            'data': usuario_publico
        }), 200
    
    except Exception as e:
        print(f"[API-USUARIOS-GET] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def validar_email(email):
    """Valida formato de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_rut(rut):
    """Valida formato básico de RUT chileno"""
    # Formato esperado: XX.XXX.XXX-X o XXXXXXXX-X
    patron = r'^(\d{1,2}\.\d{3}\.\d{3}-\d|^\d{7,8}-\d)$'
    return re.match(patron, rut) is not None


@bp.route('/api/usuarios', methods=['POST'])
@requiere_rol('administrador', 'jefe')
def api_crear_usuario():
    """API para crear nuevo usuario"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({'success': False, 'error': 'No se pudo procesar el JSON'}), 400
        
        print(f"[API-CREAR-USUARIO] Datos recibidos: {data.keys()}")
        
        # Obtener y validar datos (flexible con mayúsculas/minúsculas)
        rut = sanitizar_input(data.get('rut_usuario', '').strip())
        nombre = sanitizar_input(data.get('nombre', '').strip())
        correo = data.get('correo', '').strip().lower()
        rol = data.get('rol', '').strip().lower()
        numero_celular = sanitizar_input(data.get('numero_celular', data.get('numero celular', '')).strip())
        contraseña = data.get('contraseña', data.get('Contraseña', '')).strip()
        
        logger.info(f"[API-CREAR-USUARIO] Intento de crear usuario: {nombre} ({rut})")
        
        # Validaciones
        if not rut or not nombre or not correo or not rol or not contraseña:
            logger.warning(f"[API-CREAR-USUARIO] ✗ Campos faltantes")
            return jsonify({
                'success': False,
                'error': 'Todos los campos son requeridos'
            }), 400
        
        # Validar RUT chileno
        if not validar_rut_chileno(rut):
            return jsonify({
                'success': False,
                'error': 'RUT inválido'
            }), 400
        
        if not validar_email(correo):
            return jsonify({
                'success': False,
                'error': 'Email inválido'
            }), 400
        
        # Validar fortaleza de contraseña
        es_valida, mensaje_error = validar_fortaleza_password(contraseña)
        if not es_valida:
            return jsonify({
                'success': False,
                'error': mensaje_error
            }), 400
        
        if rol not in ROLES_DISPONIBLES:
            return jsonify({
                'success': False,
                'error': f'Rol inválido. Roles disponibles: {", ".join(ROLES_DISPONIBLES)}'
            }), 400
        
        # Verificar si el usuario ya existe
        existe = supabase.table("usuarios").select("*").eq("rut_usuario", rut).execute()
        if existe.data and len(existe.data) > 0:
            return jsonify({
                'success': False,
                'error': 'El usuario (RUT) ya existe'
            }), 409
        
        # Verificar si el email ya existe
        existe_email = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if existe_email.data and len(existe_email.data) > 0:
            return jsonify({
                'success': False,
                'error': 'El email ya está registrado'
            }), 409
        
        # Generar hash seguro de la contraseña
        try:
            password_hash = hash_password(contraseña)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 400
        
        # Crear nuevo usuario
        nuevo_usuario = {
            'rut_usuario': rut,
            'nombre': nombre,
            'correo': correo,
            'rol': rol,
            'numero celular': numero_celular if numero_celular else None,
            'password_hash': password_hash,
            'Contraseña': password_hash,  # Compatibilidad temporal
            'fecha_registro': datetime.now().isoformat(),
            'reset_token': None,
            'reset_token_expires': None
        }
        
        logger.info(f"[API-CREAR-USUARIO] Creando usuario: {rut}")
        response = supabase.table("usuarios").insert(nuevo_usuario).execute()
        
        if hasattr(response, 'data') and response.data:
            logger.info(f"[API-CREAR-USUARIO] ✅ Usuario creado: {rut}")
            return jsonify({
                'success': True,
                'message': 'Usuario creado correctamente',
                'usuario': nuevo_usuario
            }), 201
        else:
            print(f"[API-CREAR-USUARIO] ❌ Error al crear usuario")
            return jsonify({
                'success': False,
                'error': 'Error al crear el usuario'
            }), 500
    
    except Exception as e:
        print(f"[API-CREAR-USUARIO] Exception: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500


@bp.route('/api/usuarios/<rut>', methods=['PUT'])
@requiere_rol('administrador', 'jefe')
def api_editar_usuario(rut):
    """API para editar usuario existente"""
    try:
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({'success': False, 'error': 'No se pudo procesar el JSON'}), 400
        
        # Verificar que el usuario existe
        existe = supabase.table("usuarios").select("*").eq("rut_usuario", rut).execute()
        if not existe.data or len(existe.data) == 0:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        # Obtener datos a actualizar
        update_data = {}
        
        if 'nombre' in data and data['nombre']:
            update_data['nombre'] = data['nombre'].strip()
        
        if 'correo' in data and data['correo']:
            if not validar_email(data['correo']):
                return jsonify({'success': False, 'error': 'Email inválido'}), 400
            update_data['correo'] = data['correo'].strip()
        
        if 'rol' in data and data['rol']:
            if data['rol'] not in ROLES_DISPONIBLES:
                return jsonify({
                    'success': False,
                    'error': f'Rol inválido. Roles disponibles: {", ".join(ROLES_DISPONIBLES)}'
                }), 400
            update_data['rol'] = data['rol'].strip()
        
        # Flexible con nombre del campo de teléfono
        if 'numero_celular' in data:
            update_data['numero celular'] = data['numero_celular'].strip() if data['numero_celular'] else None
        elif 'numero celular' in data:
            update_data['numero celular'] = data['numero celular'].strip() if data['numero celular'] else None
        
        # Flexible con nombre del campo de contraseña
        if 'contraseña' in data and data['contraseña']:
            update_data['Contraseña'] = data['contraseña'].strip()
        elif 'Contraseña' in data and data['Contraseña']:
            update_data['Contraseña'] = data['Contraseña'].strip()
        
        if not update_data:
            return jsonify({
                'success': False,
                'error': 'No hay datos para actualizar'
            }), 400
        
        print(f"[API-EDITAR-USUARIO] Actualizando usuario: {rut} con datos: {update_data.keys()}")
        response = supabase.table("usuarios").update(update_data).eq("rut_usuario", rut).execute()
        
        if hasattr(response, 'data') and response.data:
            print(f"[API-EDITAR-USUARIO] ✅ Usuario actualizado: {rut}")
            return jsonify({
                'success': True,
                'message': 'Usuario actualizado correctamente'
            }), 200
        else:
            print(f"[API-EDITAR-USUARIO] ❌ Error al actualizar usuario")
            return jsonify({
                'success': False,
                'error': 'Error al actualizar el usuario'
            }), 500
    
    except Exception as e:
        print(f"[API-EDITAR-USUARIO] Exception: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500


@bp.route('/api/usuarios/<rut>', methods=['DELETE'])
@requiere_rol('administrador', 'jefe')
def api_eliminar_usuario(rut):
    """API para eliminar usuario"""
    try:
        # Verificar que no es el mismo usuario logueado
        if session.get('usuario_id') == rut:
            return jsonify({
                'success': False,
                'error': 'No puedes eliminar tu propia cuenta'
            }), 400
        
        # Verificar que el usuario existe
        existe = supabase.table("usuarios").select("*").eq("rut_usuario", rut).execute()
        if not existe.data or len(existe.data) == 0:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        print(f"[API-ELIMINAR-USUARIO] Eliminando usuario: {rut}")
        response = supabase.table("usuarios").delete().eq("rut_usuario", rut).execute()
        
        print(f"[API-ELIMINAR-USUARIO] ✅ Usuario eliminado: {rut}")
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado correctamente'
        }), 200
    
    except Exception as e:
        print(f"[API-ELIMINAR-USUARIO] Exception: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500
