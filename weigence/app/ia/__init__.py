"""Paquete IA: solo exporta la clase base."""
from .ia_service import IAService
from .ia_ml_anomalies import AnomalyDetector, detect_anomalies

__all__ = ["IAService", "AnomalyDetector", "detect_anomalies"]
