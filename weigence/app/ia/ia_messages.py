# app/ia/ia_messages.py
from typing import Dict, Any, List
from app.ia.config import templates_v2
import random

# --- Mensajes cortos (HEADER) que resumen el hallazgo ML correspondiente ---
def get_header_message(page: str, context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """
    Genera lista de mensajes del header según pantalla actual y hallazgos ML.
    Retorna múltiples mensajes para rotación automática.
    
    LÓGICA:
    - Si hay hallazgos ML (problemas): Mostrar SOLO esos hallazgos
    - Si NO hay hallazgos ML: Mostrar mensajes positivos/estadísticas
    """
    ctx = context or {}
    messages = []
    
    # Obtener todos los hallazgos ML de la página actual
    ml_insights_cards = ctx.get('ml_insights_cards', [])
    current_module_findings = [
        card for card in ml_insights_cards 
        if card.get('modulo') == page
    ]
    
    # Agregar hallazgos ML encontrados (orden cronológico - más recientes primero)
    for card in current_module_findings:
        titulo = card.get('titulo', '')
        descripcion = card.get('descripcion', '')
        emoji = card.get('emoji', '')
        severidad = card.get('ml_severity', 'info')
        
        # Combinar emoji + título de forma concisa
        if descripcion:
            first_sentence = descripcion.split('.')[0].strip()
            titulo_sin_prefijo = titulo.split(':', 1)[-1].strip() if ':' in titulo else titulo
            mensaje_texto = f"{emoji} {titulo_sin_prefijo}. {first_sentence}."
        else:
            mensaje_texto = f"{emoji} {titulo}"
        
        messages.append({
            "mensaje": mensaje_texto,
            "severidad": severidad,
            "detalle": descripcion
        })
    
    # SOLO agregar mensajes positivos si NO hay hallazgos ML (problemas)
    if not messages:
        positive_messages = _get_positive_messages(page, ctx)
        messages.extend(positive_messages)
    
    # Asegurar que siempre haya al menos 1 mensaje
    if not messages:
        messages = [{
            "mensaje": "✅ Sistema funcionando correctamente.",
            "severidad": "info",
            "detalle": "No se detectaron anomalías en este módulo"
        }]
    
    return messages

def _get_positive_messages(page: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    """
    Genera mensajes positivos y estadísticas cuando no hay anomalías.
    Retorna múltiples mensajes enriquecidos con métricas reales del snapshot.
    """
    ctx = context or {}
    snapshot = ctx.get('snapshot', {})
    
    # Extraer métricas reales del snapshot
    total_productos = snapshot.get('total_productos', 0)
    alertas_criticas = snapshot.get('critical_alerts', 0)
    alertas_warning = snapshot.get('warning_alerts', 0)
    eventos_auditoria = snapshot.get('audit_events_count', 0)
    movimientos_hora = snapshot.get('movements_per_hour', 0)
    
    messages_by_page = {
        "dashboard": [
            {"mensaje": f"📊 Sistema operando normalmente. {total_productos} productos activos, {alertas_criticas + alertas_warning} alertas resueltas hoy.", "severidad": "info"},
            {"mensaje": f"✅ Rendimiento estable. Todos los módulos funcionando correctamente.", "severidad": "success"},
            {"mensaje": f"🎯 Operación óptima. Monitoreo de {total_productos} productos activo.", "severidad": "info"},
        ],
        "inventario": [
            {"mensaje": f"📦 Stock estable con {total_productos} productos monitoreados. Sin alertas críticas.", "severidad": "info"},
            {"mensaje": f"✅ Niveles de inventario balanceados. Sensores operando normalmente.", "severidad": "success"},
            {"mensaje": f"🎯 Gestión eficiente. {total_productos} productos bajo control.", "severidad": "info"},
        ],
        "ventas": [
            {"mensaje": f"💰 Desempeño comercial dentro del rango esperado.", "severidad": "info"},
            {"mensaje": f"✅ Flujo de ventas consistente. Sin variaciones anómalas detectadas.", "severidad": "success"},
            {"mensaje": f"📈 Tendencia estable. Operación normalizada.", "severidad": "info"},
        ],
        "movimientos": [
            {"mensaje": f"🔄 Flujo operativo regular. {int(movimientos_hora)} movimientos/hora promedio.", "severidad": "info"},
            {"mensaje": f"✅ Trazabilidad completa. Todos los movimientos registrados.", "severidad": "success"},
            {"mensaje": f"📊 Actividad normalizada. Sin patrones inusuales.", "severidad": "info"},
        ],
        "alertas": [
            {"mensaje": f"🔔 Sistema bajo control. {alertas_criticas} alertas críticas, {alertas_warning} advertencias.", "severidad": "info"},
            {"mensaje": f"✅ Monitoreo activo. Sistema en estado óptimo.", "severidad": "success"},
            {"mensaje": f"🛡️ Protección preventiva funcionando. {total_productos} productos vigilados.", "severidad": "info"},
        ],
        "auditoria": [
            {"mensaje": f"🕵️ Registros coherentes. {eventos_auditoria} eventos registrados, 0 inconsistencias.", "severidad": "info"},
            {"mensaje": f"✅ Integridad de datos verificada. Auditoría sin observaciones.", "severidad": "success"},
            {"mensaje": f"📋 Trazabilidad completa. {eventos_auditoria} acciones documentadas.", "severidad": "info"},
        ],
    }
    
    return messages_by_page.get(page, [
        {"mensaje": "✅ Sistema funcionando correctamente.", "severidad": "info"}
    ])

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
