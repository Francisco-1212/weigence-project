"""Contextos específicos para recomendaciones IA por página."""
from typing import Dict, List
from datetime import datetime, timedelta

class IAContextBuilder:
    """Genera contextos específicos para cada página."""

    def get_context_data(self, page: str, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Obtiene datos específicos según la página actual."""
        if page == "dashboard":
            return self._get_dashboard_context(snapshot)
        elif page == "inventario":
            return self._get_inventory_context(snapshot)
        elif page == "ventas":
            return self._get_sales_context(snapshot)
        elif page == "movimientos":
            return self._get_movements_context(snapshot)
        elif page == "alertas":
            return self._get_alerts_context(snapshot)
        elif page == "auditoria":
            return self._get_audit_context(snapshot)
        return {}

    def _get_dashboard_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para el dashboard."""
        return {
            "sales_trend": snapshot.sales_trend_percent,
            "critical_alerts": snapshot.critical_alerts,
            "warning_alerts": snapshot.warning_alerts,
            "movements_per_hour": snapshot.movements_per_hour,
            "inactivity_hours": snapshot.inactivity_hours,
            "signal_strength": snapshot.signal_strength,
            "patterns": snapshot.pattern_flags
        }

    def _get_inventory_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para inventario."""
        return {
            "weight_volatility": snapshot.weight_volatility,
            "weight_change": snapshot.weight_change_rate,
            "last_weight": snapshot.last_weight,
            "critical_alerts": snapshot.critical_alerts,
            "movements_per_hour": snapshot.movements_per_hour,
            "patterns": [p for p in snapshot.pattern_flags if "inventory" in p or "weight" in p]
        }

    def _get_sales_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para ventas."""
        return {
            "sales_trend": snapshot.sales_trend_percent,
            "last_sale": snapshot.last_sale_total,
            "baseline_sale": snapshot.baseline_sale,
            "sales_volatility": snapshot.sales_volatility,
            "anomaly_score": snapshot.sales_anomaly_score,
            "patterns": [p for p in snapshot.pattern_flags if "sales" in p]
        }

    def _get_movements_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para movimientos."""
        return {
            "movements_per_hour": snapshot.movements_per_hour,
            "inactivity_hours": snapshot.inactivity_hours,
            "weight_volatility": snapshot.weight_volatility,
            "patterns": [p for p in snapshot.pattern_flags if "activity" in p or "movement" in p]
        }

    def _get_alerts_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para alertas."""
        return {
            "critical_alerts": snapshot.critical_alerts,
            "warning_alerts": snapshot.warning_alerts,
            "info_alerts": snapshot.info_alerts,
            "signal_strength": snapshot.signal_strength,
            "patterns": [p for p in snapshot.pattern_flags if "alert" in p]
        }

    def _get_audit_context(self, snapshot: 'IASnapshot') -> Dict[str, object]:
        """Contextualiza datos para auditoría."""
        return {
            "sales_trend": snapshot.sales_trend_percent,
            "weight_change": snapshot.weight_change_rate,
            "critical_alerts": snapshot.critical_alerts,
            "movements_per_hour": snapshot.movements_per_hour,
            "signal_strength": snapshot.signal_strength,
            "patterns": snapshot.pattern_flags
        }