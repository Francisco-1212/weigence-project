"""
Sistema centralizado de registro de errores en auditoría (Backend)
Permite registrar errores de Python en la tabla auditoria_eventos
"""
from datetime import datetime
from flask import session
from api.conexion_supabase import supabase
import logging
import traceback

logger = logging.getLogger(__name__)


def registrar_error_auditoria(
    mensaje: str,
    modulo: str = "backend",
    detalle: str = "",
    nivel: str = "error",
    exception: Exception = None,
    incluir_stacktrace: bool = False
):
    """
    Registra un error en la tabla auditoria_eventos de Supabase.
    
    Args:
        mensaje: Mensaje principal del error
        modulo: Módulo donde ocurrió (ej: 'ventas', 'usuarios', 'ia_ml', etc.)
        detalle: Información adicional del error
        nivel: Nivel de severidad ('error', 'warning', 'critical')
        exception: Objeto Exception de Python (opcional)
        incluir_stacktrace: Si True, incluye el stacktrace completo (solo para nivel critical)
    
    Returns:
        bool: True si se registró correctamente, False en caso de error
    """
    try:
        # Obtener usuario actual de la sesión
        usuario = "Sistema"
        try:
            if session.get("usuario_nombre"):
                usuario = session.get("usuario_nombre")
            elif session.get("usuario", {}).get("email"):
                usuario = session.get("usuario", {}).get("email")
        except Exception:
            pass  # Si no hay sesión disponible, usar "Sistema"
        
        # Construir detalle completo
        detalle_completo = detalle
        if exception:
            detalle_completo += f" | {type(exception).__name__}: {str(exception)}"
            
            # Incluir stacktrace solo para errores críticos
            if incluir_stacktrace and nivel == "critical":
                stack = traceback.format_exc()
                # Limitar tamaño del stacktrace
                detalle_completo += f" | Stack: {stack[:500]}"
        
        # Registrar en auditoría
        payload = {
            "fecha": datetime.now().isoformat(),
            "usuario": usuario,
            "accion": f"error_sistema_{nivel}",
            "detalle": f"[{modulo}] {mensaje}. {detalle_completo}".strip()
        }
        
        supabase.table("auditoria_eventos").insert(payload).execute()
        
        # Log adicional en consola del servidor
        log_msg = f"[AUDITORIA-ERROR] [{modulo}] {mensaje}"
        if nivel == "critical":
            logger.error(log_msg, exc_info=exception is not None)
        elif nivel == "warning":
            logger.warning(log_msg)
        else:
            logger.error(log_msg)
        
        return True
        
    except Exception as e:
        # Error al registrar en auditoría, solo log local
        logger.error(f"[AUDITORIA] Error al registrar error en auditoría: {e}")
        return False


def registrar_error_critico(mensaje: str, modulo: str, exception: Exception = None):
    """Atajo para registrar errores críticos con stacktrace"""
    return registrar_error_auditoria(
        mensaje=mensaje,
        modulo=modulo,
        nivel="critical",
        exception=exception,
        incluir_stacktrace=True
    )


def registrar_error_warning(mensaje: str, modulo: str, detalle: str = ""):
    """Atajo para registrar advertencias"""
    return registrar_error_auditoria(
        mensaje=mensaje,
        modulo=modulo,
        detalle=detalle,
        nivel="warning"
    )


def registrar_error(mensaje: str, modulo: str, exception: Exception = None):
    """Atajo para registrar errores normales"""
    return registrar_error_auditoria(
        mensaje=mensaje,
        modulo=modulo,
        nivel="error",
        exception=exception
    )
