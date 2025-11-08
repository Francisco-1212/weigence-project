"""IA engine public interface."""
from .ia_service import IAService, generar_recomendacion_auditoria
from .ia_service_v2 import IAServiceV2, generar_recomendacion_auditoria_v2

__all__ = [
    "IAService",
    "generar_recomendacion_auditoria",
    "IAServiceV2",
    "generar_recomendacion_auditoria_v2",
]
