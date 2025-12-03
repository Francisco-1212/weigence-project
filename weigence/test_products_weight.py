"""Script para verificar productos y sus pesos por estante."""
import sys
sys.path.insert(0, '.')

from api.conexion_supabase import supabase

# Consultar productos con su peso y estante asignado
result = supabase.table('productos').select('idproducto, nombre, peso, stock, id_estante').execute()

print("\n=== PRODUCTOS POR ESTANTE ===")

# Agrupar por estante
estantes = {}
for prod in result.data:
    id_est = prod.get('id_estante')
    peso = float(prod.get('peso', 0))
    stock = float(prod.get('stock', 0))
    peso_total = peso * stock
    
    if id_est not in estantes:
        estantes[id_est] = []
    
    estantes[id_est].append({
        'nombre': prod['nombre'],
        'peso_unitario': peso,
        'stock': stock,
        'peso_total': peso_total
    })

for id_est, productos in sorted(estantes.items()):
    peso_total_estante = sum(p['peso_total'] for p in productos)
    print(f"\n📦 Estante {id_est if id_est else 'Sin asignar'}:")
    print(f"   Peso total calculado: {peso_total_estante:.2f}kg")
    for prod in productos:
        if prod['peso_total'] > 0:
            print(f"   - {prod['nombre']}: {prod['peso_unitario']}kg x {prod['stock']} unidades = {prod['peso_total']:.2f}kg")

# Verificar si hay productos que excedan 50kg
print("\n\n=== ESTANTES QUE EXCEDEN 50KG ===")
for id_est, productos in sorted(estantes.items()):
    if id_est:  # Ignorar productos sin estante
        peso_total_estante = sum(p['peso_total'] for p in productos)
        if peso_total_estante > 50:
            print(f"⚠️ Estante {id_est}: {peso_total_estante:.2f}kg (excede en {peso_total_estante - 50:.2f}kg)")
