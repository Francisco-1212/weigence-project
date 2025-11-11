"""IA engine public interface."""
from .ia_service import IAService, generar_recomendacion

__all__ = [
    "IAService",
    "generar_recomendacion",
]
