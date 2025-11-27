
from flask import Blueprint, jsonify, session
from app.chat import chat_service as svc
from app.chat import chat_model as model
from app.utils.sesiones_activas import obtener_usuarios_conectados

bp_chat = Blueprint("chat_api", __name__, url_prefix="/api/chat")


# =============================================
# 1. Listar conversaciones recientes
# =============================================

@bp_chat.get("/conversaciones")
def chat_conversaciones():
    user = session.get("usuario_id")
    if not user:
        return jsonify({"success": False, "msg": "No autenticado"}), 401

    # Todas las conversaciones donde participa este usuario
    parts = model.obtener_conversaciones_de_usuario(user)

    # usuarios conectados (timeout 5 minutos para ser más tolerante)
    conectados, detalles = obtener_usuarios_conectados(timeout_minutos=5)
    conectados_set = set(conectados or [])

    lista = []
    for conv in parts:
        cid = conv["id"]

        # participantes
        miembros = model.obtener_participantes(cid)
        otro = [m for m in miembros if m != user][0] if len(miembros) == 2 else None

        info_otro = model.obtener_usuario(otro) if otro else None
        if not info_otro:
            # Si no hay datos del otro participante, saltamos esta conversación para no romper la API
            continue

        # obtener último mensaje
        last = model.obtener_ultimo_mensaje(cid)

        unread = model.contar_no_leidos(cid, user)

        lista.append({
            "conversacion_id": cid,
            "usuario": info_otro,
            "ultimo_mensaje": last["contenido"] if last else "",
            "fecha": last["fecha_envio"] if last else conv.get("fecha_creacion"),
            "unread": unread,
            "is_online": bool(info_otro and info_otro.get("rut_usuario") in conectados_set)
        })

    # Ordenar
    lista.sort(key=lambda x: x["fecha"], reverse=True)

    return jsonify({
        "success": True,
        "lista": lista
    })
    

# =============================================
# 2. Historial con otro usuario
# =============================================

@bp_chat.get("/history/<rut_destino>")
def chat_historial(rut_destino):
    user = session.get("usuario_id")
    if not user:
        return jsonify({"success": False, "msg": "No autenticado"}), 401

    # Obtener o crear conversación
    conv = svc.obtener_o_crear_conversacion(user, rut_destino)

    cid = conv["id"]

    # Validación de acceso
    if not svc.usuario_puede_ver(cid, user):
        return jsonify({"success": False, "msg": "Sin acceso"}), 403

    mensajes = svc.obtener_historial(cid, limit=50)

    # Últimos vistos por cada participante
    last_seen_me = None
    last_seen_other = None
    try:
        part_me = model.obtener_participacion(cid, user)
        if part_me:
            last_seen_me = part_me.get("ultimo_mensaje_leido")
        part_other = model.obtener_participacion(cid, rut_destino)
        if part_other:
            last_seen_other = part_other.get("ultimo_mensaje_leido")
    except Exception:
        pass

    return jsonify({
        "success": True,
        "conversacion_id": cid,
        "mensajes": mensajes,
        "last_seen_me": last_seen_me,
        "last_seen_other": last_seen_other
    })

@bp_chat.get("/users")
def chat_list_users():
    user = session.get("usuario_id")
    if not user:
        return jsonify({"success": False, "msg": "No autenticado"}), 401

    usuarios = model.obtener_todos_usuarios()

    # excluir a tu propio usuario
    usuarios = [u for u in usuarios if u["rut_usuario"] != user]

    # usuarios conectados (timeout 5 minutos)
    conectados, detalles = obtener_usuarios_conectados(timeout_minutos=5)
    conectados_set = set(conectados or [])

    # Ordenar por nombre (simple y estable)
    usuarios.sort(key=lambda x: x["nombre"].lower())

    # Payload limpio
    data = [{
        "id": u["rut_usuario"],
        "nombre": u["nombre"],
        "rol": u["rol"],
        "is_online": u["rut_usuario"] in conectados_set,
        "ultima_actividad": detalles.get(u["rut_usuario"], {}).get("ultima_actividad") if detalles else None
    } for u in usuarios]

    return jsonify({
        "success": True,
        "usuarios": data
    })
