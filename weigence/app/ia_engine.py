from api.conexion_supabase import supabase
import numpy as np
from datetime import datetime, timedelta

# -------------------------------
# 1. Tendencia de ventas
# -------------------------------
def tendencia_ventas(dias=14):
    """Analiza las ventas recientes y devuelve un factor (>1 indica crecimiento)."""
    ventas = supabase.table("ventas").select("total, fecha_venta").execute().data or []
    if len(ventas) < 5:
        return None

    ventas = [v for v in ventas if v.get("fecha_venta") and v.get("total")]
    ventas.sort(key=lambda v: v["fecha_venta"])
    valores = np.array([v["total"] for v in ventas[-dias:]])

    x = np.arange(len(valores))
    y = valores
    m, b = np.polyfit(x, y, 1)
    tendencia = 1 + (m / (np.mean(y) + 1e-6))
    return round(float(tendencia), 2)


# -------------------------------
# 2. Dispersión de pesos (calibración)
# -------------------------------
def dispersion_pesos():
    """Calcula la variabilidad relativa de las lecturas de peso."""
    pesajes = supabase.table("pesajes").select("peso_unitario").execute().data or []
    valores = [p["peso_unitario"] for p in pesajes if p.get("peso_unitario")]
    if len(valores) < 5:
        return None

    media = np.mean(valores)
    desv = np.std(valores)
    ratio = desv / media if media else 0
    return round(float(ratio), 3)


# -------------------------------
# 3. Predicción de quiebre de stock
# -------------------------------
def prediccion_quiebre_stock():
    """Predice qué productos podrían quedar sin stock según su ritmo de venta promedio."""
    productos = supabase.table("productos").select("idproducto, nombre, stock").execute().data or []
    ventas_detalle = supabase.table("detalle_ventas").select("idproducto, cantidad").execute().data or []
    if not productos or not ventas_detalle:
        return []

    consumo = {}
    for v in ventas_detalle:
        pid = v.get("idproducto")
        if not pid:
            continue
        consumo[pid] = consumo.get(pid, 0) + v.get("cantidad", 0)

    riesgo = []
    for p in productos:
        pid = p["idproducto"]
        stock = p.get("stock", 0)
        ritmo = consumo.get(pid, 0) / max(1, len(ventas_detalle))
        if ritmo > 0 and stock / ritmo < 3:  # se agota en ~3 días
            riesgo.append(
                f"El producto '{p['nombre']}' podría agotarse en aproximadamente {stock/ritmo:.1f} días."
            )
    return riesgo


# -------------------------------
# 4. Correlación peso - ventas
# -------------------------------
def correlacion_peso_ventas():
    """Mide si los pesajes de estantes se correlacionan con las ventas."""
    pesajes = supabase.table("pesajes").select("peso_unitario, fecha_pesaje").execute().data or []
    ventas = supabase.table("ventas").select("total, fecha_venta").execute().data or []

    if len(pesajes) < 5 or len(ventas) < 5:
        return None

    pes = np.array([p["peso_unitario"] for p in pesajes[-10:] if p.get("peso_unitario")])
    ven = np.array([v["total"] for v in ventas[-10:] if v.get("total")])
    min_len = min(len(pes), len(ven))
    if min_len < 3:
        return None

    corr = np.corrcoef(pes[:min_len], ven[:min_len])[0, 1]
    return round(float(corr), 2)


# -------------------------------
# 5. Generador de recomendaciones ML
# -------------------------------
def recomendacion_ml(contexto=None):
    """Genera recomendaciones interpretativas con lenguaje técnico ampliado."""
    recs = []

    # 1. Tendencia de ventas
    trend = tendencia_ventas()
    if trend:
        if trend > 1.1:
            recs.append(
                f"Las ventas muestran un crecimiento sostenido cercano al {int((trend-1)*100)} %. "
                "Conviene anticiparse a la demanda reforzando inventario y revisando la logística de reposición, "
                "para evitar saturaciones en los próximos ciclos de venta."
            )
        elif trend < 0.9:
            recs.append(
                f"Las ventas registran una disminución aproximada del {int((1-trend)*100)} %. "
                "Revise las campañas activas, los precios y la rotación de productos, "
                "pues una desaceleración prolongada podría afectar los niveles de stock planificados."
            )

    # 2. Variabilidad en lecturas de peso
    var_pesos = dispersion_pesos()
    if var_pesos:
        if var_pesos > 0.15:
            recs.append(
                f"Las lecturas de peso presentan una dispersión del {var_pesos*100:.1f} %. "
                "Esta variabilidad sugiere que algunos sensores podrían requerir calibración o mantenimiento preventivo "
                "para garantizar la precisión del sistema de medición."
            )
        else:
            recs.append(
                "Los valores de peso se mantienen estables y dentro de los márgenes normales. "
                "Esto refleja un correcto funcionamiento de la red de sensores y su calibración."
            )

    # 3. Riesgo de quiebre de stock
    riesgo = prediccion_quiebre_stock()
    if riesgo:
        recs.append(
            "Se identifican productos con bajo margen de inventario y alta rotación. "
            "Es recomendable revisar las proyecciones de abastecimiento para prevenir quiebres."
        )
        recs.extend(riesgo)

    # 4. Coherencia entre peso y ventas
    corr = correlacion_peso_ventas()
    if corr is not None:
        if corr < -0.5:
            recs.append(
                "La correlación entre peso y volumen de ventas se mantiene negativa, lo cual es coherente: "
                "a medida que se venden productos, disminuye el peso total de los estantes. "
                "El sistema opera con correspondencia esperada entre ventas y consumo físico."
            )
        elif corr > 0.5:
            recs.append(
                "Se detecta una correlación positiva entre ventas y peso medido, "
                "posiblemente derivada de registros duplicados o lecturas de sensores invertidas. "
                "Se sugiere validar la integridad de los datos de pesaje."
            )

    # Si no se detectó nada relevante
    if not recs:
        recs.append(
            "El análisis de los indicadores no revela anomalías significativas. "
            "El sistema mantiene un comportamiento estable y consistente con los parámetros operativos esperados."
        )

    # Aplicar tono según el contexto de uso (inventario, ventas, etc.)
    recs = [ajustar_estilo(r, contexto) for r in recs]

    # --- Contexto horario y estabilidad general ---
    ctx_info = contexto_operativo()
    momento = ctx_info.get("momento", "día")
    estado = ctx_info.get("estado", "estable")

    if estado == "inestable":
        recs.append(
            f"El sistema presenta varias incidencias críticas. "
            f"Se recomienda una revisión inmediata durante la {momento}."
        )
    elif estado == "con advertencias":
        recs.append(
            f"Existen eventos que requieren seguimiento durante la {momento}. "
            f"Se aconseja mantener una supervisión constante del sistema."
        )
    else:
        recs.append(
            f"El sistema opera con normalidad esta {momento}. "
            f"Verifique que las rutinas de mantenimiento sigan ejecutándose correctamente."
        )

    return recs



def ajustar_estilo(mensaje, contexto):
    """Ajusta el tono del mensaje según el módulo actual, manteniendo un lenguaje profesional."""
    ctx = (contexto or "").lower()

    if ctx == "ventas":
        return mensaje.replace("Revise", "Analice").replace("Se recomienda", "Se sugiere")
    if ctx == "inventario":
        return mensaje.replace("Revise", "Verifique").replace("Se recomienda", "Es aconsejable")
    if ctx == "movimientos":
        return mensaje.replace("Revise", "Supervise").replace("Se recomienda", "Se sugiere revisar")
    if ctx == "auditoria":
        return mensaje.replace("Revise", "Examine").replace("Se recomienda", "Recomendación:")
    return mensaje

# -------------------------------
# 6. CONTEXTO TEMPORAL Y OPERATIVO
# -------------------------------
from datetime import datetime

def contexto_operativo():
    """Devuelve un contexto del sistema según la hora actual y estado general."""
    hora = datetime.now().hour

    if 6 <= hora < 12:
        momento = "mañana"
    elif 12 <= hora < 18:
        momento = "tarde"
    elif 18 <= hora < 23:
        momento = "noche"
    else:
        momento = "madrugada"

    return {
        "momento": momento,
        "estado": evaluar_estado_general(),
    }

def evaluar_estado_general():
    """Evalúa condiciones globales para categorizar estabilidad del sistema."""
    alertas = supabase.table("alertas").select("tipo_color").execute().data or []
    criticas = sum(1 for a in alertas if (a.get("tipo_color") or "").lower() == "rojo")

    if criticas > 3:
        return "inestable"
    if 1 <= criticas <= 3:
        return "con advertencias"
    return "estable"
