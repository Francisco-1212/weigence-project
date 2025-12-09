"""
Script para consultar alertas específicas y detectar el problema
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.conexion_supabase import supabase
from datetime import datetime

print("\n" + "="*80)
print("🔍 CONSULTA DETALLADA DE ALERTAS RECIENTES")
print("="*80 + "\n")

# Obtener las últimas 20 alertas ordenadas por fecha de creación
alertas = supabase.table("alertas")\
    .select("*")\
    .order("fecha_creacion", desc=True)\
    .limit(20)\
    .execute().data or []

print(f"📊 Mostrando las últimas {len(alertas)} alertas:\n")

for i, alerta in enumerate(alertas, 1):
    id_alerta = alerta.get("id")
    titulo = alerta.get("titulo", "Sin título")
    estado = alerta.get("estado", "Sin estado")
    fecha_creacion = alerta.get("fecha_creacion", "Sin fecha")
    idproducto = alerta.get("idproducto", "-")
    id_estante = alerta.get("id_estante", "-")
    
    # Emojis por estado
    emoji_estado = {
        "pendiente": "🟢",
        "resuelto": "✅",
        "descartada": "🗑️",
        "activo": "🔵"
    }.get(estado, "❓")
    
    print(f"{i}. [{emoji_estado} {estado.upper()}] ID: {id_alerta}")
    print(f"   📝 {titulo}")
    print(f"   📅 Creada: {fecha_creacion}")
    print(f"   🔗 Producto: {idproducto} | Estante: {id_estante}")
    print()

# Buscar específicamente los IDs que aparecen en la captura de pantalla
print("\n" + "="*80)
print("🔎 BUSCANDO IDs ESPECÍFICOS DE LA CAPTURA DE PANTALLA")
print("="*80 + "\n")

ids_captura = [2858, 2857, 2852, 2851, 2853, 2862]

for id_buscar in ids_captura:
    resultado = supabase.table("alertas")\
        .select("*")\
        .eq("id", id_buscar)\
        .execute().data
    
    if resultado:
        alerta = resultado[0]
        print(f"✅ ID {id_buscar} encontrado:")
        print(f"   📝 {alerta.get('titulo')}")
        print(f"   Estado: {alerta.get('estado')}")
        print(f"   Fecha creación: {alerta.get('fecha_creacion')}")
        print()
    else:
        print(f"❌ ID {id_buscar} NO encontrado")
        print()

# Buscar duplicados en las últimas 24 horas
print("\n" + "="*80)
print("🔍 BÚSQUEDA DE DUPLICADOS EN ÚLTIMAS 24 HORAS")
print("="*80 + "\n")

hace_24h = (datetime.now().timestamp() - 86400) * 1000
fecha_hace_24h = datetime.fromtimestamp(hace_24h/1000).isoformat()

alertas_recientes = supabase.table("alertas")\
    .select("*")\
    .gte("fecha_creacion", fecha_hace_24h)\
    .order("fecha_creacion", desc=True)\
    .execute().data or []

print(f"📊 Total de alertas creadas en últimas 24 horas: {len(alertas_recientes)}")

# Agrupar por título
from collections import defaultdict
grupos = defaultdict(list)

for alerta in alertas_recientes:
    titulo = alerta.get("titulo")
    grupos[titulo].append(alerta)

# Mostrar grupos con más de 1 alerta
duplicados_potenciales = {k: v for k, v in grupos.items() if len(v) > 1}

if duplicados_potenciales:
    print(f"\n⚠️  Encontrados {len(duplicados_potenciales)} títulos con múltiples alertas:\n")
    
    for titulo, alertas_grupo in duplicados_potenciales.items():
        print(f"📌 {titulo} ({len(alertas_grupo)} alertas)")
        for alerta in alertas_grupo:
            print(f"   - ID: {alerta['id']} | Estado: {alerta.get('estado')} | Fecha: {alerta.get('fecha_creacion')}")
        print()
else:
    print("\n✅ No se encontraron duplicados en las últimas 24 horas")
