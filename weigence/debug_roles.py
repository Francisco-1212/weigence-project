#!/usr/bin/env python3
"""Script para verificar los roles guardados en la base de datos"""

from api.conexion_supabase import supabase

print("=" * 60)
print("VERIFICANDO ROLES EN BASE DE DATOS")
print("=" * 60)

try:
    usuarios = supabase.table('usuarios').select('nombre, rol, rut_usuario').execute().data
    
    if usuarios:
        print(f"\nTotal de usuarios: {len(usuarios)}\n")
        for u in usuarios:
            nombre = u.get('nombre', 'N/A')
            rol = u.get('rol', 'N/A')
            rut = u.get('rut_usuario', 'N/A')
            print(f"Nombre: {nombre}")
            print(f"  RUT: {rut}")
            print(f"  Rol: '{rol}' (tipo: {type(rol).__name__})")
            print(f"  Rol en lowercase: '{str(rol).lower()}'")
            print("-" * 40)
    else:
        print("No hay usuarios en la base de datos")
        
except Exception as e:
    print(f"Error al conectar a la base de datos: {e}")

print("\n" + "=" * 60)
print("ROLES ESPERADOS EN EL SIDEBAR:")
print("=" * 60)
roles_esperados = {
    'farmaceutico': ['dashboard', 'inventario', 'perfil'],
    'bodeguera': ['dashboard', 'inventario', 'movimientos', 'alertas', 'perfil'],
    'supervisor': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'alertas', 'perfil'],
    'jefe': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil'],
    'administrador': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil']
}

for rol, secciones in roles_esperados.items():
    print(f"\n{rol}:")
    for seccion in secciones:
        print(f"  • {seccion}")
