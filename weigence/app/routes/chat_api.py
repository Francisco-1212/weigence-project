"""
==================================================================
CHAT ROUTES - WEIGENCE
Sistema de rutas API para chat 1:1 en tiempo real
==================================================================
"""
from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from api.conexion_supabase import supabase
from app.db.chat_queries import (
    obtener_conversacion_entre_usuarios,
    crear_conversacion_1a1,
    obtener_conversaciones_usuario,
    obtener_mensajes_conversacion,
    crear_mensaje,
    marcar_mensajes_leidos,
    obtener_usuarios_disponibles,
    validar_participante
)
import logging

logger = logging.getLogger(__name__)

# Este blueprint se registra en app/routes/__init__.py
# No es necesario crear un blueprint separado aquí


def usuario_autenticado():
    """Obtiene el ID del usuario autenticado de la sesión"""
    return session.get('usuario_id')


# ==================================================================
# PÁGINA PRINCIPAL DEL CHAT

def chat_page():
    """Renderiza la página principal del chat"""
    user_id = usuario_autenticado()
    if not user_id:
        return redirect(url_for('main.login'))
    return render_template('pagina/chat.html')


# ==================================================================
# API: USUARIOS DISPONIBLES
# ==================================================================

def api_chat_usuarios():
    """
    GET /api/chat/usuarios
    Obtiene lista de usuarios disponibles para chatear
    
    Response:
        {
            "usuarios": [
                {
                    "id": "12345678-9",
                    "nombre": "Juan",
                    "apellido": "",
                    "nombre_completo": "Juan Pérez",
                    "email": "juan@weigence.cl",
                    "rol": "vendedor",
                    "iniciales": "JU"
                }
            ]
        }
    """
    try:
        user_id = usuario_autenticado()
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        usuarios = obtener_usuarios_disponibles(user_id)
        
        logger.info(f"Usuarios disponibles para {user_id}: {len(usuarios)}")
        return jsonify({'usuarios': usuarios}), 200
    
    except Exception as e:
        logger.error(f"Error en api_chat_usuarios: {e}", exc_info=True)
        return jsonify({'error': 'Error al cargar usuarios'}), 500


# ==================================================================
# API: CONVERSACIONES
# ==================================================================

def api_chat_conversaciones():
    """
    GET /api/chat/conversaciones
    Obtiene todas las conversaciones del usuario actual
    
    Response:
        {
            "conversaciones": [
                {
                    "id": "uuid-123",
                    "nombre": "Chat con Juan",
                    "es_grupal": false,
                    "participantes": [...],
                    "ultimo_mensaje": {...},
                    "ultima_actualizacion": "2025-11-25T10:30:00",
                    "mensajes_no_leidos": 3
                }
            ]
        }
    """
    try:
        user_id = usuario_autenticado()
        logger.info(f"👤 Usuario autenticado: {user_id}")
        
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        data = request.get_json()
        participantes = data.get('participantes', [])
        
        logger.info(f"📦 Participantes recibidos: {participantes}")
        
        if not participantes or len(participantes) != 1:
            return jsonify({'error': 'Debes especificar exactamente un participante'}), 400
        
        otro_usuario_id = participantes[0]
        logger.info(f"🔍 Buscando/creando conversación entre {user_id} y {otro_usuario_id}")
        
        # Buscar conversación existente
        conv_existente = obtener_conversacion_entre_usuarios(user_id, otro_usuario_id)
        
        if conv_existente:
            logger.info(f"✅ Conversación existente encontrada: {conv_existente['id']}")
            return jsonify({
                'conversacion_id': conv_existente['id'],
                'conversacion': {
                    'id': conv_existente['id']
                },
                'mensaje': 'Conversación existente encontrada'
            }), 200
        
        # Crear nueva conversación
        logger.info(f"🆕 No existe conversación, creando nueva...")
        nueva_conv = crear_conversacion_1a1(user_id, otro_usuario_id)
        
        if not nueva_conv:
            logger.error("❌ Error: crear_conversacion_1a1 retornó None")
            return jsonify({'error': 'Error al crear conversación'}), 500

        logger.info(f"🎉 Nueva conversación creada: {nueva_conv['id']}")
        return jsonify({
            'conversacion_id': nueva_conv['id'],
            'conversacion': {
                'id': nueva_conv['id']
            },
            'mensaje': 'Conversación creada'
        }), 201
    
    except Exception as e:
        logger.error(f"💥 Error en api_chat_crear_conversacion: {e}", exc_info=True)
        return jsonify({'error': f'Error al crear conversación: {str(e)}'}), 500


# ==================================================================
# API: MENSAJES DE CONVERSACIÓN
# ==================================================================

def api_chat_mensajes(conversacion_id):
    """
    GET /api/chat/mensajes/<conversacion_id>
    Obtiene el historial de mensajes de una conversación
    
    Response:
        {
            "mensajes": [
                {
                    "id": "uuid-msg",
                    "conversacion_id": "uuid-conv",
                    "usuario_id": "12345678-9",
                    "contenido": "Hola!",
                    "fecha_envio": "2025-11-25T10:30:00",
                    "editado": false,
                    "eliminado": false,
                    "usuario": {
                        "id": "12345678-9",
                        "nombre": "Juan",
                        "nombre_completo": "Juan Pérez",
                        "email": "juan@weigence.cl"
                    }
                }
            ]
        }
    """
    try:
        user_id = usuario_autenticado()
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        # Validar acceso
        if not validar_participante(conversacion_id, user_id):
            return jsonify({'error': 'No tienes acceso a esta conversación'}), 403
        
        mensajes = obtener_mensajes_conversacion(conversacion_id, limit=100)

        # Obtener datos de usuarios en un solo query
        usuarios_ids = {msg['usuario_id'] for msg in mensajes}
        usuarios_map = {}

        if usuarios_ids:
            usuarios_result = supabase.table('usuarios') \
                .select('rut_usuario, nombre, correo, rol') \
                .in_('rut_usuario', list(usuarios_ids)) \
                .execute()

            if usuarios_result.data:
                for usuario in usuarios_result.data:
                    usuarios_map[usuario['rut_usuario']] = {
                        'id': usuario['rut_usuario'],
                        'nombre': usuario.get('nombre') or 'Usuario',
                        'apellido': '',
                        'nombre_completo': usuario.get('nombre') or 'Usuario',
                        'email': usuario.get('correo') or '',
                        'rol': usuario.get('rol')
                    }

        # Enriquecer mensajes con flags y datos de usuario
        for msg in mensajes:
            es_mio = msg['usuario_id'] == user_id
            msg['es_mio'] = es_mio
            msg['es_propio'] = es_mio  # Alias para front-end
            msg['usuario'] = usuarios_map.get(msg['usuario_id'], {
                'id': msg['usuario_id'],
                'nombre': 'Usuario',
                'apellido': '',
                'nombre_completo': 'Usuario',
                'email': '',
                'rol': ''
            })

        logger.info(f"Mensajes para {conversacion_id}: {len(mensajes)}")
        return jsonify({'mensajes': mensajes}), 200
    
    except Exception as e:
        logger.error(f"Error en api_chat_mensajes: {e}", exc_info=True)
        return jsonify({'error': 'Error al cargar mensajes'}), 500


# ==================================================================
# API: ENVIAR MENSAJE
# ==================================================================

def api_chat_enviar_mensaje():
    """
    POST /api/chat/mensaje/enviar
    Envía un nuevo mensaje a una conversación
    
    Request:
        {
            "conversacion_id": "uuid-123",
            "contenido": "Hola, ¿cómo estás?"
        }
    
    Response:
        {
            "mensaje": {
                "id": "uuid-msg",
                "conversacion_id": "uuid-conv",
                "usuario_id": "12345678-9",
                "contenido": "Hola, ¿cómo estás?",
                "fecha_envio": "2025-11-25T10:30:00",
                "editado": false,
                "eliminado": false
            }
        }
    """
    print("=" * 80)
    print("🔥 ENDPOINT ENVIAR MENSAJE LLAMADO")
    print("=" * 80)
    
    try:
        user_id = usuario_autenticado()
        print(f"👤 Usuario autenticado: {user_id}")
        
        if not user_id:
            print("❌ No autenticado")
            return jsonify({'error': 'No autenticado'}), 401
        
        data = request.get_json()
        print(f"📦 Data recibida: {data}")
        
        conversacion_id = data.get('conversacion_id')
        contenido = data.get('contenido', '').strip()
        
        print(f"💬 conversacion_id={conversacion_id}, contenido='{contenido}'")
        
        if not conversacion_id or not contenido:
            print("❌ Faltan datos")
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        # Validar acceso
        print(f"🔐 Validando acceso a conversación {conversacion_id}")
        if not validar_participante(conversacion_id, user_id):
            print("❌ No tiene acceso")
            return jsonify({'error': 'No tienes acceso a esta conversación'}), 403
        
        # Crear mensaje
        print(f"✍️ Creando mensaje...")
        mensaje = crear_mensaje(conversacion_id, user_id, contenido)
        
        if not mensaje:
            print("❌ Error al crear mensaje")
            return jsonify({'error': 'Error al enviar mensaje'}), 500
        
        print(f"✅ Mensaje creado exitosamente: {mensaje['id']}")
        logger.info(f"Mensaje enviado: {mensaje['id']} en {conversacion_id}")
        
        # Emitir evento WebSocket (se maneja en chat_ws.py)
        try:
            from app.sockets.chat_ws import emitir_mensaje_nuevo
            emitir_mensaje_nuevo(conversacion_id, mensaje, user_id)
        except ImportError:
            logger.warning("WebSocket no disponible, enviando solo por API")
        
        print("🎉 Retornando respuesta 201")
        return jsonify({'mensaje': mensaje}), 201
    
    except Exception as e:
        print(f"💥 EXCEPCIÓN CAPTURADA: {e}")
        import traceback
        traceback.print_exc()
        logger.error(f"Error en api_chat_enviar_mensaje: {e}", exc_info=True)
        return jsonify({'error': 'Error al enviar mensaje'}), 500


# ==================================================================
# API: MARCAR MENSAJES COMO LEÍDOS
# ==================================================================

def api_chat_marcar_leido():
    """
    POST /api/chat/mensaje/marcar-leido
    Marca todos los mensajes de una conversación como leídos
    
    Request:
        {
            "conversacion_id": "uuid-123"
        }
    
    Response:
        {
            "success": true
        }
    """
    try:
        user_id = usuario_autenticado()
        if not user_id:
            return jsonify({'error': 'No autenticado'}), 401
        
        data = request.get_json()
        conversacion_id = data.get('conversacion_id')
        
        if not conversacion_id:
            return jsonify({'error': 'Falta conversacion_id'}), 400
        
        # Validar acceso
        if not validar_participante(conversacion_id, user_id):
            return jsonify({'error': 'No tienes acceso a esta conversación'}), 403
        
        # Marcar como leídos
        exito = marcar_mensajes_leidos(conversacion_id, user_id)
        
        if not exito:
            return jsonify({'error': 'Error al marcar mensajes'}), 500
        
        logger.info(f"Mensajes marcados como leídos en {conversacion_id} por {user_id}")
        return jsonify({'success': True}), 200
    
    except Exception as e:
        logger.error(f"Error en api_chat_marcar_leido: {e}", exc_info=True)
        return jsonify({'error': 'Error al marcar mensajes'}), 500


# ==================================================================
# API: CREAR O RECUPERAR CONVERSACIÓN 1 a 1
# ==================================================================

def api_chat_crear_conversacion():
    """
    POST /api/chat/conversacion/crear
    Crea o recupera una conversación 1 a 1 entre dos usuarios.
    Request JSON:
        {
            "participantes": ["rut_usuario_1", "rut_usuario_2"]
        }
    Response:
        {
            "success": True,
            "conversacion_id": "id_conversacion"
        }
    """
    try:
        data = request.get_json()
        participantes = data.get("participantes", [])
        if len(participantes) != 2:
            return jsonify({"success": False, "error": "Se requieren dos participantes"}), 400
        usuario_id, destinatario_id = participantes
        if not usuario_id or not destinatario_id:
            return jsonify({"success": False, "error": "Faltan IDs de usuario"}), 400

        # Verificar si ya existe la conversación
        conversacion = obtener_conversacion_entre_usuarios(usuario_id, destinatario_id)
        if conversacion:
            return jsonify({"success": True, "conversacion": {"id": conversacion["id"]}})

        # Si no existe, crearla
        nueva_conversacion = crear_conversacion_1a1(usuario_id, destinatario_id)
        if nueva_conversacion:
            return jsonify({"success": True, "conversacion": {"id": nueva_conversacion["id"]}})
        else:
            return jsonify({"success": False, "error": "No se pudo crear la conversación"}), 500
    except Exception as e:
        logger.error(f"💥 Error en api_chat_crear_conversacion: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================================================================
# REGISTRO DE RUTAS
# ==================================================================
# Las rutas se registran en app/routes/__init__.py usando este módulo
