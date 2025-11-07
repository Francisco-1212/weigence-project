"""Audit logger that persists every IA recommendation."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from .ia_repository import AuditLogPayload, IARepository, repository


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
    ) -> bool:
        payload = AuditLogPayload(
            timestamp=datetime.utcnow(),
            tipo=tipo,
            severidad=severidad,
            titulo=titulo,
            mensaje=mensaje,
            solucion=solucion,
            metadata=metadata or {},
        )
        return self._repo.registrar_evento_auditoria(payload)


audit_logger = AuditLogger()
