from api.conexion_supabase import supabase
try:
    from postgrest.exceptions import APIError
except ImportError:
    APIError = Exception


# ============================================================
# 1. USUARIOS
# ============================================================

def obtener_usuario(rut):
    try:
        r = (
            supabase.table("usuarios")
            .select("rut_usuario, nombre, rol")
            .eq("rut_usuario", rut)
            .execute()
        )
        return r.data[0] if r.data else None
    except (APIError, IndexError):
        return None


# ============================================================
# 2. CONVERSACIONES
# ============================================================

def obtener_conversacion_por_id(conv_id):
    try:
        r = (
            supabase.table("chat_conversaciones")
            .select("*")
            .eq("id", conv_id)
            .execute()
        )
        return r.data[0] if r.data else None
    except (APIError, IndexError):
        return None


def obtener_conversacion_entre_usuarios(user1, user2):
    """Busca una conversacion existente entre user1 y user2."""
    try:
        r = (
            supabase.table("chat_participantes")
            .select("conversacion_id, usuario_id")
            .in_("usuario_id", [user1, user2])
            .execute()
        )
    except APIError:
        return None

    if not r.data:
        return None

    conteo = {}
    for row in r.data:
        cid = row["conversacion_id"]
        conteo[cid] = conteo.get(cid, 0) + 1

    comunes = [cid for cid, n in conteo.items() if n == 2]
    if not comunes:
        return None

    return obtener_conversacion_por_id(comunes[0])


def crear_conversacion(user1, user2):
    conv = supabase.table("chat_conversaciones").insert({}).execute()
    conv_id = conv.data[0]["id"]

    supabase.table("chat_participantes").insert(
        [
            {"conversacion_id": conv_id, "usuario_id": user1},
            {"conversacion_id": conv_id, "usuario_id": user2},
        ]
    ).execute()

    return conv.data[0]


# ============================================================
# 3. MENSAJES
# ============================================================

def obtener_mensajes(conversacion_id, limit=50):
    r = (
        supabase.table("chat_mensajes")
        .select("*")
        .eq("conversacion_id", conversacion_id)
        .order("fecha_envio", desc=True)
        .limit(limit)
        .execute()
    )
    if not r.data:
        return []
    return list(reversed(r.data))


def insertar_mensaje(conversacion_id, usuario_id, contenido, reply_to=None):
    data = {
        "conversacion_id": conversacion_id,
        "usuario_id": usuario_id,
        "contenido": contenido,
    }
    
    if reply_to:
        data["reply_to"] = reply_to
    
    r = supabase.table("chat_mensajes").insert(data).execute()
    return r.data[0]


# ============================================================
# 4. PARTICIPANTES / PERMISOS
# ============================================================

def obtener_participantes(conversacion_id):
    try:
        r = (
            supabase.table("chat_participantes")
            .select("usuario_id")
            .eq("conversacion_id", conversacion_id)
            .execute()
        )
    except APIError:
        return []

    if not r.data:
        return []
    return [p["usuario_id"] for p in r.data]


def validar_usuario_en_conversacion(conversacion_id, usuario_id):
    try:
        r = (
            supabase.table("chat_participantes")
            .select("id")
            .eq("conversacion_id", conversacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(r.data and len(r.data) > 0)
    except APIError:
        return False


def obtener_participacion(conversacion_id, usuario_id):
    try:
        r = (
            supabase.table("chat_participantes")
            .select("ultimo_mensaje_leido")
            .eq("conversacion_id", conversacion_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return r.data[0] if r.data else None
    except (APIError, IndexError):
        return None


def marcar_mensajes_leidos(conversacion_id, usuario_id, ultimo_mensaje_id):
    supabase.table("chat_participantes").update(
        {"ultimo_mensaje_leido": ultimo_mensaje_id}
    ).eq("conversacion_id", conversacion_id).eq("usuario_id", usuario_id).execute()


def obtener_conversaciones_de_usuario(rut):
    try:
        r = (
            supabase.table("chat_conversaciones")
            .select("*")
            .order("ultimo_mensaje_timestamp", desc=True)
            .execute()
        )
    except APIError:
        return []

    if not r.data:
        return []

    return [conv for conv in r.data if validar_usuario_en_conversacion(conv["id"], rut)]


def obtener_conversaciones_optimizado(usuario_id):
    """Obtiene conversaciones con todos los datos necesarios en una sola consulta optimizada."""
    try:
        # Obtener conversaciones donde participa el usuario
        participaciones = (
            supabase.table("chat_participantes")
            .select("conversacion_id, ultimo_mensaje_leido")
            .eq("usuario_id", usuario_id)
            .execute()
        )
        
        if not participaciones.data:
            return []
        
        conv_ids = [p["conversacion_id"] for p in participaciones.data]
        ultimo_leido_map = {p["conversacion_id"]: p["ultimo_mensaje_leido"] for p in participaciones.data}
        
        # Obtener todos los participantes de esas conversaciones
        todos_participantes = (
            supabase.table("chat_participantes")
            .select("conversacion_id, usuario_id")
            .in_("conversacion_id", conv_ids)
            .execute()
        )
        
        # Mapear participantes por conversación
        participantes_map = {}
        for p in todos_participantes.data:
            cid = p["conversacion_id"]
            if cid not in participantes_map:
                participantes_map[cid] = []
            participantes_map[cid].append(p["usuario_id"])
        
        # Obtener todos los últimos mensajes de esas conversaciones
        mensajes = (
            supabase.table("chat_mensajes")
            .select("*")
            .in_("conversacion_id", conv_ids)
            .order("fecha_envio", desc=False)
            .execute()
        )
        
        # Agrupar mensajes por conversación (solo el último)
        ultimos_mensajes = {}
        mensajes_no_leidos = {}
        
        for msg in mensajes.data:
            cid = msg["conversacion_id"]
            ultimos_mensajes[cid] = msg
            
            # Contar no leídos
            if msg["usuario_id"] != usuario_id:
                ultimo_leido = ultimo_leido_map.get(cid)
                if not ultimo_leido or msg["id"] > ultimo_leido:
                    mensajes_no_leidos[cid] = mensajes_no_leidos.get(cid, 0) + 1
        
        # Obtener info de todos los usuarios de una vez
        otros_usuarios_ids = []
        for cid, miembros in participantes_map.items():
            otros = [m for m in miembros if m != usuario_id]
            otros_usuarios_ids.extend(otros)
        
        otros_usuarios_ids = list(set(otros_usuarios_ids))
        
        usuarios_info = {}
        if otros_usuarios_ids:
            usuarios_data = (
                supabase.table("usuarios")
                .select("rut_usuario, nombre, rol")
                .in_("rut_usuario", otros_usuarios_ids)
                .execute()
            )
            usuarios_info = {u["rut_usuario"]: u for u in usuarios_data.data}
        
        # Construir resultado
        resultado = []
        for cid in conv_ids:
            miembros = participantes_map.get(cid, [])
            otros = [m for m in miembros if m != usuario_id]
            
            if not otros:
                continue
            
            otro_id = otros[0]
            info_otro = usuarios_info.get(otro_id)
            
            if not info_otro:
                continue
            
            ultimo_msg = ultimos_mensajes.get(cid)
            unread = mensajes_no_leidos.get(cid, 0)
            
            resultado.append({
                "conversacion_id": cid,
                "usuario": info_otro,
                "ultimo_mensaje": ultimo_msg["contenido"] if ultimo_msg else "",
                "fecha": ultimo_msg["fecha_envio"] if ultimo_msg else None,
                "unread": unread,
                "is_online": False  # Se actualiza después
            })
        
        return resultado
        
    except Exception as e:
        print(f"[CHAT_MODEL] Error en obtener_conversaciones_optimizado: {e}")
        return []


def obtener_ultimo_mensaje(conversacion_id):
    r = (
        supabase.table("chat_mensajes")
        .select("*")
        .eq("conversacion_id", conversacion_id)
        .order("fecha_envio", desc=True)
        .limit(1)
        .execute()
    )
    return r.data[0] if r.data else None


def contar_no_leidos(conversacion_id, usuario_id):
    part = obtener_participacion(conversacion_id, usuario_id)
    last_seen = part.get("ultimo_mensaje_leido") if part else None

    try:
        query = (
            supabase.table("chat_mensajes")
            .select("id, usuario_id")
            .eq("conversacion_id", conversacion_id)
            .neq("usuario_id", usuario_id)  # Solo mensajes del otro usuario
        )
        
        if last_seen:
            # Si ya hay un último mensaje leído, contar solo los posteriores
            query = query.gt("id", last_seen)
        else:
            # Si es primera vez (nunca ha leído nada), retornar 0
            # Los mensajes se marcarán como leídos cuando abra el chat
            return 0
            
        res = query.execute()
    except APIError:
        return 0

    if not res.data:
        return 0

    return len(res.data)


def obtener_todos_usuarios():
    r = supabase.table("usuarios").select("rut_usuario, nombre, rol").execute()
    return r.data or []


# ============================================================
# 5. FUNCIONES ADICIONALES (Reacciones, Eliminar, Fijar)
# ============================================================

def obtener_mensaje_por_id(mensaje_id):
    """Obtiene un mensaje específico por su ID."""
    try:
        r = (
            supabase.table("chat_mensajes")
            .select("*")
            .eq("id", mensaje_id)
            .execute()
        )
        return r.data[0] if r.data else None
    except (APIError, IndexError):
        return None


def agregar_reaccion(mensaje_id, usuario_id, emoji):
    """Agrega o actualiza una reacción a un mensaje."""
    try:
        # Verificar si ya existe una reacción de este usuario
        r = (
            supabase.table("chat_reacciones")
            .select("*")
            .eq("mensaje_id", mensaje_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        
        if r.data:
            # Actualizar reacción existente
            supabase.table("chat_reacciones").update(
                {"emoji": emoji}
            ).eq("mensaje_id", mensaje_id).eq("usuario_id", usuario_id).execute()
        else:
            # Insertar nueva reacción
            supabase.table("chat_reacciones").insert({
                "mensaje_id": mensaje_id,
                "usuario_id": usuario_id,
                "emoji": emoji
            }).execute()
        
        return True
    except Exception as e:
        print(f"[CHAT_MODEL] Error agregando reacción: {e}")
        return False


def eliminar_mensaje_db(mensaje_id):
    """Elimina un mensaje de la base de datos."""
    try:
        supabase.table("chat_mensajes").delete().eq("id", mensaje_id).execute()
        return True
    except Exception as e:
        print(f"[CHAT_MODEL] Error eliminando mensaje: {e}")
        return False


def fijar_mensaje_db(conversacion_id, mensaje_id):
    """Marca un mensaje como fijado en una conversación."""
    try:
        # Actualizar la conversación con el mensaje fijado
        supabase.table("chat_conversaciones").update(
            {"mensaje_fijado_id": mensaje_id}
        ).eq("id", conversacion_id).execute()
        return True
    except Exception as e:
        print(f"[CHAT_MODEL] Error fijando mensaje: {e}")
        return False


def obtener_reacciones_mensaje(mensaje_id):
    """Obtiene todas las reacciones de un mensaje."""
    try:
        r = (
            supabase.table("chat_reacciones")
            .select("*")
            .eq("mensaje_id", mensaje_id)
            .execute()
        )
        return r.data or []
    except APIError:
        return []

