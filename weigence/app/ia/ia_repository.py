"""Data access layer for the IA engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import logging
from typing import Any, Dict, List

from api.conexion_supabase import supabase

logger = logging.getLogger(__name__)


@dataclass
class AuditLogPayload:
    """Structure used when persisting IA audit executions."""

    timestamp: datetime
    tipo: str
    severidad: str
    titulo: str
    mensaje: str
    solucion: str
    metadata: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        payload = {
            "timestamp": self.timestamp.isoformat(),
            "tipo_auditoria": self.tipo,
            "severidad": self.severidad,
            "titulo": self.titulo,
            "mensaje": self.mensaje,
            "solucion": self.solucion,
            "metadata": json.dumps(self.metadata, ensure_ascii=False),
        }
        return payload


class IARepository:
    """Wrapper around Supabase queries used by the IA engine."""

    def __init__(self) -> None:
        self._client = supabase

    def _execute(self, query: Any) -> List[Dict[str, Any]]:
        try:
            response = query.execute()
            return response.data or []
        except Exception:  # pragma: no cover - logging defensive
            logger.exception("Error executing Supabase query")
            return []

    # ------------------------------------------------------------------
    # Fetch helpers
    # ------------------------------------------------------------------
    def obtener_ventas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        query = (
            self._client.table("ventas")
            .select("total,fecha_venta")
            .gte("fecha_venta", desde.isoformat())
            .order("fecha_venta", desc=True)
        )
        return self._execute(query)

    def obtener_detalle_ventas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        query = (
            self._client.table("detalle_ventas")
            .select("idproducto,cantidad,fecha_detalle")
            .gte("fecha_detalle", desde.isoformat())
            .order("fecha_detalle", desc=True)
        )
        return self._execute(query)

    def obtener_pesajes_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        query = (
            self._client.table("pesajes")
            .select("peso_unitario,fecha_pesaje")
            .gte("fecha_pesaje", desde.isoformat())
            .order("fecha_pesaje", desc=True)
        )
        return self._execute(query)

    def obtener_alertas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        query = (
            self._client.table("alertas")
            .select("id,tipo_color,titulo,estado,fecha_creacion")
            .gte("fecha_creacion", desde.isoformat())
            .order("fecha_creacion", desc=True)
        )
        return self._execute(query)

    def obtener_movimientos_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        query = (
            self._client.table("movimientos_inventario")
            .select("tipo_evento,rut_usuario,timestamp,detalle")
            .gte("timestamp", desde.isoformat())
            .order("timestamp", desc=True)
        )
        return self._execute(query)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def registrar_evento_auditoria(self, payload: AuditLogPayload) -> bool:
        """Persist the generated recommendation in Supabase."""

        data = payload.as_dict()
        try:
            self._client.table("ia_auditoria_logs").insert(data).execute()
            return True
        except Exception:
            logger.exception("Fallo al registrar auditoría en ia_auditoria_logs; intentando fallback")

        # Fallback: reutilizamos la tabla histórica ia_registros con los campos disponibles
        fallback_payload = {
            "fecha": data["timestamp"],
            "modulo": payload.tipo,
            "tendencia_ventas": payload.metadata.get("trend_percent", 0.0),
            "dispersion_pesos": payload.metadata.get("weight_volatility", 0.0),
            "correlacion_peso_ventas": payload.metadata.get("inventory_pressure", 0.0),
            "riesgos_detectados": f"{payload.titulo} — {payload.mensaje[:180]}",
            "estado": payload.severidad,
        }
        try:
            self._client.table("ia_registros").insert(fallback_payload).execute()
            return True
        except Exception:
            logger.exception("Error insertando registro IA en fallback")
            return False


repository = IARepository()
