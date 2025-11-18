#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para problema de acceso a auditoría
"""

import sys
from api.conexion_supabase import supabase

print("="*60)
print("DIAGNÓSTICO: Acceso a Auditoría")
print("="*60)

# 1. Verificar roles en la base de datos
print("\n1. ROLES EN LA BASE DE DATOS:")
print("-" * 60)
try:
    response = supabase.table("usuarios").select("rut_usuario, nombre, rol").execute()
    
    roles_encontrados = {}
    for usuario in response.data:
        rol = usuario.get("rol", "SIN ROL")
        if rol not in roles_encontrados:
            roles_encontrados[rol] = []
        roles_encontrados[rol].append({
            "rut": usuario.get("rut_usuario"),
            "nombre": usuario.get("nombre")
        })
    
    for rol, usuarios in sorted(roles_encontrados.items()):
        print(f"\n   Rol: '{rol}' (lowercase: '{rol.lower() if rol else 'None'}')")
        for u in usuarios[:3]:  # Mostrar máximo 3 por rol
            print(f"      - {u['nombre']} ({u['rut']})")
        if len(usuarios) > 3:
            print(f"      ... y {len(usuarios) - 3} más")
            
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar requisitos de auditoría
print("\n2. REQUISITOS PARA AUDITORÍA:")
print("-" * 60)
print("   Roles permitidos: ['supervisor', 'jefe', 'administrador']")
print("   Archivo: app/routes/auditoria.py")
print("   Decorador: @requiere_rol('supervisor', 'jefe', 'administrador')")

# 3. Verificar comparación
print("\n3. VERIFICACIÓN DE COMPARACIÓN:")
print("-" * 60)
roles_permitidos = ['supervisor', 'jefe', 'administrador']

for rol_original, usuarios in sorted(roles_encontrados.items()):
    rol_normalizado = str(rol_original).lower() if rol_original else ""
    tiene_acceso = rol_normalizado in roles_permitidos
    
    print(f"\n   Rol DB: '{rol_original}'")
    print(f"   Normalizado: '{rol_normalizado}'")
    print(f"   ¿Tiene acceso? {'✅ SÍ' if tiene_acceso else '❌ NO'}")

# 4. Sugerencia
print("\n4. SOLUCIÓN:")
print("=" * 60)
print("""
Si tu usuario NO tiene uno de estos roles exactos:
- 'supervisor'
- 'jefe'  
- 'administrador'

Necesitas actualizar tu rol en Supabase:

UPDATE usuarios 
SET rol = 'administrador'  -- o 'supervisor' o 'jefe'
WHERE rut_usuario = 'TU_RUT';

IMPORTANTE: El rol debe estar en MINÚSCULAS.
""")

print("="*60)
