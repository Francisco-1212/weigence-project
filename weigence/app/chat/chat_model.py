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
            .single()
            .execute()
        )
        return r.data
    except APIError:
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
            .single()
            .execute()
        )
        return r.data
    except APIError:
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


def insertar_mensaje(conversacion_id, usuario_id, contenido):
    r = (
        supabase.table("chat_mensajes")
        .insert(
            {
                "conversacion_id": conversacion_id,
                "usuario_id": usuario_id,
                "contenido": contenido,
            }
        )
        .execute()
    )
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
            .single()
            .execute()
        )
        return bool(r.data)
    except APIError:
        return False


def obtener_participacion(conversacion_id, usuario_id):
    try:
        r = (
            supabase.table("chat_participantes")
            .select("ultimo_mensaje_leido")
            .eq("conversacion_id", conversacion_id)
            .eq("usuario_id", usuario_id)
            .single()
            .execute()
        )
        return r.data
    except APIError:
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
        )
        if last_seen:
            query = query.gt("id", last_seen)
        res = query.execute()
    except APIError:
        return 0

    if not res.data:
        return 0

    return len([m for m in res.data if m.get("usuario_id") != usuario_id])


def obtener_todos_usuarios():
    r = supabase.table("usuarios").select("rut_usuario, nombre, rol").execute()
    return r.data or []
