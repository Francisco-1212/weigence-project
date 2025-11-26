"""
==================================================================
CHAT QUERIES - WEIGENCE
Sistema de consultas SQL para chat 1:1
Tablas: chat_conversaciones, chat_participantes, chat_mensajes, usuarios
==================================================================
"""
from api.conexion_supabase import supabase
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ==================================================================
# CONVERSACIONES
# ==================================================================

def obtener_conversacion_entre_usuarios(user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca una conversación 1:1 existente entre dos usuarios
    
    Args:
        user1_id: RUT del primer usuario
        user2_id: RUT del segundo usuario
    
    Returns:
        Dict con datos de conversación o None si no existe
    """
    try:
        logger.info(f"🔍 Buscando conversación entre {user1_id} y {user2_id}")
        
        # Obtener conversaciones del primer usuario
        conv1 = supabase.table('chat_participantes')\
            .select('conversacion_id')\
            .eq('usuario_id', user1_id)\
            .execute()
        
        conv2 = supabase.table('chat_participantes')\
            .select('conversacion_id')\
            .eq('usuario_id', user2_id)\
            .execute()
        
        logger.info(f"📊 Conversaciones user1: {len(conv1.data) if conv1.data else 0}, user2: {len(conv2.data) if conv2.data else 0}")
        
        if not conv1.data or not conv2.data:
            logger.info("❌ Uno de los usuarios no tiene conversaciones")
            return None
        
        # Encontrar conversación común
        ids1 = {c['conversacion_id'] for c in conv1.data}
        ids2 = {c['conversacion_id'] for c in conv2.data}
        comunes = ids1 & ids2
        
        logger.info(f"🔗 Conversaciones comunes: {len(comunes)}")
        
        if not comunes:
            return None
        
        # Retornar la primera conversación común
        conv_id = list(comunes)[0]
        logger.info(f"✅ Conversación encontrada: {conv_id}")
        
        conversacion = supabase.table('chat_conversaciones')\
            .select('*')\
            .eq('id', conv_id)\
            .execute()
        
        if conversacion.data and len(conversacion.data) > 0:
            return conversacion.data[0]
        
        return None
    
    except Exception as e:
        logger.error(f"❌ Error al buscar conversación: {e}", exc_info=True)
        return None


def crear_conversacion_1a1(user1_id: str, user2_id: str) -> Optional[Dict[str, Any]]:
    """
    Crea una nueva conversación 1:1 entre dos usuarios
    
    Args:
        user1_id: RUT del usuario que inicia
        user2_id: RUT del otro usuario
    
    Returns:
        Dict con datos de la conversación creada o None si falla
    """
    try:
        logger.info(f"🆕 Creando conversación entre {user1_id} y {user2_id}")
        
        # Crear conversación
        conv_result = supabase.table('chat_conversaciones')\
            .insert({})\
            .execute()
        
        if not conv_result.data or len(conv_result.data) == 0:
            logger.error("❌ Error: No se recibió datos al crear conversación")
            return None
        
        conv_id = conv_result.data[0]['id']
        logger.info(f"📝 Conversación creada con ID: {conv_id}")
        
        # Registrar participantes
        participantes = [
            {'conversacion_id': conv_id, 'usuario_id': user1_id},
            {'conversacion_id': conv_id, 'usuario_id': user2_id}
        ]
        
        part_result = supabase.table('chat_participantes')\
            .insert(participantes)\
            .execute()
        
        if not part_result.data:
            logger.error(f"❌ Error al registrar participantes en conversación {conv_id}")
            return None
        
        logger.info(f"✅ Conversación creada exitosamente: {conv_id} entre {user1_id} y {user2_id}")
        return conv_result.data[0]
    
    except Exception as e:
        logger.error(f"❌ Error al crear conversación: {e}", exc_info=True)
        return None


def obtener_conversaciones_usuario(user_id: str) -> List[Dict[str, Any]]:
    """
    Obtiene todas las conversaciones de un usuario
    
    Args:
        user_id: RUT del usuario
    
    Returns:
        Lista de conversaciones con participantes y último mensaje
    """
    try:
        # Obtener conversaciones donde el usuario participa
        participaciones = supabase.table('chat_participantes')\
            .select('conversacion_id, ultimo_mensaje_leido')\
            .eq('usuario_id', user_id)\
            .execute()
        
        if not participaciones.data:
            logger.info(f"No hay conversaciones para {user_id}")
            return []
        
        conversaciones = []
        
        for part in participaciones.data:
            conv_id = part['conversacion_id']
            ultimo_leido = part['ultimo_mensaje_leido']
            
            # Datos de conversación
            conv = supabase.table('chat_conversaciones')\
                .select('*')\
                .eq('id', conv_id)\
                .single()\
                .execute()
            
            if not conv.data:
                continue
            
            # Obtener el otro participante (chat 1:1)
            otros_participantes = supabase.table('chat_participantes')\
                .select('usuario_id')\
                .eq('conversacion_id', conv_id)\
                .neq('usuario_id', user_id)\
                .execute()
            
            participantes = []
            for p in otros_participantes.data:
                usuario = supabase.table('usuarios')\
                    .select('rut_usuario, nombre, correo, rol')\
                    .eq('rut_usuario', p['usuario_id'])\
                    .single()\
                    .execute()
                
                if usuario.data:
                    u = usuario.data
                    iniciales = u['nombre'][:2].upper() if u['nombre'] else 'U'
                    
                    participantes.append({
                        'id': u['rut_usuario'],
                        'nombre': u['nombre'],
                        'apellido': '',
                        'nombre_completo': u['nombre'],
                        'email': u['correo'],
                        'rol': u['rol'],
                        'iniciales': iniciales
                    })
            
            # Último mensaje
            ultimo_msg = supabase.table('chat_mensajes')\
                .select('*')\
                .eq('conversacion_id', conv_id)\
                .order('fecha_envio', desc=True)\
                .limit(1)\
                .execute()
            
            ultimo_mensaje = None
            if ultimo_msg.data:
                msg = ultimo_msg.data[0]
                ultimo_mensaje = {
                    'id': msg['id'],
                    'contenido': msg['contenido'],
                    'fecha_envio': msg['fecha_envio'],
                    'usuario_id': msg['usuario_id'],
                    'editado': msg.get('editado', False)
                }
            
            # Contar mensajes no leídos
            no_leidos = 0
            if ultimo_leido:
                # Mensajes posteriores al último leído
                result = supabase.table('chat_mensajes')\
                    .select('id', count='exact')\
                    .eq('conversacion_id', conv_id)\
                    .neq('usuario_id', user_id)\
                    .gt('id', ultimo_leido)\
                    .execute()
                no_leidos = result.count or 0
            else:
                # Todos los mensajes del otro usuario
                result = supabase.table('chat_mensajes')\
                    .select('id', count='exact')\
                    .eq('conversacion_id', conv_id)\
                    .neq('usuario_id', user_id)\
                    .execute()
                no_leidos = result.count or 0
            
            conversaciones.append({
                'id': conv.data['id'],
                'participantes': participantes,
                'ultimo_mensaje': ultimo_mensaje,
                'no_leidos': no_leidos,
                'fecha_creacion': conv.data.get('fecha_creacion'),
                'ultimo_mensaje_timestamp': conv.data.get('ultimo_mensaje_timestamp')
            })
        
        logger.info(f"Conversaciones para {user_id}: {len(conversaciones)}")
        return conversaciones
    
    except Exception as e:
        logger.error(f"Error al obtener conversaciones: {e}")
        return []


# ==================================================================
# MENSAJES
# ==================================================================

def obtener_mensajes_conversacion(conversacion_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Obtiene los mensajes de una conversación
    
    Args:
        conversacion_id: ID de la conversación (UUID)
        limit: Cantidad máxima de mensajes a retornar
    
    Returns:
        Lista de mensajes ordenados por fecha
    """
    try:
        result = supabase.table('chat_mensajes')\
            .select('*')\
            .eq('conversacion_id', conversacion_id)\
            .order('fecha_envio', desc=False)\
            .limit(limit)\
            .execute()
        
        mensajes = []
        for msg in result.data:
            mensajes.append({
                'id': msg['id'],
                'conversacion_id': msg['conversacion_id'],
                'usuario_id': msg['usuario_id'],
                'contenido': msg['contenido'],
                'fecha_envio': msg['fecha_envio'],
                'editado': msg.get('editado', False)
            })
        
        logger.info(f"Mensajes obtenidos: {len(mensajes)} de conversación {conversacion_id}")
        return mensajes
    
    except Exception as e:
        logger.error(f"Error al obtener mensajes: {e}")
        return []


def crear_mensaje(conversacion_id: str, usuario_id: str, contenido: str) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo mensaje en una conversación
    
    Args:
        conversacion_id: ID de la conversación (UUID)
        usuario_id: RUT del usuario que envía
        contenido: Texto del mensaje
    
    Returns:
        Dict con datos del mensaje creado o None si falla
    """
    try:
        # Insertar mensaje
        mensaje_data = {
            'conversacion_id': conversacion_id,
            'usuario_id': usuario_id,
            'contenido': contenido
        }
        
        result = supabase.table('chat_mensajes')\
            .insert(mensaje_data)\
            .execute()
        
        if not result.data:
            logger.error("Error al insertar mensaje")
            return None
        
        mensaje = result.data[0]
        
        # Actualizar último mensaje en conversación
        supabase.table('chat_conversaciones')\
            .update({
                'ultimo_mensaje_id': mensaje['id'],
                'ultimo_mensaje_timestamp': mensaje['fecha_envio']
            })\
            .eq('id', conversacion_id)\
            .execute()
        
        logger.info(f"✅ Mensaje creado: {mensaje['id']} en conversación {conversacion_id}")
        return mensaje
    
    except Exception as e:
        logger.error(f"Error al crear mensaje: {e}")
        return None


def marcar_mensajes_leidos(conversacion_id: str, usuario_id: str) -> bool:
    """
    Marca mensajes como leídos obteniendo automáticamente el último mensaje
    
    Args:
        conversacion_id: ID de la conversación (UUID)
        usuario_id: RUT del usuario que lee
    
    Returns:
        True si se actualizó correctamente, False si hubo error
    """
    try:
        # Obtener el último mensaje de la conversación
        ultimo_msg = supabase.table('chat_mensajes')\
            .select('id')\
            .eq('conversacion_id', conversacion_id)\
            .order('fecha_envio', desc=True)\
            .limit(1)\
            .execute()
        
        if not ultimo_msg.data:
            logger.warning(f"No hay mensajes en conversación {conversacion_id}")
            return True
        
        ultimo_mensaje_id = ultimo_msg.data[0]['id']
        
        supabase.table('chat_participantes')\
            .update({'ultimo_mensaje_leido': ultimo_mensaje_id})\
            .eq('conversacion_id', conversacion_id)\
            .eq('usuario_id', usuario_id)\
            .execute()
        
        logger.info(f"✅ Mensajes marcados como leídos hasta {ultimo_mensaje_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error al marcar mensajes como leídos: {e}")
        return False


# ==================================================================
# USUARIOS
# ==================================================================

def obtener_usuarios_disponibles(usuario_actual: str) -> List[Dict[str, Any]]:
    """
    Obtiene lista de usuarios disponibles para chatear (excepto el actual)
    
    Args:
        usuario_actual: RUT del usuario actual
    
    Returns:
        Lista de usuarios con sus datos
    """
    try:
        result = supabase.table('usuarios')\
            .select('rut_usuario, nombre, correo, rol')\
            .neq('rut_usuario', usuario_actual)\
            .execute()
        
        usuarios = []
        for u in result.data:
            iniciales = u['nombre'][:2].upper() if u['nombre'] else 'U'
            
            usuarios.append({
                'id': u['rut_usuario'],
                'nombre': u['nombre'],
                'apellido': '',
                'nombre_completo': u['nombre'],
                'email': u['correo'],
                'rol': u['rol'],
                'iniciales': iniciales
            })
        
        logger.info(f"Usuarios disponibles: {len(usuarios)}")
        return usuarios
    
    except Exception as e:
        logger.error(f"Error al obtener usuarios: {e}")
        return []


def validar_participante(conversacion_id: str, usuario_id: str) -> bool:
    """
    Valida si un usuario es participante de una conversación
    
    Args:
        conversacion_id: ID de la conversación (UUID)
        usuario_id: RUT del usuario
    
    Returns:
        True si es participante, False si no
    """
    try:
        result = supabase.table('chat_participantes')\
            .select('id')\
            .eq('conversacion_id', conversacion_id)\
            .eq('usuario_id', usuario_id)\
            .execute()
        
        return len(result.data) > 0
    
    except Exception as e:
        logger.error(f"Error al validar participante: {e}")
        return False
