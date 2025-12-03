"""Data access layer for the IA engine."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List

from api.conexion_supabase import supabase

logger = logging.getLogger(__name__)


@dataclass
class AuditLogPayload:
    """Payload utilizado para persistir auditorías IA."""

    timestamp: datetime
    tipo: str
    severidad: str
    titulo: str
    mensaje: str
    solucion: str
    confianza: float
    metadata: Dict[str, float]

    def primary_record(self) -> Dict[str, Any]:
        """Transforma el payload al formato esperado por ia_auditoria_logs."""

        resultado = (
            f"[{self.severidad.upper()}] {self.titulo}. {self.mensaje} \nSolución sugerida: {self.solucion}"
        )
        return {
            "modulo": self.tipo,
            "resultado": resultado,
            "confianza": self.confianza,
            "fecha": self.timestamp.isoformat(),
        }

    def fallback_record(self) -> Dict[str, Any]:
        """Genera el registro compatible con la tabla histórica ia_registros."""

        return {
            "fecha": self.timestamp.isoformat(),
            "modulo": self.tipo,
            "tendencia_ventas": float(self.metadata.get("trend_percent", 0.0)),
            "dispersion_pesos": float(self.metadata.get("weight_volatility", 0.0)),
            "correlacion_peso_ventas": float(self.metadata.get("inventory_pressure", 0.0)),
            "riesgos_detectados": f"{self.titulo} — {self.mensaje[:180]}",
            "estado": self.severidad,
        }


class IARepository:
    """Wrapper around Supabase queries used by the IA engine."""

    def __init__(self) -> None:
        self._client = supabase

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------
    def _execute(self, query: Any, *, table: str, operation: str) -> List[Dict[str, Any]]:
        """Ejecuta consultas SELECT asegurando logs consistentes."""

        try:
            response = query.execute()
            return response.data or []
        except Exception:  # pragma: no cover - logging defensivo
            logger.exception("[IA] Error en %s sobre %s", operation, table)
            return []

    def _insert(self, table: str, payload: Dict[str, Any]) -> bool:
        """Centraliza inserciones en Supabase con manejo robusto de errores."""

        try:
            self._client.table(table).insert(payload).execute()
            return True
        except Exception:  # pragma: no cover - logging defensivo
            logger.exception("[IA] Error insertando en %s", table)
            return False

    def _fetch_since(
        self, *, table: str, columns: str, date_field: str, desde: datetime
    ) -> List[Dict[str, Any]]:
        """Obtiene registros filtrados por fecha usando una plantilla común."""

        query = (
            self._client.table(table)
            .select(columns)
            .gte(date_field, desde.isoformat())
            .order(date_field, desc=True)
        )
        return self._execute(query, table=table, operation="select")

    # ------------------------------------------------------------------
    # Fetch helpers
    # ------------------------------------------------------------------
    def obtener_ventas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        """Devuelve ventas registradas desde la fecha indicada."""

        return self._fetch_since(
            table="ventas",
            columns="total,fecha_venta",
            date_field="fecha_venta",
            desde=desde,
        )

    def obtener_detalle_ventas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        """Obtiene el detalle de ventas respetando el timestamp ya existente."""

        return self._fetch_since(
            table="detalle_ventas",
            columns="idproducto,cantidad,fecha_detalle",
            date_field="fecha_detalle",
            desde=desde,
        )

    def obtener_pesajes_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        """Recupera pesajes registrados en la ventana solicitada."""

        return self._fetch_since(
            table="pesajes",
            columns="peso_unitario,fecha_pesaje",
            date_field="fecha_pesaje",
            desde=desde,
        )

    def obtener_alertas_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        """Lista las alertas activas desde la fecha de referencia."""

        return self._fetch_since(
            table="alertas",
            columns="id,tipo_color,titulo,estado,fecha_creacion",
            date_field="fecha_creacion",
            desde=desde,
        )

    def obtener_movimientos_desde(self, desde: datetime) -> List[Dict[str, Any]]:
        """Entrega los movimientos de inventario ordenados por timestamp."""

        return self._fetch_since(
            table="movimientos_inventario",
            columns="tipo_evento,rut_usuario,timestamp,observacion",
            date_field="timestamp",
            desde=desde,
        )

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def registrar_evento_auditoria(self, payload: AuditLogPayload) -> bool:
        """Persiste el resultado IA con fallback transparente en caso de error."""

        logger.debug("[IA] Registrando auditoría del módulo %s...", payload.tipo)
        if self._insert("ia_auditoria_logs", payload.primary_record()):
            logger.debug("[IA] Auditoría almacenada en ia_auditoria_logs.")
            return True

        logger.warning(
            "[IA] Fallback a ia_registros para auditoría."
        )
        if self._insert("ia_registros", payload.fallback_record()):
            logger.debug("[IA] Registro guardado en tabla histórica ia_registros.")
            return True

        logger.error("[IA] Falló el registro de auditoría en todas las tablas.")
        return False


repository = IARepository()
