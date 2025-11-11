# Plantillas de recomendaciones por contexto
DASHBOARD_TEMPLATES = {
    "metrica_critica": {
        "titulo": "Atención requerida: {kpi_nombre}",
        "mensaje": "La métrica {kpi_nombre} está {tendencia} ({valor_actual}). Esta tendencia requiere atención inmediata.",
        "detalle": "El valor actual de {kpi_nombre} está {tendencia} respecto al periodo anterior ({valor_anterior}), lo que podría indicar {implicacion}.",
        "solucion": "Se recomienda {accion_sugerida}"
    },
    "tendencia_positiva": {
        "titulo": "Tendencia positiva: {kpi_nombre}",
        "mensaje": "La métrica {kpi_nombre} muestra una mejora del {porcentaje}%",
        "detalle": "El indicador {kpi_nombre} ha mejorado de {valor_anterior} a {valor_actual}, mostrando un progreso significativo.",
        "solucion": "Para mantener esta tendencia, considere {accion_sugerida}"
    }
}

INVENTORY_TEMPLATES = {
    "stock_critico": {
        "titulo": "Stock crítico detectado",
        "mensaje": "{num_productos} productos están por debajo del nivel mínimo de stock",
        "detalle": "Los siguientes productos requieren reposición urgente: {lista_productos}",
        "solucion": "Gestione una orden de compra para los productos afectados"
    },
    "variacion_peso": {
        "titulo": "Variación de peso significativa",
        "mensaje": "Se detectó una variación de peso anormal en {producto}",
        "detalle": "El peso registrado varió en {diferencia}kg en las últimas {horas} horas",
        "solucion": "Verifique la calibración del sensor y el estado del producto"
    }
}

SALES_TEMPLATES = {
    "tendencia_ventas": {
        "titulo": "Análisis de tendencia de ventas",
        "mensaje": "Las ventas {tendencia} un {porcentaje}% respecto al periodo anterior",
        "detalle": "El total de ventas {periodo} es de ${total_ventas}, comparado con ${total_anterior}",
        "solucion": "Considere {accion_sugerida} para {objetivo}"
    },
    "producto_destacado": {
        "titulo": "Producto destacado",
        "mensaje": "{producto} representa el {porcentaje}% de las ventas totales",
        "detalle": "Este producto ha generado ${ingresos} en ventas en el último periodo",
        "solucion": "Asegure stock suficiente y considere promociones relacionadas"
    }
}

MOVEMENTS_TEMPLATES = {
    "patron_movimiento": {
        "titulo": "Patrón de movimientos detectado",
        "mensaje": "Se detectó un {tipo_patron} en los movimientos de {producto}",
        "detalle": "Este patrón sugiere {implicacion} basado en {num_ocurrencias} ocurrencias",
        "solucion": "Se recomienda {accion_sugerida} para optimizar las operaciones"
    }
}

ALERTS_TEMPLATES = {
    "alerta_critica": {
        "titulo": "Alerta crítica activa",
        "mensaje": "Hay {num_alertas} alertas críticas que requieren atención inmediata",
        "detalle": "Las alertas están relacionadas con: {categorias_alertas}",
        "solucion": "Revise y resuelva las alertas según el protocolo establecido"
    }
}

AUDIT_TEMPLATES = {
    "hallazgo_auditoria": {
        "titulo": "Hallazgo de auditoría",
        "mensaje": "Se detectó {tipo_hallazgo} en {area_afectada}",
        "detalle": "El análisis indica {descripcion_hallazgo} con un impacto de {nivel_impacto}",
        "solucion": "Implemente las siguientes medidas: {acciones_correctivas}"
    }
}