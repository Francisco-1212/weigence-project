from . import chat_model as model


# ============================================================
# 1. Obtener o crear conversacion 1 a 1
# ============================================================

def obtener_o_crear_conversacion(user_id, destinatario_id):
    conv = model.obtener_conversacion_entre_usuarios(user_id, destinatario_id)
    if conv:
        return conv
    return model.crear_conversacion(user_id, destinatario_id)


# ============================================================
# 2. Historial de mensajes
# ============================================================

def obtener_historial(conversacion_id, limit=50):
    return model.obtener_mensajes(conversacion_id, limit=limit)


# ============================================================
# 3. Enviar mensaje (desde API / HTTP)
# ============================================================

def enviar_mensaje(user_id, destinatario_id, contenido):
    if not contenido or not contenido.strip():
        raise ValueError("Mensaje vacio")
    if len(contenido) > 2000:
        raise ValueError("Mensaje demasiado largo")

    conv = obtener_o_crear_conversacion(user_id, destinatario_id)
    msg = model.insertar_mensaje(conv["id"], user_id, contenido)
    return {"conversacion_id": conv["id"], "mensaje": _msg_payload(msg)}


# ============================================================
# 3b. Enviar mensaje para WebSocket
# ============================================================

def guardar_mensaje(conversacion_id, usuario_id, contenido, reply_to=None):
    if not contenido or not contenido.strip():
        raise ValueError("Mensaje vacio")
    if not model.validar_usuario_en_conversacion(conversacion_id, usuario_id):
        raise PermissionError("No pertenece a la conversacion")

    msg = model.insertar_mensaje(conversacion_id, usuario_id, contenido, reply_to)
    return _msg_payload(msg)


def enviar_mensaje_ws(usuario_id, conversacion_id, contenido):
    if not contenido or not contenido.strip():
        raise ValueError("Mensaje vacio")
    if not model.validar_usuario_en_conversacion(conversacion_id, usuario_id):
        raise PermissionError("No pertenece a la conversacion")

    msg = model.insertar_mensaje(conversacion_id, usuario_id, contenido)
    return _msg_payload(msg)


# ============================================================
# 4. Marcar como leido
# ============================================================

def marcar_leido(conversacion_id, user_id, ultimo_mensaje_id):
    if not model.validar_usuario_en_conversacion(conversacion_id, user_id):
        raise PermissionError("Usuario no pertenece a la conversacion")

    part = model.obtener_participacion(conversacion_id, user_id)
    
    # Si no existe participación o es la primera vez, siempre marcar
    if not part:
        model.marcar_mensajes_leidos(conversacion_id, user_id, ultimo_mensaje_id)
        return True
    
    last = part.get("ultimo_mensaje_leido")
    
    # Si nunca ha leído nada o el nuevo mensaje es más reciente
    if not last or ultimo_mensaje_id > last:
        model.marcar_mensajes_leidos(conversacion_id, user_id, ultimo_mensaje_id)
        return True
    
    return False


# ============================================================
# 5. Helper
# ============================================================

def usuario_puede_ver(conv_id, user):
    return model.validar_usuario_en_conversacion(conv_id, user)


def _msg_payload(msg):
    user = model.obtener_usuario(msg["usuario_id"])
    payload = {
        "id": msg["id"],
        "conversacion_id": msg["conversacion_id"],
        "usuario_id": msg["usuario_id"],
        "contenido": msg["contenido"],
        "fecha_envio": msg["fecha_envio"],
        "usuario": {
            "id": user["rut_usuario"],
            "nombre": user["nombre"],
            "rol": user["rol"],
        },
    }
    
    # Si es una respuesta, incluir el contenido del mensaje original
    if msg.get("reply_to"):
        payload["reply_to"] = msg["reply_to"]
        try:
            original = model.obtener_mensaje_por_id(msg["reply_to"])
            if original:
                payload["reply_to_content"] = original.get("contenido", "")
        except Exception:
            pass
    
    return payload


# ============================================================
# 6. Funciones adicionales (Reacciones, Eliminar, Fijar)
# ============================================================

def agregar_reaccion_mensaje(mensaje_id, usuario_id, emoji):
    """Agrega una reacción a un mensaje."""
    return model.agregar_reaccion(mensaje_id, usuario_id, emoji)


def eliminar_mensaje(mensaje_id):
    """Elimina un mensaje."""
    return model.eliminar_mensaje_db(mensaje_id)


def fijar_mensaje(conversacion_id, mensaje_id):
    """Fija un mensaje en una conversación."""
    return model.fijar_mensaje_db(conversacion_id, mensaje_id)


def obtener_reacciones(mensaje_id):
    """Obtiene las reacciones de un mensaje."""
    return model.obtener_reacciones_mensaje(mensaje_id)

