def analizar_peso(peso_actual, peso_referencia):
    diferencia = peso_referencia - peso_actual
    alerta = False

    if diferencia > 100:  # umbral arbitrario
        alerta = True

    return {
        "peso": peso_actual,
        "diferencia": diferencia,
        "alerta": alerta
    }
