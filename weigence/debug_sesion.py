"""
Script para depurar la sesión de Flask
Úsalo así:
1. Inicia sesión en la web
2. Ejecuta: python debug_sesion.py
"""

from app import create_app
from flask import session

app = create_app()

# Crear contexto de aplicación
with app.test_request_context():
    print("=" * 80)
    print("DEPURACIÓN DE SESIÓN")
    print("=" * 80)
    print("\nNota: Este script no verá la sesión de un usuario logueado.")
    print("Solo sirve para verificar que Flask está configurado correctamente.")
    print("\nPara ver la sesión real, abre las DevTools del navegador:")
    print("  1. Inicia sesión en la web")
    print("  2. Abre DevTools (F12)")
    print("  3. Ve a Application > Cookies")
    print("  4. Busca 'session'")
    print("=" * 80)

# En su lugar, vamos a verificar que el decorador funciona
print("\nVerificando que los decoradores están importados correctamente...")

try:
    from app.routes.decorators import requiere_rol, requiere_autenticacion
    print("✅ Decoradores importados correctamente")
except Exception as e:
    print(f"❌ Error importando decoradores: {e}")

# Verificar que la ruta de usuarios existe
print("\nVerificando que la ruta de usuarios está registrada...")

try:
    from app.routes import usuarios
    print("✅ Módulo usuarios importado correctamente")
except Exception as e:
    print(f"❌ Error importando usuarios: {e}")

# Ver todas las rutas
print("\nRutas registradas en la aplicación:")
print("-" * 80)

for rule in app.url_map.iter_rules():
    if 'usuario' in str(rule).lower():
        print(f"  {rule}")

print("\nRutas de dashboard y login:")
print("-" * 80)

for rule in app.url_map.iter_rules():
    if 'dashboard' in str(rule).lower() or 'login' in str(rule).lower():
        print(f"  {rule}")

print("\n" + "=" * 80)
print("VERIFICACIÓN COMPLETADA")
print("=" * 80)
