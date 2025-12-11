from flask import session
from flask_socketio import SocketIO, emit, join_room
import logging

from app.chat import chat_service as svc

socketio = None
logger = logging.getLogger(__name__)


# ============================================================
# INIT - called from app/__init__.py
# ============================================================

def init_socketio(app):
    """Inicializa SocketIO y registra eventos."""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        logger=False,
        engineio_logger=False,
        async_mode="threading",  # simple y compatible
        ping_timeout=60,
        ping_interval=25,
        max_http_buffer_size=1000000,
        allow_upgrades=True,
        transports=['websocket', 'polling'],
        # Configuraciones adicionales para manejar sesiones inválidas
        always_connect=False,  # No auto-conectar sesiones inválidas
        manage_session=True,  # Flask-SocketIO maneja sesiones Flask
        cookie=None  # Usar cookies de Flask por defecto
    )
    registrar_eventos()
    return socketio


# ============================================================
# 1. CONEXION / DESCONEXION
# ============================================================

def _get_user():
    return session.get("usuario_id")


def on_connect():
    """Maneja la conexión WebSocket con validación de sesión."""
    try:
        user = _get_user()
        if not user:
            print("[WS] conexion denegada (sin sesion)")
            return False

        print(f"[WS] usuario conectado: {user}")
        emit("ws_connected", {"usuario_id": user})
    except Exception as e:
        print(f"[WS ERROR] Error en on_connect: {e}")
        return False


def on_disconnect():
    """Maneja la desconexión WebSocket de forma segura."""
    try:
        user = _get_user()
        print(f"[WS] usuario desconectado: {user}")
    except Exception as e:
        print(f"[WS ERROR] Error en on_disconnect: {e}")


# ============================================================
# 2. UNIRSE A UNA CONVERSACION
# ============================================================

def on_join(data):
    if not isinstance(data, dict):
        _emit_error("Datos insuficientes")
        return

    user = _get_user()
    conv = data.get("conversacion_id")
    if not user or not conv:
        _emit_error("Datos insuficientes")
        return

    conv_str = str(conv)
    if not svc.usuario_puede_ver(conv_str, user):
        _emit_error("No perteneces a la conversacion")
        return

    join_room(conv_str)
    print(f"[WS] usuario {user} entro a {conv_str}")
    emit("joined", {"conversacion_id": conv_str})


# ============================================================
# 3. ENVIAR MENSAJE
# ============================================================

def on_send(data):
    if not isinstance(data, dict):
        _emit_error("Faltan datos")
        return

    user = _get_user()
    conv = data.get("conversacion_id")
    txt = data.get("contenido")
    reply_to = data.get("reply_to")  # Capturar reply_to del mensaje
    
    if not user or not conv or not txt:
        _emit_error("Faltan datos")
        return

    try:
        conv_str = str(conv)
        msg = svc.enviar_mensaje_ws(usuario_id=user, conversacion_id=conv_str, contenido=str(txt), reply_to=reply_to)
        
        # Si tiene reply_to, agregar contexto del mensaje original
        if reply_to and msg.get("id"):
            try:
                from app.chat import chat_model as model
                original = model.supabase.table("chat_mensajes")\
                    .select("contenido, usuario_id, usuarios_conectados(nombre)")\
                    .eq("id", reply_to)\
                    .single()\
                    .execute()
                
                if original.data:
                    msg["reply_to"] = reply_to
                    msg["reply_to_content"] = original.data.get("contenido")
                    msg["reply_to_user_id"] = original.data.get("usuario_id")
                    if original.data.get("usuarios_conectados"):
                        msg["reply_to_user_name"] = original.data["usuarios_conectados"].get("nombre")
            except Exception as e:
                print(f"[WS] Error obteniendo contexto de reply: {e}")
                # Enviar al menos el reply_to aunque falle obtener el contexto
                if reply_to:
                    msg["reply_to"] = reply_to
                    
    except Exception as e:
        print("[WS] ERROR SEND:", e)
        _emit_error("No se pudo enviar el mensaje")
        return

    socketio.emit(
        "mensaje_nuevo",
        msg,
        room=conv_str,
        include_self=True,
    )

    print(f"[WS] mensaje en conv {conv_str} por {user}")


# ============================================================
# 4. MARCAR COMO LEIDO
# ============================================================

def on_seen(data):
    if not isinstance(data, dict):
        _emit_error("Faltan datos")
        return

    user = _get_user()
    conv = data.get("conversacion_id")
    last = data.get("ultimo_id")
    if not user or not conv or last is None:
        _emit_error("Faltan datos")
        return

    try:
        conv_str = str(conv)
        last_id = int(last)
        svc.marcar_leido(conv_str, user, last_id)
    except Exception as e:
        print("[WS] ERROR SEEN:", e)
        _emit_error("No se pudo marcar como leido")
        return

    socketio.emit(
        "mensaje_visto",
        {
            "conversacion_id": conv_str,
            "usuario_id": user,
            "ultimo_id": last_id,
        },
        room=conv_str,
    )

    print(f"[WS] visto conv {conv_str} por {user}")


# ============================================================
# 5. UTILIDAD
# ============================================================

def _emit_error(msg):
    emit("error", {"msg": msg})


# ============================================================
# 6. MANEJADOR GLOBAL DE ERRORES
# ============================================================

def on_error_default(e):
    """Maneja errores globales de SocketIO de forma silenciosa."""
    # Suprimir errores de sesiones inválidas (muy comunes cuando usuarios refrescan)
    error_msg = str(e).lower()
    if "invalid session" in error_msg or "session not found" in error_msg:
        logger.debug(f"[WS] Sesión inválida detectada (ignorada): {e}")
    else:
        logger.error(f"[WS ERROR] Error SocketIO: {e}")


# ============================================================
# REGISTRO CENTRAL
# ============================================================

def registrar_eventos():
    if socketio is None:
        raise RuntimeError("SocketIO no inicializado. Llama primero a init_socketio(app).")
    
    # Registrar eventos principales
    socketio.on_event("connect", on_connect)
    socketio.on_event("disconnect", on_disconnect)
    socketio.on_event("join", on_join)
    socketio.on_event("send", on_send)
    socketio.on_event("seen", on_seen)
    
    # Registrar manejador global de errores
    socketio.on_error_default(on_error_default)
