"""Human-readable formatter for IA insights."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List

from .ia_engine import EngineInsight
from .ia_snapshots import IASnapshot


logger = logging.getLogger(__name__)


@dataclass
class TemplateGroup:
    titles: List[str] = field(default_factory=list)
    summaries: List[str] = field(default_factory=list)
    descriptions: List[str] = field(default_factory=list)
    causes: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)

    def ensure_defaults(self) -> None:
        """Guarantee that every collection has at least one element."""

        if not self.titles:
            self.titles.append("Estado operativo estable")
        if not self.summaries:
            self.summaries.append("Panorama sin novedades relevantes.")
        if not self.descriptions:
            self.descriptions.append("Las métricas monitoreadas permanecen dentro de parámetros normales.")
        if not self.causes:
            self.causes.append("No se detectaron desviaciones con impacto operativo.")
        if not self.solutions:
            self.solutions.append("Mantener la rutina de supervisión estándar.")


class IAFormatter:
    """Generates narrative recommendations using varied templates."""

    _DEFAULT_KEY = "stable_outlook"

    def __init__(self) -> None:
        self._rng = random.SystemRandom()
        self._templates: Dict[str, TemplateGroup] = {
            "sales_collapse": TemplateGroup(
                titles=[
                    "Ventas en caída libre controlada",
                    "Pérdida acelerada de tracción comercial",
                    "Desaceleración abrupta del flujo de ventas",
                ],
                summaries=[
                    "Ventas contrayéndose {trend_percent:.1f}% con señales de estrés inmediato.",
                    "Contracción pronunciada de ventas y baja actividad operativa.",
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
                summaries=[
                    "Inventario mostrando variaciones anormales de peso.",
                    "Stock con volatilidad fuera de parámetros.",
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
                summaries=[
                    "Acumulación de alertas críticas en curso.",
                    "Tablero de alarmas saturado, requiere priorización.",
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
                summaries=[
                    "Movimiento operativo insuficiente en la última ventana.",
                    "Actividad en piso con ritmo muy bajo.",
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
                summaries=[
                    "Se consolida un repunte comercial y operativo.",
                    "Indicadores alineados con tendencia positiva.",
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
                summaries=[
                    "Operación estable sin alertas destacadas.",
                    "Sin desvíos relevantes detectados.",
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

        for grupo in self._templates.values():
            grupo.ensure_defaults()

    def render(self, insight: EngineInsight, snapshot: IASnapshot) -> Dict[str, str]:
        grupo = self._templates.get(insight.key, self._templates[self._DEFAULT_KEY])
        contexto = self._construir_contexto(insight, snapshot)

        titulo = self._render_fragment(grupo.titles, contexto, "Estado operativo estable")
        resumen = self._render_fragment(grupo.summaries, contexto, "Panorama estable.")
        descripcion = self._render_fragment(
            grupo.descriptions,
            contexto,
            "Las métricas monitoreadas se mantienen en márgenes esperados.",
        )
        causa = self._render_fragment(
            grupo.causes,
            contexto,
            "No se detectaron factores críticos adicionales.",
        )
        solucion = self._render_fragment(
            grupo.solutions,
            contexto,
            "Mantener la vigilancia operativa y documentar el seguimiento.",
        )

        drivers = [d for d in insight.drivers if d]
        if drivers:
            drivers_text = "\n".join(f"- {driver}" for driver in drivers)
            detalle = f"{descripcion}\n\nIndicadores relevantes:\n{drivers_text}\n\nMotivo principal: {causa}"
        else:
            detalle = f"{descripcion}\n\nMotivo principal: {causa}"

        resultado = {
            "titulo": titulo,
            "mensaje_resumen": resumen,
            "mensaje_detallado": detalle,
            "mensaje": resumen,
            "detalle": detalle,
            "solucion": solucion,
            "severidad": insight.severity,
        }

        return self._validar_payload(resultado)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _render_fragment(
        self, opciones: List[str], contexto: Dict[str, float], fallback: str
    ) -> str:
        if not opciones:
            return fallback
        plantilla = self._rng.choice(opciones)
        try:
            texto = plantilla.format(**contexto)
        except Exception as exc:  # pragma: no cover - logging defensive path
            logger.exception("[IAFormatter] Error formateando plantilla '%s': %s", plantilla, exc)
            return fallback
        texto = texto.strip()
        return texto or fallback

    def _validar_payload(self, payload: Dict[str, str]) -> Dict[str, str]:
        for clave in ("titulo", "mensaje_resumen", "mensaje_detallado", "solucion"):
            valor = payload.get(clave, "")
            if not valor:
                payload[clave] = {
                    "titulo": "Diagnóstico operativo",
                    "mensaje_resumen": "Sin resumen disponible.",
                    "mensaje_detallado": "No se pudo construir el detalle de la recomendación.",
                    "solucion": "Revisar manualmente los indicadores clave y relanzar el motor IA.",
                }[clave]
        payload.setdefault("mensaje", payload["mensaje_resumen"])
        payload.setdefault("detalle", payload["mensaje_detallado"])
        payload.setdefault("severidad", "info")
        return payload

    def _construir_contexto(self, insight: EngineInsight, snapshot: IASnapshot) -> Dict[str, float]:
        contexto = {
            "trend_percent": float(
                insight.data_points.get("trend_percent", snapshot.sales_trend_percent)
            )
            * 100,
            "sales_volatility": float(snapshot.sales_volatility or 0.0),
            "anomaly_score": float(
                insight.data_points.get("anomaly_score", snapshot.sales_anomaly_score)
                or 0.0
            ),
            "weight_volatility": float(
                insight.data_points.get("weight_volatility", snapshot.weight_volatility) or 0.0
            ),
            "weight_change": float(
                insight.data_points.get("weight_change", snapshot.weight_change_rate) or 0.0
            ),
            "critical_alerts": int(
                insight.data_points.get("critical_alerts", snapshot.critical_alerts) or 0
            ),
            "warning_alerts": int(
                insight.data_points.get("warning_alerts", snapshot.warning_alerts) or 0
            ),
            "signal_strength": float(
                insight.data_points.get("signal_strength", snapshot.signal_strength) or 0.0
            ),
            "movements_per_hour": float(
                insight.data_points.get("movements_per_hour", snapshot.movements_per_hour) or 0.0
            ),
            "inactivity_hours": float(
                insight.data_points.get("inactivity_hours", snapshot.inactivity_hours) or 0.0
            ),
            "alerts_total": int(sum(snapshot.alerts_summary.values())),
            "sales_window": int(snapshot.sales_window_hours),
            "movement_window": int(snapshot.movement_window_hours),
        }
        return contexto


formatter = IAFormatter()
