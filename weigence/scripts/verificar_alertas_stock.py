"""
Script para verificar alertas de productos específicos
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.conexion_supabase import supabase

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE ALERTAS DE STOCK")
print("="*80 + "\n")

# Productos sin stock
productos_sin_stock = ["Paracetamol", "Ibuprofeno", "Alcohol Gel"]

for producto in productos_sin_stock:
    # Buscar producto en BD
    prod = supabase.table("productos")\
        .select("*")\
        .ilike("nombre", f"%{producto}%")\
        .execute().data
    
    if prod:
        p = prod[0]
        print(f"📦 {p.get('nombre')}")
        print(f"   ID: {p.get('idproducto')}")
        print(f"   Stock: {p.get('stock')}")
        print(f"   Activo: {p.get('activo')}")
        
        # Buscar alertas de este producto
        alertas = supabase.table("alertas")\
            .select("*")\
            .eq("idproducto", p.get('idproducto'))\
            .order("fecha_creacion", desc=True)\
            .limit(5)\
            .execute().data or []
        
        if alertas:
            print(f"   Alertas encontradas: {len(alertas)}")
            for a in alertas:
                print(f"      - [{a.get('estado')}] {a.get('titulo')} (ID: {a['id']}) - {a.get('fecha_creacion')}")
        else:
            print(f"   ⚠️  NO HAY ALERTAS para este producto")
        print()

# Verificar alertas pendientes de stock
print("\n" + "="*80)
print("📊 TODAS LAS ALERTAS DE STOCK PENDIENTES")
print("="*80 + "\n")

alertas_stock = supabase.table("alertas")\
    .select("*")\
    .eq("estado", "pendiente")\
    .ilike("titulo", "%stock%")\
    .execute().data or []

print(f"Total de alertas de stock pendientes: {len(alertas_stock)}\n")

for a in alertas_stock:
    print(f"- [{a.get('estado')}] {a.get('titulo')} (ID: {a['id']})")
    print(f"  Producto ID: {a.get('idproducto')}")
    print(f"  Fecha: {a.get('fecha_creacion')}")
    print()

# Verificar si los productos tienen activo=True
print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE PRODUCTOS ACTIVOS")
print("="*80 + "\n")

for producto in productos_sin_stock:
    prod = supabase.table("productos")\
        .select("idproducto, nombre, stock, activo")\
        .ilike("nombre", f"%{producto}%")\
        .execute().data
    
    if prod:
        p = prod[0]
        activo = p.get('activo', 'NULL')
        emoji = "✅" if activo else "❌"
        print(f"{emoji} {p.get('nombre')}: stock={p.get('stock')}, activo={activo}")
