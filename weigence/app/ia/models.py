"""Data models for the internal IA engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MetricSnapshot:
    """Aggregated metrics captured from operational data sources."""

    tendencia_ventas: Optional[float] = None
    dispersion_pesos: Optional[float] = None
    correlacion_peso_ventas: Optional[float] = None
    riesgos_detectados: int = 0
    riesgos_detalle: List[str] = field(default_factory=list)
    estado_operativo: str = "estable"


@dataclass
class SystemContext:
    """Represents the current context of the platform used to tailor insights."""

    momento: str = "día"
    estado: str = "estable"
    alertas_criticas: int = 0
    estantes_al_limite: int = 0
    ultimo_evento: Optional[str] = None


@dataclass
class Recommendation:
    """Textual recommendation enriched with a severity level."""

    mensaje: str
    nivel: str = "normal"
    categoria: Optional[str] = None


@dataclass
class AuditoriaRegistro:
    """Raw record retrieved from ia_registros."""

    fecha: str
    tendencia_ventas: Optional[float]
    dispersion_pesos: Optional[float]
    correlacion_peso_ventas: Optional[float]
    riesgos_detectados: Optional[int]
    estado: Optional[str]


@dataclass
class AuditoriaInsight(Recommendation):
    """Specialisation of Recommendation with contextual metadata."""

    tendencia_referencia: Optional[float] = None
    valor_actual: Optional[float] = None
