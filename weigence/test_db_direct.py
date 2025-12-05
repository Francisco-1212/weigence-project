"""
Test directo: verifica si collect_auditoria_eventos() retorna error_sistema
Simula lo que hace la ruta /api/auditoria/logs
"""

import sys
import os

# Añadir el directorio app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from datetime import datetime, timedelta, timezone
from api.conexion_supabase import supabase

print("🔍 Consultando base de datos directamente...")

# Últimas 24 horas
desde = datetime.now(timezone.utc) - timedelta(hours=24)
desde_iso = desde.isoformat()

print(f"📅 Buscando eventos desde: {desde_iso}")

# Query exacta que usa collect_auditoria_eventos()
response = (
    supabase.table("auditoria_eventos")
    .select("id,fecha,usuario,accion,detalle")
    .gte("fecha", desde_iso)
    .order("fecha", desc=True)
    .limit(100)
    .execute()
)

print(f"\n✅ Total de eventos en DB: {len(response.data)}")

# Filtrar error_sistema
errores_sistema = [
    row for row in response.data 
    if row.get("accion", "").lower().startswith("error_sistema")
]

print(f"🔍 Eventos con acción error_sistema*: {len(errores_sistema)}")

if errores_sistema:
    print("\n📋 Detalles de errores del sistema:")
    for i, error in enumerate(errores_sistema[:5], 1):
        print(f"\n{i}. ID: {error.get('id')}")
        print(f"   Fecha: {error.get('fecha')}")
        print(f"   Usuario: {error.get('usuario')}")
        print(f"   Acción: {error.get('accion')}")
        print(f"   Detalle: {error.get('detalle')[:100]}...")
else:
    print("\n⚠️ No se encontraron eventos error_sistema en las últimas 24h")
    
    # Mostrar acciones presentes
    acciones_presentes = {}
    for row in response.data:
        accion = row.get("accion", "sin_accion")
        acciones_presentes[accion] = acciones_presentes.get(accion, 0) + 1
    
    print("\n📊 Acciones presentes en DB:")
    for accion, count in sorted(acciones_presentes.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   - {accion}: {count}")
