"""Analytical routines used by the IA engine."""
from __future__ import annotations

import math
from datetime import datetime
from typing import Iterable, List, Optional

import numpy as np

from .models import MetricSnapshot, SystemContext
from .repository import repository


class MetricAnalyzer:
    """Builds metric snapshots from transactional data."""

    def __init__(self) -> None:
        self._repo = repository

    def snapshot(self) -> MetricSnapshot:
        productos = self._repo.fetch_products()
        ventas = self._repo.fetch_sales(limit=60)
        ventas_detalle = self._repo.fetch_sales_details()
        pesajes = self._repo.fetch_weights(limit=200)

        tendencia = self._calc_tendencia_ventas(ventas)
        dispersion = self._calc_dispersion_pesos(pesajes)
        correlacion = self._calc_correlacion_peso_ventas(pesajes, ventas)
        riesgos, detalles = self._calc_riesgos_stock(productos, ventas_detalle)
        estado = self._calc_estado_operativo(riesgos, dispersion)

        return MetricSnapshot(
            tendencia_ventas=tendencia,
            dispersion_pesos=dispersion,
            correlacion_peso_ventas=correlacion,
            riesgos_detectados=riesgos,
            riesgos_detalle=detalles,
            estado_operativo=estado,
        )

    # --- métricas individuales -------------------------------------------------
    def _calc_tendencia_ventas(self, ventas: Iterable[dict], dias: int = 14) -> Optional[float]:
        filtradas = [
            (idx, float(v.get("total", 0)))
            for idx, v in enumerate(sorted(ventas, key=lambda x: x.get("fecha_venta") or ""))
            if v.get("total") is not None and v.get("fecha_venta")
        ]
        if len(filtradas) < 5:
            return None

        valores = np.array([valor for _, valor in filtradas[-dias:]])
        if valores.size < 3:
            return None

        x = np.arange(valores.size)
        y = valores
        m, _ = np.polyfit(x, y, 1)
        promedio = np.mean(y) or 1e-6
        tendencia = 1 + (m / promedio)
        return round(float(tendencia), 2)

    def _calc_dispersion_pesos(self, pesajes: Iterable[dict]) -> Optional[float]:
        valores = [float(p.get("peso_unitario")) for p in pesajes if p.get("peso_unitario") not in (None, "")]
        if len(valores) < 5:
            return None

        media = float(np.mean(valores))
        if math.isclose(media, 0, abs_tol=1e-6):
            return None
        desv = float(np.std(valores))
        return round(desv / media, 3)

    def _calc_correlacion_peso_ventas(
        self, pesajes: Iterable[dict], ventas: Iterable[dict], muestras: int = 15
    ) -> Optional[float]:
        pesajes_filtrados = [
            (
                p.get("fecha_pesaje") or "",
                float(p.get("peso_unitario")),
            )
            for p in pesajes
            if p.get("peso_unitario") is not None
        ]
        ventas_filtradas = [
            (
                v.get("fecha_venta") or "",
                float(v.get("total")),
            )
            for v in ventas
            if v.get("total") is not None
        ]

        pesajes_ordenados = [valor for _, valor in sorted(pesajes_filtrados, key=lambda x: x[0])][-muestras:]
        ventas_ordenadas = [valor for _, valor in sorted(ventas_filtradas, key=lambda x: x[0])][-muestras:]

        serie_pesajes = pesajes_ordenados
        serie_ventas = ventas_ordenadas

        min_len = min(len(serie_pesajes), len(serie_ventas))
        if min_len < 3:
            return None

        corr = float(np.corrcoef(serie_pesajes[:min_len], serie_ventas[:min_len])[0, 1])
        return round(corr, 2)

    def _calc_riesgos_stock(self, productos: Iterable[dict], ventas_detalle: Iterable[dict]) -> tuple[int, List[str]]:
        consumo: dict[int, float] = {}
        for detalle in ventas_detalle:
            producto = detalle.get("idproducto")
            cantidad = detalle.get("cantidad")
            if not producto or cantidad is None:
                continue
            consumo[producto] = consumo.get(producto, 0.0) + float(cantidad)

        total_registros = max(len(ventas_detalle), 1)
        riesgos: List[str] = []
        for prod in productos:
            prod_id = prod.get("idproducto")
            stock = float(prod.get("stock") or 0)
            ritmo = consumo.get(prod_id, 0.0) / total_registros
            if ritmo <= 0:
                continue
            dias_restantes = stock / ritmo if ritmo else 0
            if dias_restantes < 3:
                nombre = prod.get("nombre") or f"Producto {prod_id}"
                riesgos.append(
                    (
                        "El producto {nombre} podría agotarse en aproximadamente {dias:.1f} días."
                    ).format(nombre=nombre, dias=dias_restantes)
                )

        return len(riesgos), riesgos

    def _calc_estado_operativo(self, riesgos: int, dispersion: Optional[float]) -> str:
        dispersion = dispersion or 0
        if riesgos > 5 or dispersion > 0.2:
            return "critico"
        if riesgos > 0 or dispersion > 0.1:
            return "advertencia"
        return "estable"


class ContextAnalyzer:
    """Determines the operational context of the platform."""

    def __init__(self) -> None:
        self._repo = repository

    def contexto(self) -> SystemContext:
        alertas = self._repo.fetch_alerts()
        estantes = self._repo.fetch_shelves()
        eventos = self._repo.fetch_system_events(limit=1)

        criticas = sum(1 for a in alertas if (a.get("tipo_color") or "").lower() == "rojo")
        estantes_al_limite = 0
        for est in estantes:
            try:
                maximo = float(est.get("peso_maximo") or 0)
                actual = float(est.get("peso_actual") or 0)
            except (TypeError, ValueError):
                continue
            if maximo <= 0:
                continue
            if actual >= 0.95 * maximo:
                estantes_al_limite += 1

        return SystemContext(
            momento=self._momento_actual(),
            estado=self._evaluar_estado(criticas, estantes_al_limite),
            alertas_criticas=criticas,
            estantes_al_limite=estantes_al_limite,
            ultimo_evento=eventos[0].get("mensaje") if eventos else None,
        )

    def _momento_actual(self) -> str:
        hora = datetime.now().hour
        if 6 <= hora < 12:
            return "mañana"
        if 12 <= hora < 18:
            return "tarde"
        if 18 <= hora < 23:
            return "noche"
        return "madrugada"

    def _evaluar_estado(self, criticas: int, estantes_al_limite: int) -> str:
        if criticas >= 3 or estantes_al_limite >= 5:
            return "critico"
        if criticas or estantes_al_limite:
            return "advertencia"
        return "normal"
