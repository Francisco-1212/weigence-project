# app/ia/ia_messages.py
from typing import Dict, Any
import random
from app.ia.config import templates_v2

# --- Mensajes cortos (HEADER) ---
_HEADER_MESSAGES = {
    "dashboard": [
        "Estabilidad general. {n_alerts} alertas activas.",
        "Indicadores en rango normal. {n_alerts} alertas en seguimiento.",
        "Sin incidencias críticas. Operación estable."
    ],
    "inventario": [
        "Inventario estable. Críticas: {critical_alerts}, advertencias: {warning_alerts}.",
        "Variación de peso {weight_change_rate:.2%} vs. día anterior.",
        "Flujo de reposición regular en estantes."
    ],
    "ventas": [
        "Tendencia de ventas {sales_trend_percent:.1%} vs. histórico.",
        "Volatilidad controlada ({sales_volatility:.2f}).",
        "Desempeño comercial dentro del rango esperado."
    ],
    "movimientos": [
        "{movements_per_hour:.2f} movimientos/h. Inactividad {inactivity_hours:.1f} h.",
        "Flujo operativo regular y sin bloqueos.",
        "Actividad consistente. Sin inactividad extendida."
    ],
    "alertas": [
        "{critical_alerts} críticas y {warning_alerts} advertencias activas.",
        "Monitoreo constante. Sin nuevas incidencias graves.",
        "Condición general bajo control."
    ],
    "auditoria": [
        "Auditoría estable. Sin hallazgos críticos.",
        "Registros coherentes y controles validados.",
        "Sistema consistente tras verificación."
    ],
    "default": [
        "Sistema en operación normal.",
        "Sin anomalías detectadas en el módulo.",
        "Procesos según lo esperado."
    ],
}

def get_header_message(page: str, context: Dict[str, Any] | None = None) -> str:
    mensajes = _HEADER_MESSAGES.get(page, _HEADER_MESSAGES["default"])
    msg = random.choice(mensajes)
    try:
        return msg.format(**(context or {}))
    except Exception:
        return msg

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

    clave = random.choice(list(catalogo.keys()))
    tpl = catalogo[clave]

    out = {}
    for k, v in tpl.items():
        try:
            out[k] = v.format(**ctx)
        except Exception:
            out[k] = v
    out["plantilla_usada"] = clave
    return out
