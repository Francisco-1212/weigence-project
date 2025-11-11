"""Mensajes predefinidos para recomendaciones IA."""
from typing import Dict, List

HEADER_MESSAGES = {
    "dashboard": [
        "El estado general del sistema se mantiene estable",
        "Los indicadores principales muestran un comportamiento normal",
        "Se detectan {n_alerts} alertas que requieren atención",
        "La actividad del sistema muestra patrones regulares",
        "Las métricas clave están dentro de rangos esperados"
    ],
    "inventario": [
        "El inventario muestra variaciones normales de peso",
        "Se mantiene un ritmo constante de movimientos",
        "La rotación de productos sigue patrones esperados",
        "Los niveles de stock se mantienen estables",
        "No se detectan anomalías significativas en pesajes"
    ],
    "ventas": [
        "Las ventas mantienen un ritmo constante",
        "Se observa una tendencia positiva en transacciones",
        "El flujo comercial se desarrolla con normalidad",
        "Los indicadores de venta están en rangos óptimos",
        "La actividad comercial sigue patrones regulares"
    ],
    "movimientos": [
        "Los movimientos de inventario son consistentes",
        "Se registra actividad normal en el sistema",
        "El flujo de operaciones se mantiene estable",
        "Las operaciones siguen el ritmo esperado",
        "No se detectan anomalías en movimientos"
    ],
    "auditoria": [
        "Los controles operativos funcionan correctamente",
        "Se mantiene la integridad de los registros",
        "Los sistemas de monitoreo operan normalmente",
        "No se detectan desviaciones significativas",
        "Las validaciones del sistema son satisfactorias"
    ],
    "default": [
        "El sistema opera con normalidad",
        "Los procesos se ejecutan según lo esperado",
        "Se mantiene la estabilidad operativa",
        "No se detectan anomalías significativas",
        "Los indicadores muestran comportamiento regular"
    ]
}

def get_header_message(page: str, context: Dict = None) -> str:
    """
    Selecciona un mensaje apropiado para el header según la página y contexto.
    
    Args:
        page: Página actual
        context: Datos de contexto para personalizar el mensaje
        
    Returns:
        Mensaje seleccionado y formateado
    """
    # Obtener lista de mensajes para la página
    messages = HEADER_MESSAGES.get(page, HEADER_MESSAGES["default"])
    
    # TODO: Implementar lógica de selección basada en contexto
    # Por ahora retorna el primer mensaje
    message = messages[0]
    
    # Si hay contexto, formatea el mensaje
    if context:
        try:
            message = message.format(**context)
        except KeyError:
            pass
            
    return message