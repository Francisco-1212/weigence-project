from . import chat_model as model


# ============================================================
# 1. Obtener o crear conversación 1 a 1
# ============================================================

def obtener_o_crear_conversacion(user_id, destinatario_id):
    # Buscar conversación existente
    conv = model.obtener_conversacion_entre_usuarios(user_id, destinatario_id)
    if conv:
        return conv

    # Crear conversación nueva
    return model.crear_conversacion(user_id, destinatario_id)


# ============================================================
# 2. Historial de mensajes
# ============================================================

def obtener_historial(conversacion_id, limit=50):
    mensajes = model.obtener_mensajes(conversacion_id, limit=limit)
    return mensajes


# ============================================================
# 3. Enviar mensaje (desde API / HTTP)
# ============================================================

def enviar_mensaje(user_id, destinatario_id, contenido):
    """
    Flujo API normal (crear conversación si no existe).
    Útil para /api/chat/send
    """
    if not contenido or not contenido.strip():
        raise ValueError("Mensaje vacío")

    if len(contenido) > 2000:
        raise ValueError("Mensaje demasiado largo")

    conv = obtener_o_crear_conversacion(user_id, destinatario_id)

    msg = model.insertar_mensaje(conv["id"], user_id, contenido)

    return {
        "conversacion_id": conv["id"],
        "mensaje": _msg_payload(msg),
    }


# ============================================================
# 3. Enviar mensaje para WebSocket
# ============================================================

def guardar_mensaje(conversacion_id, usuario_id, contenido):
    """
    Flujo WS: ya existe la conversación → insert directo.
    NO crea conversaciones nuevas aquí.
    """
    if not contenido or not contenido.strip():
        raise ValueError("Mensaje vacío")

    # Validar que el usuario pertenece a la conversación
    if not model.validar_usuario_en_conversacion(conversacion_id, usuario_id):
        raise PermissionError("No pertenece a la conversación")

    msg = model.insertar_mensaje(conversacion_id, usuario_id, contenido)
    return _msg_payload(msg)


def enviar_mensaje_ws(usuario_id, conversacion_id, contenido):
    if not contenido or len(contenido.strip()) == 0:
        raise ValueError("Mensaje vacío")

    # Validación de permisos
    if not model.validar_usuario_en_conversacion(conversacion_id, usuario_id):
        raise PermissionError("No pertenece a la conversación")

    msg = model.insertar_mensaje(conversacion_id, usuario_id, contenido)

    # payload completo
    return _msg_payload(msg)


# ============================================================
# 4. Marcar como leído
# ============================================================

def marcar_leido(conversacion_id, user_id, ultimo_mensaje_id):
    """
    Marca el último mensaje visto por el usuario.
    Solo actualiza si el nuevo ID es mayor.
    """
    # Validar que esté en la conversación
    if not model.validar_usuario_en_conversacion(conversacion_id, user_id):
        raise PermissionError("Usuario no pertenece a la conversación")

    # Obtener último registrado
    part = model.obtener_participacion(conversacion_id, user_id)
    last = part.get("ultimo_mensaje_leido")

    # No mover hacia atrás
    if last and ultimo_mensaje_id <= last:
        return False

    model.marcar_mensajes_leidos(conversacion_id, user_id, ultimo_mensaje_id)
    return True


# ============================================================
# 5. Helper
# ============================================================

def usuario_puede_ver(conv_id, user):
    return model.validar_usuario_en_conversacion(conv_id, user)


def _msg_payload(msg):
    user = model.obtener_usuario(msg["usuario_id"])

    return {
        "id": msg["id"],
        "conversacion_id": msg["conversacion_id"],
        "usuario_id": msg["usuario_id"],
        "contenido": msg["contenido"],
        "fecha_envio": msg["fecha_envio"],
        "usuario": {
            "id": user["rut_usuario"],
            "nombre": user["nombre"],
            "rol": user["rol"]
        }
    }

