"""Snapshot builder that aggregates recent operational data."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, pstdev
from typing import Any, Dict, Iterable, List, Optional

from .ia_repository import IARepository, repository


@dataclass
class IASnapshot:
    """Aggregated metrics that describe the operational context."""

    generated_at: datetime
    sales_window_hours: int
    weight_window_hours: int
    movement_window_hours: int
    sales_totals: List[float] = field(default_factory=list)
    sales_trend_percent: float = 0.0
    sales_anomaly_score: float = 0.0
    sales_volatility: float = 0.0
    last_sale_total: Optional[float] = None
    baseline_sale: Optional[float] = None
    weight_values: List[float] = field(default_factory=list)
    weight_volatility: float = 0.0
    weight_change_rate: float = 0.0
    last_weight: Optional[float] = None
    alerts_summary: Dict[str, int] = field(default_factory=dict)
    movements_per_hour: float = 0.0
    inactivity_hours: float = 0.0
    pattern_flags: List[str] = field(default_factory=list)
    signal_strength: float = 0.0

    @property
    def critical_alerts(self) -> int:
        return self.alerts_summary.get("critical", 0)

    @property
    def warning_alerts(self) -> int:
        return self.alerts_summary.get("warning", 0)

    @property
    def info_alerts(self) -> int:
        return self.alerts_summary.get("info", 0)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        from .ia_snapshot_utils import snapshot_to_dict
        return snapshot_to_dict(self)


class SnapshotBuilder:
    """Coordinates data extraction and transformation into an IASnapshot."""

    def __init__(self, repo: IARepository | None = None) -> None:
        self._repo = repo or repository

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build(self, contexto: str | None = None) -> IASnapshot:
        ahora = datetime.utcnow()
        sales_window = 48 if contexto != "inventario" else 72
        weight_window = 72
        movement_window = 48

        ventas = self._repo.obtener_ventas_desde(ahora - timedelta(hours=sales_window))
        detalles = self._repo.obtener_detalle_ventas_desde(ahora - timedelta(hours=sales_window))
        pesajes = self._repo.obtener_pesajes_desde(ahora - timedelta(hours=weight_window))
        alertas = self._repo.obtener_alertas_desde(ahora - timedelta(hours=movement_window))
        movimientos = self._repo.obtener_movimientos_desde(ahora - timedelta(hours=movement_window))

        snapshot = IASnapshot(
            generated_at=ahora,
            sales_window_hours=sales_window,
            weight_window_hours=weight_window,
            movement_window_hours=movement_window,
        )

        self._enriquecer_ventas(snapshot, ventas)
        self._enriquecer_pesajes(snapshot, pesajes)
        self._enriquecer_alertas(snapshot, alertas)
        self._enriquecer_movimientos(snapshot, movimientos)
        self._inferir_patrones(snapshot, detalles)

        return snapshot

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ordenar_por_fecha(self, items: Iterable[Dict[str, object]], campo: str) -> List[Dict[str, object]]:
        def _parse(item: Dict[str, object]) -> datetime:
            valor = item.get(campo)
            if isinstance(valor, datetime):
                return valor
            if isinstance(valor, str):
                try:
                    return datetime.fromisoformat(valor.replace("Z", "+00:00"))
                except ValueError:
                    return datetime.utcnow()
            return datetime.utcnow()

        return sorted(items, key=_parse)

    def _enriquecer_ventas(self, snapshot: IASnapshot, ventas: List[Dict[str, object]]) -> None:
        if not ventas:
            return

        ordenadas = self._ordenar_por_fecha(ventas, "fecha_venta")
        totales = [float(item.get("total") or 0.0) for item in ordenadas]
        snapshot.sales_totals = totales
        snapshot.last_sale_total = totales[-1] if totales else None
        snapshot.baseline_sale = mean(totales[:-1]) if len(totales) > 1 else (totales[0] if totales else None)

        if len(totales) > 1:
            snapshot.sales_volatility = self._calcular_volatilidad(totales)
            snapshot.sales_anomaly_score = self._calcular_z_score(totales)
            snapshot.sales_trend_percent = self._calcular_tendencia(totales)
        else:
            snapshot.sales_volatility = 0.0
            snapshot.sales_anomaly_score = 0.0
            snapshot.sales_trend_percent = 0.0

    def _enriquecer_pesajes(self, snapshot: IASnapshot, pesajes: List[Dict[str, object]]) -> None:
        if not pesajes:
            return

        ordenadas = self._ordenar_por_fecha(pesajes, "fecha_pesaje")
        valores = [float(item.get("peso_unitario") or 0.0) for item in ordenadas]
        snapshot.weight_values = valores
        snapshot.last_weight = valores[-1] if valores else None

        if len(valores) > 1:
            snapshot.weight_volatility = self._calcular_volatilidad(valores)
            snapshot.weight_change_rate = self._calcular_cambio_relativo(valores)
        else:
            snapshot.weight_volatility = 0.0
            snapshot.weight_change_rate = 0.0

    def _enriquecer_alertas(self, snapshot: IASnapshot, alertas: List[Dict[str, object]]) -> None:
        resumen = {"critical": 0, "warning": 0, "info": 0}
        for alerta in alertas:
            clave = (alerta.get("tipo_color") or "").lower()
            if "rojo" in clave or "crit" in clave:
                resumen["critical"] += 1
            elif "amar" in clave or "warn" in clave:
                resumen["warning"] += 1
            else:
                resumen["info"] += 1
        snapshot.alerts_summary = resumen

    def _enriquecer_movimientos(self, snapshot: IASnapshot, movimientos: List[Dict[str, object]]) -> None:
        if movimientos:
            intervalo_horas = snapshot.movement_window_hours or 1
            snapshot.movements_per_hour = len(movimientos) / intervalo_horas
            ordenadas = self._ordenar_por_fecha(movimientos, "timestamp")
            ultimo = ordenadas[-1]
            ultima_fecha = ultimo.get("timestamp")
            if isinstance(ultima_fecha, str):
                try:
                    ultima_fecha_dt = datetime.fromisoformat(ultima_fecha.replace("Z", "+00:00"))
                except ValueError:
                    ultima_fecha_dt = snapshot.generated_at
            elif isinstance(ultima_fecha, datetime):
                ultima_fecha_dt = ultima_fecha
            else:
                ultima_fecha_dt = snapshot.generated_at
            snapshot.inactivity_hours = max(
                0.0,
                (snapshot.generated_at - ultima_fecha_dt).total_seconds() / 3600.0,
            )
        else:
            snapshot.movements_per_hour = 0.0
            snapshot.inactivity_hours = float(snapshot.movement_window_hours)

    def _inferir_patrones(
        self,
        snapshot: IASnapshot,
        detalles: List[Dict[str, object]],
    ) -> None:
        patrones: List[str] = []
        if snapshot.sales_trend_percent <= -0.2:
            patrones.append("sales_drop")
        if snapshot.sales_anomaly_score <= -1.8:
            patrones.append("sudden_collapse")
        if snapshot.weight_change_rate <= -0.12:
            patrones.append("inventory_loss")
        if snapshot.weight_volatility >= 0.22:
            patrones.append("weight_instability")
        if snapshot.movements_per_hour <= 0.25:
            patrones.append("low_activity")
        if snapshot.inactivity_hours >= 3:
            patrones.append("extended_inactivity")
        if snapshot.critical_alerts >= 2:
            patrones.append("alert_pressure")
        if snapshot.sales_trend_percent >= 0.15 and snapshot.weight_change_rate >= 0.05:
            patrones.append("positive_recovery")

        # Analizamos velocidad de venta de productos para detectar patrones complementarios
        top_items = self._productos_con_mayor_variacion(detalles)
        if top_items and top_items[0][1] > 0:
            patrones.append("fast_moving_items")

        snapshot.pattern_flags = patrones
        snapshot.signal_strength = min(
            1.0,
            abs(snapshot.sales_trend_percent) * 1.5
            + abs(snapshot.weight_change_rate) * 1.3
            + snapshot.critical_alerts * 0.2,
        )

    # ------------------------------------------------------------------
    # Numeric utilities
    # ------------------------------------------------------------------
    def _calcular_volatilidad(self, valores: List[float]) -> float:
        if not valores:
            return 0.0
        promedio = mean(valores)
        if promedio == 0:
            return 0.0
        if len(valores) == 1:
            return 0.0
        return pstdev(valores) / abs(promedio)

    def _calcular_z_score(self, valores: List[float]) -> float:
        if len(valores) < 2:
            return 0.0
        promedio = mean(valores[:-1]) if len(valores) > 2 else mean(valores)
        desviacion = pstdev(valores)
        if desviacion == 0:
            return 0.0
        ultimo = valores[-1]
        return (ultimo - promedio) / desviacion

    def _calcular_tendencia(self, valores: List[float]) -> float:
        if len(valores) < 3:
            return 0.0
        tercio = max(1, len(valores) // 3)
        recientes = valores[-tercio:]
        anteriores = valores[:tercio]
        if not anteriores:
            return 0.0
        prom_reciente = mean(recientes)
        prom_anterior = mean(anteriores)
        if prom_anterior == 0:
            return 0.0
        return (prom_reciente - prom_anterior) / abs(prom_anterior)

    def _calcular_cambio_relativo(self, valores: List[float]) -> float:
        if len(valores) < 3:
            return 0.0
        recientes = valores[-3:]
        anteriores = valores[:3]
        prom_reciente = mean(recientes)
        prom_anterior = mean(anteriores)
        if prom_anterior == 0:
            return 0.0
        return (prom_reciente - prom_anterior) / abs(prom_anterior)

    def _productos_con_mayor_variacion(
        self,
        detalles: List[Dict[str, object]],
    ) -> List[tuple[str, float]]:
        conteo: Dict[str, float] = {}
        for item in detalles:
            producto = str(item.get("idproducto"))
            cantidad = float(item.get("cantidad") or 0.0)
            conteo[producto] = conteo.get(producto, 0.0) + cantidad
        ordenado = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        return ordenado[:5]


snapshot_builder = SnapshotBuilder()
