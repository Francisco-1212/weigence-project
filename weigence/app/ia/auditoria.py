"""Audit interpretation logic for IA."""
from __future__ import annotations

import statistics
from typing import List, Optional

from .models import AuditoriaRegistro, Recommendation
from .repository import repository


class AuditoriaInterpreter:
    """Generates narrative insights based on historical IA records."""

    def __init__(self, modulo: str = "auditoria") -> None:
        self._repo = repository
        self._modulo = modulo

    def interpretar(self) -> List[Recommendation]:
        registros = [self._mapear_registro(r) for r in self._repo.fetch_auditoria_registros(self._modulo)]
        registros = [r for r in registros if r is not None]

        if len(registros) < 2:
            return [
                Recommendation(
                    mensaje="Aún no hay datos suficientes para comparar tendencias históricas.",
                    nivel="advertencia",
                )
            ]

        actual = registros[0]
        historico = registros[1:]

        promedios = {
            "tendencia_ventas": self._promedio(historico, "tendencia_ventas"),
            "dispersion_pesos": self._promedio(historico, "dispersion_pesos"),
            "correlacion_peso_ventas": self._promedio(historico, "correlacion_peso_ventas"),
            "riesgos_detectados": self._promedio(historico, "riesgos_detectados"),
        }

        mensajes: List[Recommendation] = []
        mensajes.extend(self._analizar_tendencia(actual, promedios["tendencia_ventas"]))
        mensajes.extend(self._analizar_dispersion(actual, promedios["dispersion_pesos"]))
        mensajes.extend(self._analizar_correlacion(actual, promedios["correlacion_peso_ventas"]))
        mensajes.extend(self._analizar_riesgos(actual, promedios["riesgos_detectados"]))

        if actual.estado and actual.estado.lower() in {"critico", "inestable"}:
            mensajes.append(
                Recommendation(
                    mensaje="El último registro del sistema fue catalogado como crítico. Valide alertas recientes y ejecute calibraciones prioritarias.",
                    nivel="critico",
                )
            )
        elif actual.estado and actual.estado.lower() in {"advertencia", "con advertencias"}:
            mensajes.append(
                Recommendation(
                    mensaje="El estado general se reporta con advertencias. Mantenga seguimiento cercano a las incidencias detectadas.",
                    nivel="advertencia",
                )
            )
        else:
            mensajes.append(
                Recommendation(
                    mensaje="No se observan anomalías adicionales al comparar el estado actual con los registros previos.",
                    nivel="normal",
                )
            )

        return mensajes

    # ------------------------------------------------------------------
    def _mapear_registro(self, registro: dict) -> Optional[AuditoriaRegistro]:
        try:
            return AuditoriaRegistro(
                fecha=registro.get("fecha"),
                tendencia_ventas=self._to_float(registro.get("tendencia_ventas")),
                dispersion_pesos=self._to_float(registro.get("dispersion_pesos")),
                correlacion_peso_ventas=self._to_float(registro.get("correlacion_peso_ventas")),
                riesgos_detectados=self._to_int(registro.get("riesgos_detectados")),
                estado=registro.get("estado"),
            )
        except Exception:
            return None

    def _promedio(self, registros: List[AuditoriaRegistro], campo: str) -> Optional[float]:
        valores = [getattr(r, campo) for r in registros if getattr(r, campo) is not None]
        if not valores:
            return None
        return float(statistics.mean(valores))

    def _analizar_tendencia(self, actual: AuditoriaRegistro, referencia: Optional[float]) -> List[Recommendation]:
        if actual.tendencia_ventas is None or referencia is None:
            return []
        delta = actual.tendencia_ventas - referencia
        if delta > 0.08:
            return [
                Recommendation(
                    mensaje="Las ventas muestran un crecimiento aproximado del {porc:.0f} % sobre el promedio histórico.".format(
                        porc=abs(delta) * 100
                    ),
                    nivel="advertencia",
                )
            ]
        if delta < -0.08:
            return [
                Recommendation(
                    mensaje="La tendencia de ventas cayó cerca del {porc:.0f} % respecto al comportamiento previo. Revise campañas y surtido.".format(
                        porc=abs(delta) * 100
                    ),
                    nivel="advertencia",
                )
            ]
        return [
            Recommendation(
                mensaje="La tendencia de ventas se mantiene estable frente al promedio registrado.",
                nivel="normal",
            )
        ]

    def _analizar_dispersion(self, actual: AuditoriaRegistro, referencia: Optional[float]) -> List[Recommendation]:
        if actual.dispersion_pesos is None or referencia is None:
            return []
        delta = actual.dispersion_pesos - referencia
        if delta > 0.05:
            return [
                Recommendation(
                    mensaje="Las lecturas de peso presentan una dispersión superior al promedio. Inspeccione calibraciones recientes.",
                    nivel="critico",
                )
            ]
        if delta < -0.03:
            return [
                Recommendation(
                    mensaje="Las lecturas de peso muestran una dispersión menor al promedio histórico, lo que indica estabilidad en los sensores.",
                    nivel="normal",
                )
            ]
        return [
            Recommendation(
                mensaje="La variación de peso permanece alineada con los registros anteriores.",
                nivel="normal",
            )
        ]

    def _analizar_correlacion(self, actual: AuditoriaRegistro, referencia: Optional[float]) -> List[Recommendation]:
        if actual.correlacion_peso_ventas is None or referencia is None:
            return []
        delta = actual.correlacion_peso_ventas - referencia
        if delta > 0.4:
            return [
                Recommendation(
                    mensaje="La correlación peso-ventas aumentó de forma atípica. Revise integridad de registros y lecturas duplicadas.",
                    nivel="advertencia",
                )
            ]
        if delta < -0.4:
            return [
                Recommendation(
                    mensaje="La correlación peso-ventas se mantuvo negativa, confirmando coherencia entre ventas y consumo físico.",
                    nivel="normal",
                )
            ]
        return [
            Recommendation(
                mensaje="No se observan variaciones relevantes en la correlación entre peso e ingresos registrados.",
                nivel="normal",
            )
        ]

    def _analizar_riesgos(self, actual: AuditoriaRegistro, referencia: Optional[float]) -> List[Recommendation]:
        if actual.riesgos_detectados is None or referencia is None:
            return []
        delta = actual.riesgos_detectados - referencia
        if delta >= 2:
            return [
                Recommendation(
                    mensaje="El número de riesgos detectados aumentó en aproximadamente {porc:.0f} unidades respecto a la semana anterior. Revise alertas y calibraciones.".format(
                        porc=delta
                    ),
                    nivel="critico" if delta >= 4 else "advertencia",
                )
            ]
        if delta <= -2:
            return [
                Recommendation(
                    mensaje="La cantidad de riesgos detectados disminuyó en comparación con el histórico reciente, indicando mejoras operacionales.",
                    nivel="normal",
                )
            ]
        return [
            Recommendation(
                mensaje="Los riesgos registrados se mantienen en niveles similares a periodos anteriores.",
                nivel="normal",
            )
        ]

    @staticmethod
    def _to_float(value: Optional[float]) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value: Optional[int]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
