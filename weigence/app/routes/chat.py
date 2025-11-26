"""
==================================================================
CHAT ROUTES - WEIGENCE
Sistema de rutas para chat 1:1 en tiempo real
Usa chat_api.py para la lógica de negocio
==================================================================
"""
from . import bp
from .chat_api import (
    chat_page,
    api_chat_usuarios,
    api_chat_conversaciones,
    api_chat_crear_conversacion,
    api_chat_mensajes,
    api_chat_enviar_mensaje,
    api_chat_marcar_leido
)
from app import csrf  # Importa la instancia CSRF correctamente
# ==================================================================
# PÁGINA PRINCIPAL
# ==================================================================

@bp.route('/chat')
def chat_page_route():
    """Renderiza la página principal del chat"""
    return chat_page()


# ==================================================================
# API ENDPOINTS
# ==================================================================

@bp.route('/api/chat/usuarios', methods=['GET'])
def api_usuarios():
    """GET: Lista de usuarios disponibles para chatear"""
    return api_chat_usuarios()


@bp.route('/api/chat/conversaciones', methods=['GET'])
def api_conversaciones():
    """GET: Conversaciones del usuario actual"""
    return api_chat_conversaciones()


@bp.route('/api/chat/conversacion/crear', methods=['POST'])
@csrf.exempt
def api_crear_conversacion():
    """POST: Crear o obtener conversación 1:1"""
    return api_chat_crear_conversacion()


@bp.route('/api/chat/mensajes/<conversacion_id>', methods=['GET'])
def api_mensajes(conversacion_id):
    """GET: Mensajes de una conversación"""
    return api_chat_mensajes(conversacion_id)


@bp.route('/api/chat/mensajes', methods=['GET'])
def api_mensajes_query():
    """GET: Mensajes de una conversación (usando query param)"""
    from flask import request
    conversacion_id = request.args.get('conversacion_id')
    if not conversacion_id:
        from flask import jsonify
        return jsonify({'error': 'Falta conversacion_id'}), 400
    return api_chat_mensajes(conversacion_id)


@bp.route('/api/chat/mensaje/enviar', methods=['POST'])
@csrf.exempt
def api_enviar_mensaje():
    """POST: Enviar un mensaje"""
    return api_chat_enviar_mensaje()


@bp.route('/api/chat/mensaje/marcar-leido', methods=['POST'])
@csrf.exempt
def api_marcar_leido():
    """POST: Marcar mensajes como leídos"""
    return api_chat_marcar_leido()
