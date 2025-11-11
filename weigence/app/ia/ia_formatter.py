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
            # Plantillas actualizadas para una comunicación más humana y empática
            "sales_collapse": TemplateGroup(
                titles=[
                    "⚠️ Momento clave para impulsar ventas",
                    "🔄 Oportunidad de reactivación comercial",
                    "📊 Atención: Ventas necesitan impulso",
                ],
                summaries=[
                    "He detectado una disminución del {trend_percent:.1f}% en ventas que podemos abordar juntos.",
                    "Las ventas muestran una tendencia que requiere nuestra atención inmediata.",
                ],
                descriptions=[
                    "En las últimas {sales_window}h, he observado un patrón importante: nuestras ventas han disminuido un {trend_percent:.1f}%. El indicador de anomalía ({anomaly_score:.2f}) sugiere que este no es un comportamiento típico y tenemos una clara oportunidad de mejora.",
                    "El ritmo de ventas actual se ha alejado {trend_percent:.1f}% de nuestro promedio esperado. La variabilidad ({sales_volatility:.2f}) indica que es el momento perfecto para implementar acciones correctivas.",
                ],
                causes=[
                    "He identificado dos factores clave: tenemos {critical_alerts} alertas pendientes y {inactivity_hours:.1f}h de actividad reducida que están impactando nuestro rendimiento.",
                    "Los datos sugieren que esto se debe a niveles de inventario más bajos ({weight_change:.2f}) y una disminución en la actividad operativa ({movements_per_hour:.2f} movimientos/hora).",
                ],
                solutions=[
                    "💡 Recomiendo activar un plan de respuesta rápida: reforcemos el equipo en piso e implementemos una estrategia de ventas especial para las próximas 6 horas. ¡Podemos revertir esta situación juntos!",
                    "💡 Sugiero dos acciones inmediatas: realizar una verificación rápida de inventario y considerar promociones estratégicas. El momento es ideal para impulsar la demanda.",
                ],
            ),
            "inventory_instability": TemplateGroup(
                titles=[
                    "📦 Atención al equilibrio de inventario",
                    "⚖️ Oportunidad de optimización de stock",
                ],
                summaries=[
                    "He detectado algunas variaciones en el inventario que merecen nuestra atención.",
                    "El comportamiento del stock muestra patrones que podemos mejorar juntos.",
                ],
                descriptions=[
                    "Los últimos datos muestran un panorama interesante: tenemos una variación de {weight_volatility:.2f} en los pesajes y un cambio neto de {weight_change:.2f}. Estos valores están fuera de nuestros rangos ideales y representan una oportunidad de mejora.",
                    "Estoy observando fluctuaciones poco usuales en nuestro inventario: la variabilidad es de {weight_volatility:.2f} y hay un desbalance de {weight_change:.2f}. Es importante que actuemos antes de que esto afecte nuestra disponibilidad.",
                ],
                causes=[
                    "He identificado dos factores principales: una demanda elevada en productos clave y {warning_alerts} alertas que necesitan nuestra atención.",
                    "Los datos sugieren que esto se debe a una combinación de reposición no optimizada y posibles discrepancias en los pesajes iniciales.",
                ],
                solutions=[
                    "💡 Te sugiero iniciar un proceso de verificación enfocado en los productos más demandados. También sería valioso reforzar el sistema de reposición para estos items.",
                    "💡 Recomiendo dos acciones: primero, ajustar nuestros parámetros de alerta, y segundo, implementar un ciclo de verificación cada 2 horas hasta que logremos la estabilidad deseada.",
                ],
            ),
            "alert_pressure": TemplateGroup(
                titles=[
                    "🚨 Atención: Sistema de alertas necesita revisión",
                    "⚡ Momento de optimizar nuestras alertas",
                ],
                summaries=[
                    "He detectado un incremento en las alertas que requiere nuestra atención.",
                    "Tenemos una oportunidad para optimizar la gestión de alertas.",
                ],
                descriptions=[
                    "Durante las últimas {movement_window}h, he registrado un panorama que necesita nuestra atención: tenemos {critical_alerts} alertas críticas y {warning_alerts} advertencias activas. El índice de prioridad está en {signal_strength:.2f}, lo que indica que es un buen momento para actuar.",
                    "Nuestro panel está mostrando más actividad de lo habitual: hay {critical_alerts} situaciones críticas y {warning_alerts} advertencias que podríamos resolver juntos. Es importante que actuemos de manera organizada.",
                ],
                causes=[
                    "El análisis sugiere que tenemos algunos procesos pendientes de resolución y casos que necesitan escalarse al siguiente nivel.",
                    "Las alertas persistentes están relacionadas con una disminución del {trend_percent:.1f}% en ventas, lo que indica que podemos mejorar nuestro tiempo de respuesta.",
                ],
                solutions=[
                    "💡 Sugiero implementar un plan de acción en dos fases: primero, atender las alertas críticas con un equipo dedicado en las próximas 2 horas, y segundo, asignar responsables claros para el seguimiento.",
                    "💡 Recomiendo organizar una sesión de coordinación rápida entre los equipos de operaciones, logística y TI. Juntos podemos resolver estas incidencias de manera más efectiva.",
                ],
            ),
            "operational_inertia": TemplateGroup(
                titles=[
                    "🔄 Oportunidad para impulsar la actividad",
                    "📈 Momento de reactivar operaciones",
                ],
                summaries=[
                    "He notado que podemos mejorar nuestro ritmo operativo actual.",
                    "Tenemos espacio para optimizar la actividad en piso.",
                ],
                descriptions=[
                    "Los datos muestran que tenemos {movements_per_hour:.2f} movimientos por hora en un período de {movement_window}h. Este ritmo está relacionado con una variación del {trend_percent:.1f}% en ventas, lo que nos da una clara oportunidad de mejora.",
                    "En las últimas {inactivity_hours:.1f}h he detectado una actividad más baja de lo usual ({movements_per_hour:.2f} movimientos/hora). Juntos podemos elevar estos números.",
                ],
                causes=[
                    "El análisis sugiere que podemos mejorar la sincronización entre operaciones y reposición. Esto puede deberse a ajustes en los turnos o temas de acceso.",
                    "Parece que la carga de tareas administrativas está afectando nuestra capacidad de seguimiento en piso y reposición.",
                ],
                solutions=[
                    "💡 Te sugiero tres acciones clave: reorganizar las tareas prioritarias, activar el equipo de respaldo y revisar los accesos para optimizar el flujo operativo.",
                    "💡 Recomiendo implementar un sistema de seguimiento por hora y establecer breves reuniones de coordinación. Esto nos ayudará a recuperar nuestro ritmo óptimo.",
                ],
            ),
            "positive_outlook": TemplateGroup(
                titles=[
                    "🌟 ¡Excelente momento comercial!",
                    "💫 Resultados muy positivos",
                ],
                summaries=[
                    "¡Felicitaciones! Estamos viendo resultados muy positivos.",
                    "¡Genial trabajo! Los indicadores muestran una tendencia favorable.",
                ],
                descriptions=[
                    "¡Excelentes noticias! Nuestros números están mejorando: hemos logrado un crecimiento del {trend_percent:.1f}% y el inventario muestra una recuperación saludable ({weight_change:.2f}). El índice de rendimiento está en {signal_strength:.2f}, ¡lo cual es fantástico!",
                    "Los datos de las últimas {sales_window}h confirman nuestro buen momento: tenemos un crecimiento sostenido y un índice de rendimiento de {signal_strength:.2f}. ¡El equipo está haciendo un trabajo excepcional!",
                ],
                causes=[
                    "Este éxito se debe a la excelente ejecución de nuestras estrategias comerciales y a un manejo eficiente del inventario.",
                    "La combinación de promociones efectivas y mejoras en nuestra logística está dando resultados sobresalientes.",
                ],
                solutions=[
                    "💡 Para mantener este impulso, sugiero: expandir las estrategias que están funcionando, documentar las mejores prácticas y establecer un seguimiento diario.",
                    "💡 Recomiendo compartir estas técnicas exitosas con todos los turnos y mantener nuestro sistema de medición horaria. ¡Sigamos con este excelente ritmo!",
                ],
            ),
            "stable_outlook": TemplateGroup(
                titles=[
                    "✨ Todo fluye con normalidad",
                    "🎯 Operaciones en equilibrio ideal",
                ],
                summaries=[
                    "Las operaciones se mantienen estables y saludables.",
                    "Todo se desarrolla según lo esperado.",
                ],
                descriptions=[
                    "¡Buenas noticias! Todos nuestros indicadores están en rangos óptimos. Tenemos una tendencia del {trend_percent:.1f}% y una estabilidad muy buena ({weight_volatility:.2f}).",
                    "El panorama es positivo: mantenemos una tendencia del {trend_percent:.1f}% y solo {alerts_total} alertas en total. ¡Sigamos así!",
                ],
                causes=[
                    "Este equilibrio es resultado de una ejecución consistente y un buen trabajo en equipo.",
                    "Las mejoras implementadas anteriormente están dando los resultados esperados en ventas e inventario.",
                ],
                solutions=[
                    "💡 Recomiendo mantener nuestro ritmo actual y programar una revisión más detallada en las próximas 12 horas.",
                    "💡 Sugiero documentar estas buenas prácticas que nos están funcionando y mantener nuestra atención para detectar cualquier ajuste necesario.",
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
