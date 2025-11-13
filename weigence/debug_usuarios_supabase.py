#!/usr/bin/env python3
"""
Script para verificar todos los usuarios en Supabase y sus atributos
"""
from api.conexion_supabase import supabase

print("=" * 80)
print("VERIFICACIÓN DE USUARIOS EN SUPABASE")
print("=" * 80)

try:
    usuarios = supabase.table('usuarios').select('*').execute().data
    
    if usuarios:
        print(f"\n✓ Total de usuarios encontrados: {len(usuarios)}\n")
        
        for idx, usuario in enumerate(usuarios, 1):
            print(f"\n[USUARIO {idx}]")
            print(f"{'─' * 70}")
            for clave, valor in usuario.items():
                print(f"  {clave:20s} → {valor} (tipo: {type(valor).__name__})")
            print(f"{'─' * 70}")
    else:
        print("\n✗ No hay usuarios en la base de datos")
        
except Exception as e:
    print(f"\n✗ Error al conectar a la base de datos: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
