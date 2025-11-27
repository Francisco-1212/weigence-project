
from flask import Blueprint, jsonify, session, request
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


# =============================================
# 3. Enviar mensaje (HTTP - fallback cuando no hay WS)
# =============================================

@bp_chat.post("/send")
def chat_enviar_mensaje():
    user = session.get("usuario_id")
    if not user:
        return jsonify({"success": False, "msg": "No autenticado"}), 401

    payload = request.get_json(silent=True) or {}
    contenido = (payload.get("contenido") or "").strip()
    conversacion_id = payload.get("conversacion_id")
    destinatario_id = payload.get("destinatario_id") or payload.get("rut_destino")

    if not contenido:
        return jsonify({"success": False, "msg": "Mensaje vacio"}), 400

    try:
        # Prefiere flujo por destinatario para garantizar que la conversacion exista
        if destinatario_id:
            res = svc.enviar_mensaje(user_id=user, destinatario_id=destinatario_id, contenido=contenido)
            conv_id = str(res["conversacion_id"])
            msg = res["mensaje"]
        elif conversacion_id is not None:
            try:
                conv_int = int(conversacion_id)
            except (TypeError, ValueError):
                return jsonify({"success": False, "msg": "conversacion_id invalido"}), 400

            msg = svc.guardar_mensaje(conv_int, user, contenido)
            conv_id = str(conv_int)
        else:
            return jsonify({"success": False, "msg": "Falta destinatario"}), 400
    except PermissionError:
        return jsonify({"success": False, "msg": "Sin acceso a la conversacion"}), 403
    except ValueError as e:
        return jsonify({"success": False, "msg": str(e)}), 400
    except Exception as e:
        # Registramos para depurar errores de Supabase o datos
        try:
            from flask import current_app
            if current_app:
                current_app.logger.error(f"[CHAT_API_SEND] Error enviando mensaje: {e}", exc_info=True)
        except Exception:
            pass
        return jsonify({"success": False, "msg": "No se pudo enviar el mensaje"}), 500

    # Intentar emitir por WS si hay clientes conectados a la sala
    try:
        from app import socketio_instance

        if socketio_instance:
            socketio_instance.emit("mensaje_nuevo", msg, to=conv_id)
    except Exception:
        pass

    return jsonify({
        "success": True,
        "conversacion_id": conv_id,
        "mensaje": msg,
    })
