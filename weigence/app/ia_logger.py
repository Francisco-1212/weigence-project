from datetime import datetime
from api.conexion_supabase import supabase
from app.ia_engine import (
    tendencia_ventas,
    dispersion_pesos,
    correlacion_peso_ventas,
    prediccion_quiebre_stock,
)

def registrar_ia(modulo="auditoria"):
    """
    Genera un registro IA con las métricas actuales y lo guarda en ia_registros.
    Se ejecuta cada vez que se analiza o abre el panel Auditoría.
    """
    try:
        # === Calcular métricas ===
        tendencia = tendencia_ventas() or 0
        dispersion = dispersion_pesos() or 0
        correlacion = correlacion_peso_ventas() or 0
        riesgos = len(prediccion_quiebre_stock() or [])

        # Estado general
        if riesgos > 5 or dispersion > 0.2:
            estado = "inestable"
        elif riesgos > 0 or dispersion > 0.1:
            estado = "con advertencias"
        else:
            estado = "estable"

        # === Insertar registro en Supabase ===
        registro = {
            "fecha": datetime.now().isoformat(),
            "modulo": modulo,
            "tendencia_ventas": float(tendencia),
            "dispersion_pesos": float(dispersion),
            "correlacion_peso_ventas": float(correlacion),
            "riesgos_detectados": int(riesgos),
            "estado": estado,
        }

        supabase.table("ia_registros").insert(registro).execute()
        print("[IA] Registro automático guardado:", registro)

        return True
    except Exception as e:
        print("[registrar_ia]", e)
        return False
