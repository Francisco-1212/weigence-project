"""Script para verificar y testear estantes con sobrepeso."""

import sys
sys.path.append('.')

from api.conexion_supabase import supabase

print("🔍 Verificando estantes con peso...")

# Consultar todos los estantes
response = supabase.table('estantes').select('*').execute()

if response.data:
    print(f"\n📊 Total de estantes: {len(response.data)}")
    print("\nEstantes actuales:")
    print("-" * 80)
    
    for estante in response.data:
        id_estante = estante.get('id_estante')
        nombre = estante.get('nombre', f'Estante {id_estante}')
        peso_actual = float(estante.get('peso_actual', 0))
        peso_maximo = float(estante.get('peso_maximo', 0))
        
        porcentaje = (peso_actual / peso_maximo * 100) if peso_maximo > 0 else 0
        estado = "🚨 SOBRECARGADO" if peso_actual > peso_maximo else "✅ Normal"
        
        print(f"{estado} | {nombre} | Actual: {peso_actual}kg | Máximo: {peso_maximo}kg | Capacidad: {porcentaje:.1f}%")
    
    # Verificar si hay estantes sobrecargados
    sobrecargados = [e for e in response.data if float(e.get('peso_actual', 0)) > float(e.get('peso_maximo', 0))]
    
    if sobrecargados:
        print(f"\n⚠️  Se detectaron {len(sobrecargados)} estantes con sobrepeso")
    else:
        print("\n✅ No hay estantes con sobrepeso actualmente")
        print("\n💡 Para testear, puedes actualizar un estante con:")
        print("   UPDATE estantes SET peso_actual = peso_maximo + 10 WHERE id_estante = 1;")
        
        # Opción: crear un estante de prueba con sobrepeso
        print("\n❓ ¿Quieres crear un estante de prueba con sobrepeso? (si/no)")
        respuesta = input().strip().lower()
        
        if respuesta == 'si':
            # Actualizar el primer estante para que tenga sobrepeso
            if response.data:
                primer_estante = response.data[0]
                id_estante = primer_estante['id_estante']
                peso_max = float(primer_estante.get('peso_maximo', 100))
                nuevo_peso = peso_max + 15  # Sobrepeso de 15kg
                
                update_response = supabase.table('estantes') \
                    .update({'peso_actual': nuevo_peso}) \
                    .eq('id_estante', id_estante) \
                    .execute()
                
                if update_response.data:
                    print(f"✅ Estante {id_estante} actualizado con sobrepeso: {nuevo_peso}kg (máx: {peso_max}kg)")
                else:
                    print(f"❌ Error al actualizar estante")

else:
    print("❌ No se encontraron estantes en la base de datos")
