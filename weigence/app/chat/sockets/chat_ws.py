ws
from flask import session
from flask_socketio import SocketIO, emit, join_room, leave_room

from app.chat import chat_service as svc


socketio = None


# ============================================================
# INIT — debe ejecutarse en app/__init__.py
# ============================================================

def init_socketio(app):
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        logger=False,
        engineio_logger=False,
        async_mode="threading"  # simple y compatible
    )
    registrar_eventos()
    return socketio


# ============================================================
# 1. CONEXIÓN / DESCONEXIÓN
# ============================================================

def _get_user():
    return session.get("usuario_id")


def on_connect():
    user = _get_user()
    if not user:
        print("[WS] ❌ conexión denegada (sin sesión)")
        return False

    print(f"[WS] ✓ conectado: {user}")
    emit("ws_connected", {"usuario_id": user})


def on_disconnect():
    user = _get_user()
    print(f"[WS] ✂ desconectado: {user}")


# ============================================================
# 2. UNIRSE A UNA CONVERSACIÓN
# ============================================================

def on_join(data):
    user = _get_user()
    conv = data.get("conversacion_id")

    if not user or not conv:
        EmitError("Datos insuficientes")
        return

    if not svc.usuario_puede_ver(conv, user):
        EmitError("No perteneces a la conversación")
        return

    join_room(conv)
    print(f"[WS] 🚪 {user} entró a {conv}")
    emit("joined", {"conversacion_id": conv})


# ============================================================
# 3. ENVIAR MENSAJE
# ============================================================

def on_send(data):
    user = _get_user()
    conv = data.get("conversacion_id")
    txt = data.get("contenido")

    if not user or not conv or not txt:
        EmitError("Faltan datos")
        return

    try:
        msg = svc.enviar_mensaje_ws(usuario_id=user, conversacion_id=conv, contenido=txt)
    except Exception as e:
        print("[WS] ERROR SEND:", e)
        EmitError("No se pudo enviar el mensaje")
        return

    # Broadcast del mensaje
    socketio.emit(
        "mensaje_nuevo",
        msg,
        room=conv,
        include_self=True
    )

    print(f"[WS] 📩 mensaje en conv {conv} por {user}")


# ============================================================
# 4. MARCAR COMO LEÍDO
# ============================================================

def on_seen(data):
    user = _get_user()
    conv = data.get("conversacion_id")
    last = data.get("ultimo_id")

    if not user or not conv or not last:
        EmitError("Faltan datos")
        return

    try:
        svc.marcar_leido(conv, user, last)
    except Exception as e:
        print("[WS] ERROR SEEN:", e)
        EmitError("No se pudo marcar como leído")
        return

    socketio.emit(
        "mensaje_visto",
        {
            "conversacion_id": conv,
            "usuario_id": user,
            "ultimo_id": last
        },
        room=conv
    )

    print(f"[WS] 👀 visto conv {conv} por {user}")


# ============================================================
# 5. UTILIDAD
# ============================================================

def EmitError(msg):
    emit("error", {"msg": msg})


# ============================================================
# REGISTRO CENTRAL
# ============================================================

def registrar_eventos():
    if socketio is None:
        raise RuntimeError("SocketIO no inicializado. Llama primero a init_socketio(app).")
    socketio.on_event("connect", on_connect)
    socketio.on_event("disconnect", on_disconnect)
    socketio.on_event("join", on_join)
    socketio.on_event("send", on_send)
    socketio.on_event("seen", on_seen)

