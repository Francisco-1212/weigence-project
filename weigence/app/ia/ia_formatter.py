"""Human-readable formatter for IA insights."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List

from .ia_engine import EngineInsight
from .ia_snapshots import IASnapshot


@dataclass
class TemplateGroup:
    titles: List[str]
    descriptions: List[str]
    causes: List[str]
    solutions: List[str]


class IAFormatter:
    """Generates narrative recommendations using varied templates."""

    def __init__(self) -> None:
        self._rng = random.SystemRandom()
        self._templates: Dict[str, TemplateGroup] = {
            "sales_collapse": TemplateGroup(
                titles=[
                    "Ventas en caída libre controlada",
                    "Pérdida acelerada de tracción comercial",
                    "Desaceleración abrupta del flujo de ventas",
                ],
                descriptions=[
                    "Las métricas de las últimas {sales_window}h muestran una contracción del {trend_percent:.1f}% respecto al comportamiento previo, acompañada de un z-score de {anomaly_score:.2f} que confirma la anomalía estadística.",
                    "Se detectó una caída significativa en el ritmo de ventas: el promedio reciente se aleja del histórico con un diferencial del {trend_percent:.1f}%. La dispersión actual ({sales_volatility:.2f}) refuerza un escenario de inestabilidad comercial.",
                ],
                causes=[
                    "Una conjunción de alertas críticas ({critical_alerts}) y {inactivity_hours:.1f}h sin actividad consistente sugiere un freno operativo.",
                    "La tendencia negativa se explica por la reducción de inventario ({weight_change:.2f}) y la menor interacción operativa ({movements_per_hour:.2f} movimientos/hora).",
                ],
                solutions=[
                    "Restablecer el pulso operativo desplegando refuerzos en piso y habilitando un plan de ventas intensivo para las próximas 6h.",
                    "Coordinar con operaciones una verificación inmediata de inventario y lanzar promociones tácticas para recuperar demanda.",
                ],
            ),
            "inventory_instability": TemplateGroup(
                titles=[
                    "Inventario sin equilibrio funcional",
                    "Oscilaciones de stock fuera de tolerancia",
                ],
                descriptions=[
                    "Los pesajes recientes evidencian una variación relativa de {weight_volatility:.2f} y un cambio neto de {weight_change:.2f}, valores que superan los umbrales habituales del módulo.",
                    "Se registran fluctuaciones de inventario atípicas: la volatilidad ({weight_volatility:.2f}) combinada con el desbalance de {weight_change:.2f} anticipa quiebres de stock inminentes.",
                ],
                causes=[
                    "La demanda específica de ítems de alta rotación y las alertas abiertas ({warning_alerts}) presionan la disponibilidad.",
                    "La reducción acelerada del inventario apunta a una reposición tardía y potenciales errores de pesaje en origen.",
                ],
                solutions=[
                    "Iniciar un ciclo de reconteo asistido y reforzar la reposición en los productos de mayor salida detectados.",
                    "Ajustar los umbrales de alerta y programar verificaciones cada 2h hasta estabilizar el peso promedio.",
                ],
            ),
            "alert_pressure": TemplateGroup(
                titles=[
                    "Presión operativa por exceso de alertas",
                    "Panel de alarmas en zona de saturación",
                ],
                descriptions=[
                    "En las últimas {movement_window}h se acumularon {critical_alerts} alertas críticas y {warning_alerts} advertencias. El indicador compuesto alcanza {signal_strength:.2f}, reflejando estrés sostenido.",
                    "El tablero supera el umbral saludable: {critical_alerts} incidencias críticas simultáneas y {warning_alerts} avisos activos demandan priorización inmediata.",
                ],
                causes=[
                    "La concentración de eventos críticos sugiere procesos correctivos incompletos y escalamiento pendiente.",
                    "Persisten alarmas vinculadas a la caída del {trend_percent:.1f}% en ventas, lo que indica un problema sistémico de atención.",
                ],
                solutions=[
                    "Aplicar un protocolo de depuración priorizando alarmas rojas y definir responsables antes de las próximas 2h.",
                    "Coordinar una sala de guerra operativa que integre operaciones, logística y TI para cerrar incidencias con dueños claros.",
                ],
            ),
            "operational_inertia": TemplateGroup(
                titles=[
                    "Actividad operativa por debajo de lo esperado",
                    "Piso de operaciones en estado de latencia",
                ],
                descriptions=[
                    "Solo se registran {movements_per_hour:.2f} movimientos/hora durante {movement_window}h. La ausencia de flujo se correlaciona con una caída del {trend_percent:.1f}% en ventas.",
                    "El sistema reporta {inactivity_hours:.1f}h sin interacción relevante y un dinamismo mínimo ({movements_per_hour:.2f} movimientos/hora).",
                ],
                causes=[
                    "Se observa un desacople entre operaciones y reposición, posiblemente por turnos reducidos o bloqueos de acceso.",
                    "Una sobrecarga en tareas administrativas pudo desatender el seguimiento en piso y la reposición clave.",
                ],
                solutions=[
                    "Redistribuir tareas críticas, activar personal de respaldo y auditar accesos para normalizar el flujo en las próximas horas.",
                    "Implementar un tablero de control horario y micro-reuniones de coordinación hasta recuperar el ritmo base.",
                ],
            ),
            "positive_outlook": TemplateGroup(
                titles=[
                    "Momentum positivo confirmado",
                    "Recuperación sostenida del negocio",
                ],
                descriptions=[
                    "El promedio reciente crece {trend_percent:.1f}% respecto al histórico y el inventario se recompone ({weight_change:.2f}). La señal agregada es {signal_strength:.2f}.",
                    "Los indicadores de las últimas {sales_window}h validan el repunte comercial con variaciones controladas y señal consolidada ({signal_strength:.2f}).",
                ],
                causes=[
                    "Las acciones de impulso recientes y la reposición ágil están alineando demanda e inventario.",
                    "El refuerzo de promociones y la optimización logística se traducen en mayor conversión.",
                ],
                solutions=[
                    "Escalar la estrategia de impulso, documentar aprendizajes y fijar un plan de seguimiento diario para sostener el ritmo.",
                    "Consolidar este comportamiento replicando los ajustes operativos al resto de turnos y manteniendo medición horaria.",
                ],
            ),
            "stable_outlook": TemplateGroup(
                titles=[
                    "Entorno operativo estable",
                    "Sin anomalías relevantes en la última ventana",
                ],
                descriptions=[
                    "Las métricas monitoreadas permanecen dentro de parámetros normales. La tendencia es de {trend_percent:.1f}% con volatilidad de {weight_volatility:.2f}.",
                    "La lectura consolidada no muestra desviaciones severas: tendencia {trend_percent:.1f}%, alertas totales {alerts_total}.",
                ],
                causes=[
                    "Se mantiene una ejecución consistente sin eventos que comprometan el desempeño.",
                    "Las correcciones previas estabilizaron ventas e inventario en el corto plazo.",
                ],
                solutions=[
                    "Continuar con la rutina de seguimiento y planificar un chequeo extendido en las próximas 12h.",
                    "Documentar buenas prácticas y mantener la vigilancia sobre posibles desviaciones incipientes.",
                ],
            ),
        }

    def render(self, insight: EngineInsight, snapshot: IASnapshot) -> Dict[str, str]:
        grupo = self._templates.get(insight.key, self._templates["stable_outlook"])
        contexto = self._construir_contexto(insight, snapshot)

        titulo = self._rng.choice(grupo.titles).format(**contexto)
        descripcion = self._rng.choice(grupo.descriptions).format(**contexto)
        causa = self._rng.choice(grupo.causes).format(**contexto)
        solucion = self._rng.choice(grupo.solutions).format(**contexto)

        mensaje = f"{descripcion}\n\nCausa probable: {causa}"

        return {
            "titulo": titulo,
            "mensaje": mensaje,
            "solucion": solucion,
            "severidad": insight.severity,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _construir_contexto(self, insight: EngineInsight, snapshot: IASnapshot) -> Dict[str, float]:
        contexto = {
            "trend_percent": insight.data_points.get("trend_percent", snapshot.sales_trend_percent) * 100,
            "sales_volatility": snapshot.sales_volatility,
            "anomaly_score": insight.data_points.get("anomaly_score", snapshot.sales_anomaly_score),
            "weight_volatility": insight.data_points.get("weight_volatility", snapshot.weight_volatility),
            "weight_change": insight.data_points.get("weight_change", snapshot.weight_change_rate),
            "critical_alerts": insight.data_points.get("critical_alerts", snapshot.critical_alerts),
            "warning_alerts": insight.data_points.get("warning_alerts", snapshot.warning_alerts),
            "signal_strength": insight.data_points.get("signal_strength", snapshot.signal_strength),
            "movements_per_hour": insight.data_points.get("movements_per_hour", snapshot.movements_per_hour),
            "inactivity_hours": insight.data_points.get("inactivity_hours", snapshot.inactivity_hours),
            "alerts_total": sum(snapshot.alerts_summary.values()),
            "sales_window": snapshot.sales_window_hours,
            "movement_window": snapshot.movement_window_hours,
        }
        return contexto


formatter = IAFormatter()
