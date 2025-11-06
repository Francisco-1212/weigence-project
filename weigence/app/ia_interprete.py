from api.conexion_supabase import supabase
from statistics import mean

def interpretar_ia_auditoria():
    try:
        registros = supabase.table("ia_registros") \
            .select("*") \
            .eq("modulo", "auditoria") \
            .order("fecha", desc=True) \
            .limit(10).execute().data or []

        if len(registros) < 2:
            return ["Aún no hay suficientes registros para generar un análisis comparativo."]

        actual = registros[0]
        historico = registros[1:]

        # Calcular promedios
        prom = {
            "tendencia_ventas": mean([r["tendencia_ventas"] for r in historico if r["tendencia_ventas"] is not None]),
            "dispersion_pesos": mean([r["dispersion_pesos"] for r in historico if r["dispersion_pesos"] is not None]),
            "correlacion_peso_ventas": mean([r["correlacion_peso_ventas"] for r in historico if r["correlacion_peso_ventas"] is not None]),
            "riesgos_detectados": mean([r["riesgos_detectados"] for r in historico if r["riesgos_detectados"] is not None]),
        }

        # Calcular diferencias
        delta_tendencia = actual["tendencia_ventas"] - prom["tendencia_ventas"]
        delta_dispersion = actual["dispersion_pesos"] - prom["dispersion_pesos"]
        delta_correlacion = actual["correlacion_peso_ventas"] - prom["correlacion_peso_ventas"]
        delta_riesgos = actual["riesgos_detectados"] - prom["riesgos_detectados"]

        # Interpretar resultados
        recs = []

        if delta_tendencia > 0.05:
            recs.append("Las ventas muestran una leve tendencia al alza respecto al comportamiento histórico.")
        elif delta_tendencia < -0.05:
            recs.append("Se observa una disminución en la tendencia de ventas comparada con el promedio previo.")

        if delta_dispersion > 0.1:
            recs.append("El sistema presenta mayor dispersión en los pesajes, posible descalibración o fluctuaciones.")
        elif delta_dispersion < -0.05:
            recs.append("Los valores de peso se han estabilizado, indicando buena calibración.")

        if delta_correlacion < -0.3:
            recs.append("La correlación peso-ventas es coherente: las ventas aumentan al disminuir el peso de inventario.")
        elif delta_correlacion > 0.3:
            recs.append("La correlación peso-ventas es anómala; revisar lecturas o coherencia de datos de pesaje.")

        if delta_riesgos > 2:
            recs.append("El número de alertas o riesgos detectados aumentó significativamente.")
        elif delta_riesgos < -2:
            recs.append("La cantidad de riesgos disminuyó, señal de estabilidad operacional.")

        if not recs:
            recs.append("El sistema mantiene un comportamiento estable en relación con sus métricas previas.")

        return recs

    except Exception as e:
        print("[interpretar_ia_auditoria]", e)
        return ["Error en la interpretación de IA."]
