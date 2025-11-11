"""IA snapshots common utilities."""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Protocol, Union, runtime_checkable

@runtime_checkable
class SnapshotProtocol(Protocol):
    """Protocol for snapshot classes."""
    sales_trend_percent: float
    last_sale_total: float
    baseline_sale: float
    sales_volatility: float
    sales_anomaly_score: float
    weight_volatility: float
    weight_change_rate: float
    last_weight: float
    critical_alerts: Union[list, int]
    warning_alerts: Union[list, int]
    info_alerts: Union[list, int]
    movements_per_hour: float
    inactivity_hours: float
    signal_strength: float
    pattern_flags: list


def snapshot_to_dict(snapshot: SnapshotProtocol) -> Dict[str, Any]:
    """Convert any snapshot type to dictionary."""

    if is_dataclass(snapshot):
        base = asdict(snapshot)
    else:
        base = dict(getattr(snapshot, "__dict__", {}))
    # Convert datetime objects to ISO format
    for key, value in base.items():
        if isinstance(value, datetime):
            base[key] = value.isoformat()
    return base


def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely cast value to float, returning default when unable.

    This protects against None values and non-numeric inputs.
    """
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_list(value: Any) -> list:
    """Return a list for list-like inputs; empty list for None or invalid types."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    # Try to coerce single items into a list
    return [value]