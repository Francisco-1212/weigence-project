# app/ia/ia_messages.py
from typing import Dict, Any
from app.ia.config import templates_v2

# --- Mensajes cortos (HEADER) que resumen el hallazgo ML correspondiente ---
def get_header_message(page: str, context: Dict[str, Any] | None = None) -> str:
    """
    Genera mensaje del header según pantalla actual y hallazgos ML.
    El mensaje debe ser contextual a la página y resumir el hallazgo principal.
    """
    ctx = context or {}
    
    # Obtener hallazgo ML de la página actual (si existe)
    ml_insights_cards = ctx.get('ml_insights_cards', [])
    current_module_finding = None
    
    # Buscar hallazgo correspondiente a la página actual
    for card in ml_insights_cards:
        if card.get('modulo') == page:
            current_module_finding = card
            break
    
    # Si hay un hallazgo ML específico para este módulo, usarlo
    if current_module_finding:
        titulo = current_module_finding.get('titulo', '')
        descripcion = current_module_finding.get('descripcion', '')
        emoji = current_module_finding.get('emoji', '')
        
        # Combinar emoji + título + descripción de forma concisa
        if descripcion:
            # Tomar primera oración de la descripción (hasta el primer punto)
            first_sentence = descripcion.split('.')[0].strip()
            # Quitar el prefijo del módulo del título (ej: "Ventas: " → "")
            titulo_sin_prefijo = titulo.split(':', 1)[-1].strip() if ':' in titulo else titulo
            return f"{emoji} {titulo_sin_prefijo}. {first_sentence}."
        return f"{emoji} {titulo}"
    
    # Mensajes por defecto si no hay hallazgo ML
    default_messages = {
        "dashboard": "📊 Sistema operando normalmente. Sin anomalías detectadas.",
        "inventario": "📦 Stock y sensores estables. Sin alertas críticas de inventario.",
        "ventas": "💰 Desempeño comercial dentro del rango esperado.",
        "movimientos": "🔄 Flujo operativo regular. Sin inactividad prolongada.",
        "alertas": "🔔 Sistema de monitoreo bajo control. Sin emergencias activas.",
        "auditoria": "🕵️ Registros coherentes. Sin inconsistencias detectadas.",
    }
    
    return default_messages.get(page, "✅ Sistema funcionando correctamente.")

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
