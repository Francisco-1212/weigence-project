"""Public service used by Flask routes and background jobs."""
from __future__ import annotations

from datetime import datetime
from typing import List

from .analyzers import ContextAnalyzer, MetricAnalyzer
from .auditoria import AuditoriaInterpreter
from .models import Recommendation
from .recommendations import RecommendationBuilder
from .repository import repository


class IAService:
    """Facade that exposes the capabilities of the IA engine."""

    def __init__(self) -> None:
        self._metric_analyzer = MetricAnalyzer()
        self._context_analyzer = ContextAnalyzer()
        self._builder = RecommendationBuilder()

    def build_header_recommendations(self, contexto: str | None = None) -> List[Recommendation]:
        snapshot = self._metric_analyzer.snapshot()
        ctx = self._context_analyzer.contexto()
        return self._builder.build_global(snapshot, ctx, contexto)

    def build_contextual_recommendations(self, modulo: str) -> List[Recommendation]:
        snapshot = self._metric_analyzer.snapshot()
        ctx = self._context_analyzer.contexto()
        return self._builder.build_contextual(snapshot, ctx, modulo)

    def interpretar_auditoria(self) -> List[Recommendation]:
        interpreter = AuditoriaInterpreter()
        return interpreter.interpretar()

    def registrar_snapshot(self, modulo: str = "auditoria") -> bool:
        snapshot = self._metric_analyzer.snapshot()
        payload = {
            "fecha": datetime.now().isoformat(),
            "modulo": modulo,
            "tendencia_ventas": snapshot.tendencia_ventas,
            "dispersion_pesos": snapshot.dispersion_pesos,
            "correlacion_peso_ventas": snapshot.correlacion_peso_ventas,
            "riesgos_detectados": snapshot.riesgos_detectados,
            "estado": snapshot.estado_operativo,
        }
        return repository.insert_auditoria_registro(payload)


ia_service = IAService()
