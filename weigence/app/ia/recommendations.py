"""Recommendation builders for different contexts."""
from __future__ import annotations

from typing import List

from .models import MetricSnapshot, Recommendation, SystemContext


class RecommendationBuilder:
    """Generates narrative recommendations based on metrics."""

    def build_global(self, snapshot: MetricSnapshot, contexto: SystemContext, modulo: str | None = None) -> List[Recommendation]:
        mensajes: List[Recommendation] = []

        if snapshot.tendencia_ventas is not None:
            if snapshot.tendencia_ventas > 1.1:
                mensajes.append(
                    Recommendation(
                        mensaje=(
                            "Las ventas mantienen una pendiente de crecimiento superior al 10 % respecto a las semanas previas. "
                            "Refuerce el abastecimiento y verifique la logística de reposición para sostener la demanda."),
                        nivel="advertencia",
                        categoria="ventas",
                    )
                )
            elif snapshot.tendencia_ventas < 0.9:
                mensajes.append(
                    Recommendation(
                        mensaje=(
                            "La tendencia de ventas disminuyó más de un 10 % frente al promedio histórico. "
                            "Analice campañas, precios y rotación para evitar un impacto prolongado en inventario."),
                        nivel="advertencia",
                        categoria="ventas",
                    )
                )

        if snapshot.dispersion_pesos is not None:
            if snapshot.dispersion_pesos > 0.15:
                mensajes.append(
                    Recommendation(
                        mensaje=(
                            "Las lecturas de peso muestran una dispersión por sobre el 15 %, indicio de sensores que requieren calibración o mantenimiento preventivo."),
                        nivel="critico",
                        categoria="sensores",
                    )
                )
            else:
                mensajes.append(
                    Recommendation(
                        mensaje=(
                            "Las lecturas de peso se encuentran dentro de la dispersión esperada, reflejando estabilidad en la calibración de sensores."),
                        nivel="normal",
                        categoria="sensores",
                    )
                )

        if snapshot.riesgos_detectados:
            mensajes.append(
                Recommendation(
                    mensaje=(
                        "Se identificaron productos con riesgo de quiebre de stock en menos de tres días. Revise la planificación de reposición para mitigarlos."),
                    nivel="critico" if snapshot.riesgos_detectados > 3 else "advertencia",
                    categoria="inventario",
                )
            )
            for detalle in snapshot.riesgos_detalle[:3]:
                mensajes.append(Recommendation(mensaje=detalle, nivel="advertencia", categoria="inventario"))

        if snapshot.correlacion_peso_ventas is not None:
            if snapshot.correlacion_peso_ventas < -0.5:
                mensajes.append(
                    Recommendation(
                        mensaje="La correlación entre pesos registrados y ventas es negativa y coherente: el inventario físico disminuye conforme avanza la venta.",
                        nivel="normal",
                        categoria="coherencia",
                    )
                )
            elif snapshot.correlacion_peso_ventas > 0.5:
                mensajes.append(
                    Recommendation(
                        mensaje="Existe correlación positiva entre ventas y peso registrado. Valide posibles duplicidades o lectura invertida de sensores.",
                        nivel="advertencia",
                        categoria="coherencia",
                    )
                )

        if not mensajes:
            mensajes.append(
                Recommendation(
                    mensaje="Los indicadores analizados no presentan anomalías relevantes. El sistema mantiene comportamiento estable.",
                    nivel="normal",
                )
            )

        mensajes.extend(self._context_messages(contexto, modulo))
        return mensajes

    def build_contextual(self, snapshot: MetricSnapshot, contexto: SystemContext, modulo: str) -> List[Recommendation]:
        modulo = modulo.lower()
        base: List[Recommendation] = []

        if modulo == "dashboard":
            base.append(
                Recommendation(
                    mensaje="El panel concentra {criticas} alertas críticas pendientes.".format(
                        criticas=contexto.alertas_criticas
                    )
                    if contexto.alertas_criticas
                    else "No se registran alertas críticas activas en el panel general.",
                    nivel="critico" if contexto.alertas_criticas else "normal",
                )
            )
        elif modulo == "inventario":
            base.extend(self._inventario_messages(snapshot, contexto))
        elif modulo == "ventas":
            tendencia = snapshot.tendencia_ventas
            if tendencia is None:
                base.append(
                    Recommendation(
                        mensaje="No se registran suficientes ventas para estimar una tendencia confiable.",
                        nivel="advertencia",
                    )
                )
            elif tendencia < 0.9:
                base.append(
                    Recommendation(
                        mensaje="Las ventas caen respecto al histórico reciente. Ajuste promociones y abastecimiento.",
                        nivel="advertencia",
                    )
                )
            elif tendencia > 1.1:
                base.append(
                    Recommendation(
                        mensaje="Las ventas aumentan sobre lo proyectado. Planifique reposiciones adicionales.",
                        nivel="advertencia",
                    )
                )
            else:
                base.append(
                    Recommendation(
                        mensaje="La tendencia de ventas se mantiene estable frente a la referencia histórica.",
                        nivel="normal",
                    )
                )
        elif modulo == "movimientos":
            base.append(
                Recommendation(
                    mensaje="El módulo de movimientos registra actividad constante. Revise trazabilidad si identifica operaciones sin responsable registrado.",
                    nivel="advertencia",
                )
            )
        elif modulo == "alertas":
            base.append(
                Recommendation(
                    mensaje=(
                        "La bandeja de alertas mantiene {criticas} eventos críticos.".format(
                            criticas=contexto.alertas_criticas
                        )
                        if contexto.alertas_criticas
                        else "No hay alertas críticas abiertas en este momento."
                    ),
                    nivel="critico" if contexto.alertas_criticas else "normal",
                )
            )
        elif modulo == "auditoria":
            base.append(
                Recommendation(
                    mensaje="La consola de auditoría recopilará métricas comparativas tras cada consulta para identificar variaciones relevantes.",
                    nivel="normal",
                )
            )
        else:
            base.append(Recommendation(mensaje="No existen recomendaciones específicas para este módulo.", nivel="normal"))

        return base

    # ------------------------------------------------------------------
    def _context_messages(self, contexto: SystemContext, modulo: str | None) -> List[Recommendation]:
        mensajes: List[Recommendation] = []
        estado = contexto.estado
        if estado == "critico":
            mensajes.append(
                Recommendation(
                    mensaje=(
                        "El sistema presenta incidencias críticas en curso. Priorice una revisión inmediata durante la {momento}.".format(
                            momento=contexto.momento
                        )
                    ),
                    nivel="critico",
                )
            )
        elif estado == "advertencia":
            mensajes.append(
                Recommendation(
                    mensaje=(
                        "Se detectan eventos que requieren seguimiento cercano esta {momento}. Mantenga una supervisión activa del tablero.".format(
                            momento=contexto.momento
                        )
                    ),
                    nivel="advertencia",
                )
            )
        else:
            mensajes.append(
                Recommendation(
                    mensaje=(
                        "El sistema opera con normalidad durante la {momento}. Mantenga las rutinas de verificación preventiva.".format(
                            momento=contexto.momento
                        )
                    ),
                    nivel="normal",
                )
            )

        if contexto.ultimo_evento:
            mensajes.append(
                Recommendation(
                    mensaje="Último evento registrado: {evento}".format(evento=contexto.ultimo_evento),
                    nivel="advertencia" if estado != "normal" else "normal",
                    categoria="eventos",
                )
            )

        return mensajes

    def _inventario_messages(self, snapshot: MetricSnapshot, contexto: SystemContext) -> List[Recommendation]:
        mensajes: List[Recommendation] = []
        if contexto.estantes_al_limite:
            mensajes.append(
                Recommendation(
                    mensaje="{cantidad} estantes superan el 95 % de capacidad. Realice redistribución para evitar sobrecargas.".format(
                        cantidad=contexto.estantes_al_limite
                    ),
                    nivel="advertencia" if contexto.estantes_al_limite < 3 else "critico",
                )
            )
        if snapshot.riesgos_detectados:
            mensajes.append(
                Recommendation(
                    mensaje="Existen {cantidad} productos con riesgo de quiebre. Ajuste pedidos y confirme entregas.".format(
                        cantidad=snapshot.riesgos_detectados
                    ),
                    nivel="critico" if snapshot.riesgos_detectados > 3 else "advertencia",
                )
            )
        if not mensajes:
            mensajes.append(
                Recommendation(
                    mensaje="Los niveles de inventario se encuentran dentro de los márgenes operativos definidos.",
                    nivel="normal",
                )
            )
        return mensajes
