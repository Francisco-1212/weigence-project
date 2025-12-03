"""Script para verificar detección de estantes con sobrepeso."""
import sys
sys.path.insert(0, '.')

from api.conexion_supabase import supabase
result = supabase.table('estantes').select('id_estante, nombre, peso_actual, peso_maximo').execute()

print("\n=== ESTANTES EN BASE DE DATOS ===")
for shelf in result.data:
    peso_actual = float(shelf.get('peso_actual', 0))
    peso_max = float(shelf.get('peso_maximo', 0))
    porcentaje = (peso_actual / peso_max * 100) if peso_max > 0 else 0
    excede = "⚠️ EXCEDE" if peso_actual > peso_max else "✅ OK"
    
    print(f"\n{excede} Estante {shelf['id_estante']}: {shelf.get('nombre', 'Sin nombre')}")
    print(f"   Peso actual: {peso_actual:.1f}kg")
    print(f"   Peso máximo: {peso_max:.1f}kg")
    print(f"   Capacidad: {porcentaje:.1f}%")
    if peso_actual > peso_max:
        print(f"   Sobrepeso: {peso_actual - peso_max:.1f}kg")

# Probar el análisis ML
print("\n\n=== ANÁLISIS ML ===")
from app.ia.ia_ml_insights_advanced import get_advanced_insights

insights = get_advanced_insights()
inventory_analysis = insights.analyze_inventory_capacity()

print(f"\nProductos sin stock: {len(inventory_analysis['without_stock'])}")
print(f"Productos con stock bajo: {len(inventory_analysis['below_min'])}")
print(f"Estantes excedidos: {len(inventory_analysis['shelves_exceeded'])}")

if inventory_analysis['shelves_exceeded']:
    print("\n📦 ESTANTES CON SOBREPESO DETECTADOS:")
    for shelf in inventory_analysis['shelves_exceeded']:
        print(f"   - {shelf['nombre']}: {shelf['actual']:.1f}kg / {shelf['maximo']:.1f}kg ({shelf['exceso_porcentaje']}% exceso)")
else:
    print("\n⚠️ NO SE DETECTARON ESTANTES CON SOBREPESO")
