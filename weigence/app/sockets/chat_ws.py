"""
==================================================================
CHAT WEBSOCKET - WEIGENCE
Sistema de comunicación en tiempo real con Flask-SocketIO
==================================================================
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session, request
import logging

logger = logging.getLogger(__name__)

# Instancia de SocketIO (se inicializa en __init__.py)
socketio = None

# Diccionario de usuarios conectados: {user_id: sid}
usuarios_conectados = {}


# ==================================================================
# INICIALIZACIÓN
# ==================================================================

def init_socketio(app):
    """
    Inicializa SocketIO con la aplicación Flask
    
    Args:
        app: Instancia de Flask
    
    Returns:
        Instancia de SocketIO configurada
    """
    global socketio
    
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        logger=True,
        engineio_logger=False,
        async_mode='threading'
    )
    
    logger.info("✅ SocketIO inicializado correctamente")
    return socketio


# ==================================================================
# EVENTOS DE CONEXIÓN
# ==================================================================

def on_connect():
    """Evento: Cliente se conecta al WebSocket"""
    user_id = session.get('usuario_id')
    
    if not user_id:
        logger.warning("Conexión rechazada: usuario no autenticado")
        return False
    
    # Guardar SID del usuario
    usuarios_conectados[user_id] = request.sid
    
    logger.info(f"✅ Usuario conectado: {user_id} (SID: {request.sid})")
    emit('conectado', {'mensaje': 'Conectado al chat en tiempo real'})


def on_disconnect():
    """Evento: Cliente se desconecta del WebSocket"""
    user_id = session.get('usuario_id')
    
    if user_id and user_id in usuarios_conectados:
        del usuarios_conectados[user_id]
        logger.info(f"❌ Usuario desconectado: {user_id}")


# ==================================================================
# EVENTOS DE CHAT
# ==================================================================

def on_unirse_conversacion(data):
    """
    Evento: Usuario se une a una conversación (room)
    
    Args:
        data: {
            "conversacion_id": "uuid-123"
        }
    """
    user_id = session.get('usuario_id')
    conversacion_id = data.get('conversacion_id')
    
    if not user_id or not conversacion_id:
        emit('error', {'mensaje': 'Datos inválidos'})
        return
    
    # Validar que el usuario sea participante
    from app.db.chat_queries import validar_participante
    
    if not validar_participante(conversacion_id, user_id):
        emit('error', {'mensaje': 'No tienes acceso a esta conversación'})
        return
    
    # Unirse a la sala
    join_room(conversacion_id)
    logger.info(f"👥 Usuario {user_id} se unió a conversación {conversacion_id}")
    
    emit('unido_conversacion', {
        'conversacion_id': conversacion_id,
        'mensaje': 'Te has unido a la conversación'
    })


def on_salir_conversacion(data):
    """
    Evento: Usuario sale de una conversación (room)
    
    Args:
        data: {
            "conversacion_id": "uuid-123"
        }
    """
    user_id = session.get('usuario_id')
    conversacion_id = data.get('conversacion_id')
    
    if not conversacion_id:
        return
    
    leave_room(conversacion_id)
    logger.info(f"👋 Usuario {user_id} salió de conversación {conversacion_id}")


def on_mensaje_enviar(data):
    """
    Evento: Usuario envía un mensaje (alternativo a API REST)
    
    Args:
        data: {
            "conversacion_id": "uuid-123",
            "contenido": "Hola!"
        }
    """
    user_id = session.get('usuario_id')
    conversacion_id = data.get('conversacion_id')
    contenido = data.get('contenido', '').strip()
    
    if not user_id or not conversacion_id or not contenido:
        emit('error', {'mensaje': 'Datos inválidos'})
        return
    
    # Validar acceso
    from app.db.chat_queries import validar_participante, crear_mensaje
    
    if not validar_participante(conversacion_id, user_id):
        emit('error', {'mensaje': 'No tienes acceso a esta conversación'})
        return
    
    # Crear mensaje en BD
    mensaje = crear_mensaje(conversacion_id, user_id, contenido)
    
    if not mensaje:
        emit('error', {'mensaje': 'Error al enviar mensaje'})
        return
    
    # Obtener datos del usuario
    from api.conexion_supabase import supabase
    usuario = supabase.table('usuarios')\
        .select('rut_usuario, nombre, correo')\
        .eq('rut_usuario', user_id)\
        .single()\
        .execute()
    
    usuario_data = None
    if usuario.data:
        u = usuario.data
        usuario_data = {
            'id': u['rut_usuario'],
            'nombre': u['nombre'],
            'apellido': '',
            'nombre_completo': u['nombre'],
            'email': u['correo']
        }
    
    mensaje_completo = {
        'id': mensaje['id'],
        'conversacion_id': mensaje['conversacion_id'],
        'usuario_id': mensaje['usuario_id'],
        'contenido': mensaje['contenido'],
        'fecha_envio': mensaje['fecha_envio'],
        'editado': mensaje['editado'],
        'eliminado': mensaje['eliminado'],
        'usuario': usuario_data
    }
    
    # Emitir a todos los participantes de la conversación
    emit('mensaje_recibido', mensaje_completo, room=conversacion_id)
    
    logger.info(f"📨 Mensaje enviado vía WebSocket: {mensaje['id']} en {conversacion_id}")


def on_escribiendo(data):
    """
    Evento: Usuario está escribiendo
    
    Args:
        data: {
            "conversacion_id": "uuid-123"
        }
    """
    user_id = session.get('usuario_id')
    conversacion_id = data.get('conversacion_id')
    
    if not user_id or not conversacion_id:
        return
    
    # Obtener nombre del usuario
    from api.conexion_supabase import supabase
    usuario = supabase.table('usuarios')\
        .select('nombre')\
        .eq('rut_usuario', user_id)\
        .single()\
        .execute()
    
    nombre = usuario.data['nombre'] if usuario.data else 'Usuario'
    
    # Emitir a la conversación (excluyendo al emisor)
    emit('usuario_escribiendo', {
        'conversacion_id': conversacion_id,
        'usuario_id': user_id,
        'nombre': nombre
    }, room=conversacion_id, skip_sid=request.sid)


# ==================================================================
# FUNCIONES AUXILIARES PARA EMISIÓN
# ==================================================================

def emitir_mensaje_nuevo(conversacion_id: str, mensaje: dict, remitente_id: str):
    """
    Emite un mensaje nuevo a todos los participantes de una conversación
    
    Args:
        conversacion_id: ID de la conversación
        mensaje: Dict con datos del mensaje
        remitente_id: RUT del usuario que envió el mensaje
    """
    if not socketio:
        return
    
    try:
        # Obtener datos del usuario remitente
        from api.conexion_supabase import supabase
        usuario = supabase.table('usuarios')\
            .select('rut_usuario, nombre, correo')\
            .eq('rut_usuario', remitente_id)\
            .single()\
            .execute()
        
        usuario_data = None
        if usuario.data:
            u = usuario.data
            usuario_data = {
                'id': u['rut_usuario'],
                'nombre': u['nombre'],
                'apellido': '',
                'nombre_completo': u['nombre'],
                'email': u['correo']
            }
        
        mensaje_completo = {
            'id': mensaje['id'],
            'conversacion_id': mensaje['conversacion_id'],
            'usuario_id': mensaje['usuario_id'],
            'contenido': mensaje['contenido'],
            'fecha_envio': mensaje['fecha_envio'],
            'editado': mensaje['editado'],
            'eliminado': mensaje['eliminado'],
            'usuario': usuario_data
        }
        
        # Emitir a la sala de la conversación
        socketio.emit('mensaje_recibido', mensaje_completo, room=conversacion_id)
        
        logger.info(f"📡 Mensaje emitido vía SocketIO: {mensaje['id']}")
    
    except Exception as e:
        logger.error(f"Error al emitir mensaje: {e}")


def emitir_nueva_conversacion(user_id: str, conversacion: dict):
    """
    Notifica a un usuario sobre una nueva conversación
    
    Args:
        user_id: RUT del usuario a notificar
        conversacion: Dict con datos de la conversación
    """
    if not socketio or user_id not in usuarios_conectados:
        return
    
    try:
        sid = usuarios_conectados[user_id]
        
        socketio.emit('nueva_conversacion', {
            'conversacion': conversacion
        }, room=sid)
        
        logger.info(f"📬 Nueva conversación notificada a {user_id}")
    
    except Exception as e:
        logger.error(f"Error al emitir nueva conversación: {e}")


# ==================================================================
# REGISTRO DE EVENTOS
# ==================================================================

def registrar_eventos_socket():
    """Registra todos los eventos de SocketIO"""
    if not socketio:
        logger.error("❌ SocketIO no inicializado")
        return
    
    socketio.on_event('connect', on_connect)
    socketio.on_event('disconnect', on_disconnect)
    socketio.on_event('unirse_conversacion', on_unirse_conversacion)
    socketio.on_event('salir_conversacion', on_salir_conversacion)
    socketio.on_event('mensaje_enviar', on_mensaje_enviar)
    socketio.on_event('escribiendo', on_escribiendo)
    
    logger.info("✅ Eventos de SocketIO registrados")
