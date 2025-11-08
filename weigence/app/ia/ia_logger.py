"""Audit logger that persists every IA recommendation."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import Dict, Optional

from .ia_repository import AuditLogPayload, IARepository, repository

logger = logging.getLogger(__name__)


class AuditLogger:
    """Coordinates persistence of IA recommendations for traceability."""

    def __init__(self, repo: IARepository | None = None) -> None:
        self._repo = repo or repository

    def registrar_evento(
        self,
        *,
        tipo: str,
        severidad: str,
        titulo: str,
        mensaje: str,
        solucion: str,
        metadata: Optional[Dict[str, float]] = None,
        confianza: float | None = None,
    ) -> bool:
        """Registra la recomendación final y su metadata de soporte."""

        metadata = metadata or {}
        confianza_val = float(
            confianza
            if confianza is not None
            else metadata.get("signal_strength")
            or metadata.get("trend_percent")
            or metadata.get("weight_volatility")
            or 0.0
        )
        logger.debug("[IA] Preparando payload de auditoría para el módulo %s", tipo)
        payload = AuditLogPayload(
            timestamp=datetime.utcnow(),
            tipo=tipo,
            severidad=severidad,
            titulo=titulo,
            mensaje=mensaje,
            solucion=solucion,
            confianza=confianza_val,
            metadata=metadata,
        )
        return self._repo.registrar_evento_auditoria(payload)


audit_logger = AuditLogger()
