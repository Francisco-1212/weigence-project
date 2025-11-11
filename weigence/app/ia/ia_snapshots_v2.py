"""Análisis y captura de estado para recomendaciones IA.

Este módulo define `IASnapshot`, una clase ligera que normaliza los datos
recibidos desde la capa de snapshot/repository y expone `to_dict()` para
serialización segura.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

from .ia_snapshot_utils import snapshot_to_dict, SnapshotProtocol, safe_float, safe_list

logger = logging.getLogger(__name__)


class IASnapshot(SnapshotProtocol):
    """Captura del estado actual del sistema para análisis.

    Usa funciones `safe_*` para normalizar valores faltantes o None y evitar
    excepciones al convertir tipos.
    """

    def __init__(self, data: Dict[str, Any]):
        """Inicializa snapshot con datos actuales.

        `data` suele ser un diccionario extraído de la base de datos o generado
        por el servicio. Se toleran entradas incompletas.
        """
        if not isinstance(data, dict):
            logger.warning("[IASnapshot] data no es un dict: %r", data)
            data = {}  # normalizar para evitar errores

        logger.debug("[IASnapshot] Inicializando con datos: %s", list(data.keys()))

        # Tendencias de ventas
        self.sales_trend_percent = safe_float(data.get('sales_trend_percent', 0))
        self.last_sale_total = safe_float(data.get('last_sale_total', 0))
        self.baseline_sale = safe_float(data.get('baseline_sale', 0))
        self.sales_volatility = safe_float(data.get('sales_volatility', 0))
        self.sales_anomaly_score = safe_float(data.get('sales_anomaly_score', 0))

        # Estado del inventario
        self.weight_volatility = safe_float(data.get('weight_volatility', 0))
        self.weight_change_rate = safe_float(data.get('weight_change_rate', 0))
        self.last_weight = safe_float(data.get('last_weight', 0))

        # Alertas activas
        self.critical_alerts = safe_list(data.get('critical_alerts', []))
        self.warning_alerts = safe_list(data.get('warning_alerts', []))
        self.info_alerts = safe_list(data.get('info_alerts', []))

        # Actividad del sistema
        self.movements_per_hour = safe_float(data.get('movements_per_hour', 0))
        self.inactivity_hours = safe_float(data.get('inactivity_hours', 0))
        self.signal_strength = safe_float(data.get('signal_strength', 100))

        # Patrones detectados
        self.pattern_flags = safe_list(data.get('pattern_flags', []))

    def __str__(self) -> str:
        """Representación en string para logs."""
        return f"IASnapshot(sales_trend={self.sales_trend_percent:.2f}, alerts={len(self.critical_alerts)})"

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el snapshot a un diccionario serializable."""
        return snapshot_to_dict(self)