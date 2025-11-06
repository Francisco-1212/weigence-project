"""IA engine public interface."""
from .service import IAService, ia_service
from .models import Recommendation

__all__ = ["IAService", "ia_service", "Recommendation"]
