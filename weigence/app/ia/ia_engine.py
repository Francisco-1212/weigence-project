"""Rule engine that combines heuristics, anomalies and pattern inference."""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Optional

from .ia_snapshots import IASnapshot


@dataclass
class EngineInsight:
    """Structured insight produced by the engine prior to formatting."""

    key: str
    severity: str
    confidence: float
    summary: str
    drivers: List[str]
    data_points: Dict[str, float]


class IAEngine:
    """Combines multiple heuristics to derive a single actionable insight."""

    _SEVERITY_SCORE = {"critical": 3, "warning": 2, "info": 1}
    _KNOWN_KEYS = {
        "sales_collapse",
        "inventory_instability",
        "alert_pressure",
        "operational_inertia",
        "positive_outlook",
        "stable_outlook",
    }

    def evaluate(self, snapshot: IASnapshot) -> EngineInsight:
        candidates: List[EngineInsight] = []
        for generator in (
            self._regla_colapso_ventas,
            self._regla_inestabilidad_inventario,
            self._regla_presion_alertas,
            self._regla_inactividad_operativa,
            self._regla_tendencia_positiva,
        ):
            insight = generator(snapshot)
            if insight:
                candidates.append(insight)

        if not candidates:
            return self._sanitizar(self._default(snapshot))

        candidates.sort(key=self._prioridad, reverse=True)
        mejor = candidates[0]
        return self._sanitizar(mejor)

    # ------------------------------------------------------------------
    # Reglas específicas
    # ------------------------------------------------------------------
    def _regla_colapso_ventas(self, snapshot: IASnapshot) -> Optional[EngineInsight]:
        if snapshot.sales_trend_percent >= -0.18 and snapshot.sales_anomaly_score >= -1.4:
            return None

        severidad = "critical" if snapshot.sales_trend_percent <= -0.35 or snapshot.critical_alerts else "warning"
        drivers: List[str] = []
        if snapshot.critical_alerts:
            drivers.append(f"{snapshot.critical_alerts} alertas críticas activas")
        if snapshot.inactivity_hours >= 2:
            drivers.append(f"{snapshot.inactivity_hours:.1f}h sin movimientos relevantes")
        if snapshot.weight_change_rate <= -0.1:
            drivers.append("descenso de inventario detectado")

        data = {
            "trend_percent": snapshot.sales_trend_percent,
            "anomaly_score": snapshot.sales_anomaly_score,
            "weight_change": snapshot.weight_change_rate,
            "inactivity_hours": snapshot.inactivity_hours,
            "movements_per_hour": snapshot.movements_per_hour,
        }
        summary = "Caída abrupta del ritmo de ventas"
        return EngineInsight(
            key="sales_collapse",
            severity=severidad,
            confidence=min(0.98, 0.55 + abs(snapshot.sales_trend_percent) + abs(snapshot.sales_anomaly_score) / 2),
            summary=summary,
            drivers=drivers,
            data_points=data,
        )

    def _regla_inestabilidad_inventario(self, snapshot: IASnapshot) -> Optional[EngineInsight]:
        if snapshot.weight_volatility < 0.2 and abs(snapshot.weight_change_rate) < 0.08:
            return None
        severidad = "warning"
        if snapshot.weight_change_rate <= -0.18 or (snapshot.weight_volatility >= 0.3 and snapshot.sales_trend_percent <= -0.1):
            severidad = "critical"
        drivers = [
            f"Variación relativa de peso {snapshot.weight_volatility:.2f}",
        ]
        if snapshot.weight_change_rate < 0:
            drivers.append(f"Consumo acelerado de inventario ({snapshot.weight_change_rate:.2f})")
        data = {
            "weight_volatility": snapshot.weight_volatility,
            "weight_change": snapshot.weight_change_rate,
            "trend_percent": snapshot.sales_trend_percent,
            "alerts_warning": snapshot.warning_alerts,
        }
        summary = "Inventario con variaciones fuera de lo normal"
        return EngineInsight(
            key="inventory_instability",
            severity=severidad,
            confidence=min(0.9, 0.4 + snapshot.weight_volatility + abs(snapshot.weight_change_rate)),
            summary=summary,
            drivers=drivers,
            data_points=data,
        )

    def _regla_presion_alertas(self, snapshot: IASnapshot) -> Optional[EngineInsight]:
        if snapshot.critical_alerts + snapshot.warning_alerts < 4:
            return None
        severidad = "critical" if snapshot.critical_alerts >= 2 else "warning"
        drivers = [
            f"{snapshot.critical_alerts} alertas críticas",
            f"{snapshot.warning_alerts} advertencias técnicas",
        ]
        data = {
            "critical_alerts": snapshot.critical_alerts,
            "warning_alerts": snapshot.warning_alerts,
            "signal_strength": snapshot.signal_strength,
            "trend_percent": snapshot.sales_trend_percent,
        }
        summary = "Alta presión de alertas operativas"
        return EngineInsight(
            key="alert_pressure",
            severity=severidad,
            confidence=min(0.88, 0.45 + snapshot.signal_strength + 0.1 * snapshot.critical_alerts),
            summary=summary,
            drivers=drivers,
            data_points=data,
        )

    def _regla_inactividad_operativa(self, snapshot: IASnapshot) -> Optional[EngineInsight]:
        if snapshot.movements_per_hour >= 0.35 and snapshot.inactivity_hours < 3:
            return None
        if snapshot.sales_trend_percent > 0:
            return None
        severidad = "warning" if snapshot.inactivity_hours < 6 else "critical"
        drivers = [
            f"Solo {snapshot.movements_per_hour:.2f} movimientos/hora",
            f"Última actividad hace {snapshot.inactivity_hours:.1f}h",
        ]
        data = {
            "movements_per_hour": snapshot.movements_per_hour,
            "inactivity_hours": snapshot.inactivity_hours,
            "trend_percent": snapshot.sales_trend_percent,
        }
        summary = "Actividad operativa irregular"
        return EngineInsight(
            key="operational_inertia",
            severity=severidad,
            confidence=min(0.85, 0.5 + snapshot.inactivity_hours / 6 + abs(snapshot.sales_trend_percent)),
            summary=summary,
            drivers=drivers,
            data_points=data,
        )

    def _regla_tendencia_positiva(self, snapshot: IASnapshot) -> Optional[EngineInsight]:
        if snapshot.sales_trend_percent <= 0.12 and snapshot.weight_change_rate <= 0.02:
            return None
        if "sales_drop" in snapshot.pattern_flags:
            return None
        drivers = []
        if snapshot.sales_trend_percent > 0:
            drivers.append(f"Ventas creciendo {snapshot.sales_trend_percent * 100:.1f}%")
        if snapshot.weight_change_rate >= 0.05:
            drivers.append("Inventario recuperándose")
        data = {
            "trend_percent": snapshot.sales_trend_percent,
            "weight_change": snapshot.weight_change_rate,
            "signal_strength": snapshot.signal_strength,
        }
        summary = "Tendencia positiva consolidándose"
        return EngineInsight(
            key="positive_outlook",
            severity="info",
            confidence=min(0.8, 0.45 + snapshot.signal_strength + snapshot.sales_trend_percent),
            summary=summary,
            drivers=drivers,
            data_points=data,
        )

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------
    def _default(self, snapshot: IASnapshot) -> EngineInsight:
        data = {
            "trend_percent": snapshot.sales_trend_percent,
            "weight_volatility": snapshot.weight_volatility,
            "alerts_total": sum(snapshot.alerts_summary.values()),
        }
        summary = "Comportamiento operativo estable"
        return EngineInsight(
            key="stable_outlook",
            severity="info",
            confidence=0.45,
            summary=summary,
            drivers=["Sin anomalías relevantes detectadas"],
            data_points=data,
        )

    def _prioridad(self, insight: EngineInsight) -> float:
        severidad = self._SEVERITY_SCORE.get(insight.severity, 1)
        return severidad * 10 + insight.confidence

    def _sanitizar(self, insight: EngineInsight) -> EngineInsight:
        """Normalize the insight so the formatter receives consistent payloads."""

        key = insight.key if insight.key in self._KNOWN_KEYS else "stable_outlook"
        severity = insight.severity if insight.severity in self._SEVERITY_SCORE else "info"
        confidence = min(max(float(insight.confidence or 0.0), 0.0), 1.0)
        summary = insight.summary or "Sin hallazgos destacados"
        drivers = [driver for driver in insight.drivers if driver]
        data_points: Dict[str, float] = {}
        for clave, valor in insight.data_points.items():
            try:
                data_points[clave] = float(valor)
            except (TypeError, ValueError):
                continue

        if not data_points:
            data_points = {"trend_percent": 0.0}

        return replace(
            insight,
            key=key,
            severity=severity,
            confidence=confidence,
            summary=summary,
            drivers=drivers,
            data_points=data_points,
        )


engine = IAEngine()
