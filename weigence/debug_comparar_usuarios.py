#!/usr/bin/env python3
"""
Script para comparar lo que dice el usuario que inició sesión
vs lo que hay en Supabase
"""
from flask import session
from api.conexion_supabase import supabase

print("=" * 80)
print("VERIFICACIÓN DE COINCIDENCIA: SESIÓN vs SUPABASE")
print("=" * 80)

# Datos de la sesión actual (si existe)
print("\n📍 DATOS DE LA SESIÓN ACTUAL:")
print(f"  usuario_nombre: {session.get('usuario_nombre', 'NO DEFINIDO')}")
print(f"  usuario_rol: {session.get('usuario_rol', 'NO DEFINIDO')}")
print(f"  usuario_id: {session.get('usuario_id', 'NO DEFINIDO')}")

# Buscar todos los usuarios en Supabase
try:
    print("\n🔍 BUSCANDO EN SUPABASE...")
    usuarios = supabase.table('usuarios').select('nombre, rol, rut_usuario, correo').execute().data
    
    if usuarios:
        print(f"\n✓ Usuarios en Supabase ({len(usuarios)} total):\n")
        for idx, u in enumerate(usuarios, 1):
            print(f"  [{idx}] Nombre: '{u.get('nombre')}' | Rol: '{u.get('rol')}' | RUT: '{u.get('rut_usuario')}'")
    else:
        print("\n✗ No hay usuarios en Supabase")

except Exception as e:
    print(f"\n✗ Error al consultar Supabase: {e}")

print("\n" + "=" * 80)
print("INSTRUCCIONES:")
print("1. Inicia sesión con el usuario 'farmacéutico'")
print("2. Abre: http://localhost:5000/debug-usuario")
print("3. Compara qué usuario_nombre ves con los usuarios en Supabase")
print("4. Si no coincide, el problema está en la BD")
print("=" * 80)
