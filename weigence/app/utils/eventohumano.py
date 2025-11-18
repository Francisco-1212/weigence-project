from datetime import datetime, timezone
from flask import session
from api.conexion_supabase import supabase
import logging

logger = logging.getLogger(__name__)

def registrar_evento_humano(accion: str, detalle: str = ""):
    """
    Registra eventos generados por usuarios (login, logout, navegación, exportación, acciones manuales, etc.).
    Guarda en la tabla auditoria_eventos de Supabase.
    """
    try:
        usuario = (
            session.get("usuario_nombre") 
            or session.get("usuario_id") 
            or "desconocido"
        )
        
        # Insertar en la tabla auditoria_eventos
        payload = {
            "fecha": datetime.now(timezone.utc).isoformat(),
            "usuario": usuario,
            "accion": accion,
            "detalle": detalle or accion
        }
        
        resultado = supabase.table("auditoria_eventos").insert(payload).execute()
        
        logger.info(f"[AUDITORIA] ✓ Evento registrado: {accion} - {detalle} (Usuario: {usuario})")
        return True

    except Exception as e:
        logger.error(f"[AUDITORIA] ✗ Error registrando evento humano: {e}", exc_info=True)
        return False
