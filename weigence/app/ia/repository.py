"""Data access helpers for the IA engine."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from api.conexion_supabase import supabase

logger = logging.getLogger(__name__)


class SupabaseRepository:
    """Wrapper around Supabase client providing safe access helpers."""

    def __init__(self) -> None:
        self._client = supabase

    def _execute(self, query: Any) -> List[Dict[str, Any]]:
        try:
            response = query.execute()
            return response.data or []
        except Exception:
            logger.exception("Error executing Supabase query")
            return []

    def fetch_sales(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self._client.table("ventas").select("total,fecha_venta")
        if limit:
            query = query.order("fecha_venta", desc=True).limit(limit)
        return self._execute(query)

    def fetch_sales_details(self) -> List[Dict[str, Any]]:
        query = self._client.table("detalle_ventas").select("idproducto,cantidad")
        return self._execute(query)

    def fetch_weights(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        query = self._client.table("pesajes").select("peso_unitario,fecha_pesaje")
        if limit:
            query = query.order("fecha_pesaje", desc=True).limit(limit)
        return self._execute(query)

    def fetch_products(self) -> List[Dict[str, Any]]:
        query = self._client.table("productos").select("idproducto,nombre,stock")
        return self._execute(query)

    def fetch_shelves(self) -> List[Dict[str, Any]]:
        query = self._client.table("estantes").select("id_estante,peso_actual,peso_maximo")
        return self._execute(query)

    def fetch_alerts(self) -> List[Dict[str, Any]]:
        query = self._client.table("alertas").select("id,tipo_color,titulo,estado")
        return self._execute(query)

    def fetch_system_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        query = (
            self._client.table("eventos_sistema")
            .select("mensaje,tipo,timestamp")
            .order("timestamp", desc=True)
            .limit(limit)
        )
        return self._execute(query)

    def fetch_inventory_movements(self, limit: int = 50) -> List[Dict[str, Any]]:
        query = (
            self._client.table("movimientos_inventario")
            .select("tipo_evento,rut_usuario,timestamp")
            .order("timestamp", desc=True)
            .limit(limit)
        )
        return self._execute(query)

    def fetch_auditoria_registros(self, modulo: str, limit: int = 20) -> List[Dict[str, Any]]:
        query = (
            self._client.table("ia_registros")
            .select("fecha,modulo,tendencia_ventas,dispersion_pesos,correlacion_peso_ventas,riesgos_detectados,estado")
            .eq("modulo", modulo)
            .order("fecha", desc=True)
            .limit(limit)
        )
        return self._execute(query)

    def insert_auditoria_registro(self, payload: Dict[str, Any]) -> bool:
        try:
            self._client.table("ia_registros").insert(payload).execute()
            return True
        except Exception:
            logger.exception("Error inserting IA registry entry")
            return False


repository = SupabaseRepository()
