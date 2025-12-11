# app/ia/ia_messages.py
from typing import Dict, Any, List
from app.ia.config import templates_v2
import random

def _formato_tiempo_inactividad(horas: float) -> str:
    """Formatea el tiempo de inactividad en un mensaje legible."""
    if horas < 1:
        minutos = int(horas * 60)
        if minutos == 0:
            return "Movimiento registrado hace instantes"
        return f"Sin movimientos hace {minutos} minuto{'s' if minutos != 1 else ''}"
    elif horas < 24:
        horas_int = int(horas)
        return f"Sin movimientos hace {horas_int} hora{'s' if horas_int != 1 else ''}"
    else:
        dias = int(horas / 24)
        return f"⚠️ Sin movimientos hace {dias} día{'s' if dias != 1 else ''}"

# --- Mensajes cortos (HEADER) con métricas del sistema ---
def get_header_message(page: str, context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Genera lista de mensajes del header con métricas operacionales del sistema.
    Retorna exactamente 2 mensajes por módulo con información accionable.
    
    LÓGICA:
    - Siempre muestra métricas reales del sistema (stock, alertas, ventas, etc.)
    - 2 mensajes por pantalla con información esencial y accionable
    """
    ctx = context or {}
    messages = _get_positive_messages(page, ctx)
    
    # Asegurar que siempre haya al menos 1 mensaje
    if not messages:
        messages = [{
            "mensaje": "📊 Sistema operativo",
            "severidad": "info"
        }]
    
    return messages

def _get_positive_messages(page: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Genera mensajes accionables y específicos con métricas reales del sistema.
    Siempre incluye información útil, no solo mensajes positivos genéricos.
    """
    ctx = context or {}
    snapshot = ctx.get('snapshot', {})
    
    # Extraer métricas reales del snapshot
    total_productos = snapshot.get('total_productos', 0)
    productos_sin_stock = snapshot.get('productos_sin_stock', 0)
    
    # Extraer alertas del summary
    alerts_summary = snapshot.get('alerts_summary', {})
    alertas_criticas = alerts_summary.get('critical', 0)
    alertas_warning = alerts_summary.get('warning', 0)
    alertas_info = alerts_summary.get('info', 0)
    alertas_pendientes = alertas_criticas + alertas_warning + alertas_info
    eventos_auditoria = snapshot.get('audit_events_count', 0)
    movimientos_hora = snapshot.get('movements_per_hour', 0)
    ventas_24h = snapshot.get('ventas_ultimas_24h', 0)
    movimientos_no_justificados = snapshot.get('movimientos_no_justificados', 0)
    usuarios_actividad_sospechosa = snapshot.get('usuarios_sospechosos', 0)
    
    # Extraer métricas adicionales
    estantes_sobrecargados = snapshot.get('estantes_sobrecargados', 0)
    productos_no_encontrados = snapshot.get('productos_no_encontrados_movimientos', 0)
    
    print(f"[DEBUG MESSAGES] ========================================")
    print(f"[DEBUG MESSAGES] Page: {page}")
    print(f"[DEBUG MESSAGES] Alertas - Críticas: {alertas_criticas}, Advertencias: {alertas_warning}, Total pendientes: {alertas_pendientes}")
    print(f"[DEBUG MESSAGES] productos_no_encontrados_movimientos: {productos_no_encontrados}")
    print(f"[DEBUG MESSAGES] estantes_sobrecargados: {estantes_sobrecargados}")
    print(f"[DEBUG MESSAGES] ========================================")
    
    messages_by_page = {
        "dashboard": [
            {"mensaje": f" Stock estable: {total_productos} productos en inventario{f', {productos_sin_stock} sin stock' if productos_sin_stock > 0 else ''}", "severidad": "info" if productos_sin_stock == 0 else "warning"},
            {"mensaje": f" {alertas_pendientes} alertas {'pendientes' if alertas_pendientes > 0 else 'resueltas'} ({alertas_criticas} críticas, {alertas_warning} advertencias)", "severidad": "warning" if alertas_pendientes > 0 else "success"},
        ],
        "inventario": [
            {"mensaje": f" {total_productos} productos en inventario{f' - {productos_sin_stock} sin stock' if productos_sin_stock > 0 else ' - Stock completo'}", "severidad": "warning" if productos_sin_stock > 0 else "success"},
            {"mensaje": f" {estantes_sobrecargados} estantes sobrecargados{' - Redistribuir carga' if estantes_sobrecargados > 0 else ' - Capacidad normal'}", "severidad": "warning" if estantes_sobrecargados > 0 else "info"},
        ],
        "ventas": [
            {"mensaje": f"💰 Ventas {'estables' if ventas_24h >= 30 else 'bajas'}: {ventas_24h} ventas en las últimas 24h", "severidad": "info" if ventas_24h >= 30 else "warning"},
        ],
        "movimientos": [
            {"mensaje": f"❓ {productos_no_encontrados} movimientos de productos no encontrados{' - Revisar registros' if productos_no_encontrados > 0 else ''}", "severidad": "warning" if productos_no_encontrados > 0 else "success"},
        ],
        "alertas": [
            {"mensaje": f"🔔 {alertas_pendientes} alertas pendientes - {'Atención urgente' if alertas_criticas > 0 else 'Revisar cuando sea posible'}", "severidad": "critical" if alertas_criticas > 0 else "warning" if alertas_pendientes > 0 else "success"},
            {"mensaje": f"⚠️ {alertas_criticas} críticas, {alertas_warning} advertencias{' - Priorizar críticas' if alertas_criticas > 0 else ''}", "severidad": "warning" if alertas_pendientes > 0 else "info"},
        ],
        "auditoria": [
            {"mensaje": f"🕵️ {usuarios_actividad_sospechosa} usuarios con actividad sospechosa{' - Revisar logs' if usuarios_actividad_sospechosa > 0 else ''}", "severidad": "warning" if usuarios_actividad_sospechosa > 0 else "success"},
            {"mensaje": f"📋 {eventos_auditoria} eventos registrados - {'Revisar inconsistencias' if movimientos_no_justificados > 0 else 'Registros coherentes'}", "severidad": "warning" if movimientos_no_justificados > 0 else "info"},
        ],
    }
    
    # Si la página no está en el diccionario, imprimir advertencia y usar dashboard como fallback
    if page not in messages_by_page:
        print(f"[DEBUG MESSAGES] ⚠️ Página '{page}' no tiene mensajes definidos, usando dashboard como fallback")
        return messages_by_page.get("dashboard", [
            {"mensaje": f"📊 Sistema operativo - {total_productos} productos monitoreados", "severidad": "info"}
        ])
    
    return messages_by_page[page]

# --- Mensajes largos (AUDITORÍA u otros bloques extensos) ---
def get_detailed_message(page: str, context: Dict[str, Any] | None = None) -> Dict[str, str]:
    ctx = context or {}
    catalogo = {
        "dashboard":   templates_v2.DASHBOARD_TEMPLATES,
        "inventario":  templates_v2.INVENTORY_TEMPLATES,
        "ventas":      templates_v2.SALES_TEMPLATES,
        "movimientos": templates_v2.MOVEMENTS_TEMPLATES,
        "alertas":     templates_v2.ALERTS_TEMPLATES,
        "auditoria":   templates_v2.AUDIT_TEMPLATES,
    }.get(page, templates_v2.AUDIT_TEMPLATES)

    clave = list(catalogo.keys())[0] if catalogo else 'default'
    tpl = catalogo.get(clave, {})

    out = {}
    for k, v in tpl.items():
        try:
            out[k] = v.format(**ctx)
        except Exception:
            out[k] = v
    out["plantilla_usada"] = clave
    return out
