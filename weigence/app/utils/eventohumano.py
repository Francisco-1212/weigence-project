from datetime import datetime, timezone
from flask import session
from api.conexion_supabase import supabase

def registrar_evento_humano(accion: str, detalle: str = ""):
    """
    Registra eventos generados por usuarios (navegación, exportación, acciones manuales, etc.).
    """
    try:
        usuario = (
            session.get("usuario_nombre") 
            or session.get("usuario_id") 
            or "desconocido"
        )

        supabase.table("auditoria_eventos").insert({
            "fecha": datetime.now(timezone.utc).isoformat(),
            "usuario": usuario,
            "accion": accion,
            "detalle": detalle,
        }).execute()

    except Exception as e:
        print("[AUDITORIA] Error registrando evento humano:", e)
