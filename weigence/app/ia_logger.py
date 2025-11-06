"""Utilities to persist IA snapshots."""
from __future__ import annotations

from app.ia import ia_service

def registrar_ia(modulo="auditoria"):
    """
    Genera un registro IA con las métricas actuales y lo guarda en ia_registros.
    Se ejecuta cada vez que se analiza o abre el panel Auditoría.
    """
    try:
        registrado = ia_service.registrar_snapshot(modulo)
        if not registrado:
            raise RuntimeError("No fue posible insertar el registro IA")
        return True
    except Exception as e:
        print("[registrar_ia]", e)
        return False
