"""
Script para migrar contraseñas existentes en texto plano a hashes bcrypt

IMPORTANTE: 
- Ejecutar una sola vez después de implementar el sistema de hash
- Hace backup de las contraseñas originales antes de migrar
- Requiere confirmación manual antes de proceder

Uso:
    python scripts/migrar_passwords.py
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.conexion_supabase import supabase
from app.utils.security import hash_password
from datetime import datetime
import json


def hacer_backup_passwords():
    """Guarda un backup de las contraseñas actuales"""
    try:
        usuarios = supabase.table("usuarios").select("rut_usuario, Contraseña").execute()
        
        backup_data = {
            'fecha': datetime.now().isoformat(),
            'usuarios': usuarios.data
        }
        
        backup_file = f'backup_passwords_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error al crear backup: {e}")
        return False


def migrar_passwords():
    """Migra todas las contraseñas en texto plano a hashes bcrypt"""
    print("\n" + "="*60)
    print("MIGRACIÓN DE CONTRASEÑAS A HASH BCRYPT")
    print("="*60 + "\n")
    
    # Paso 1: Backup
    print("📦 Paso 1: Creando backup de contraseñas...")
    if not hacer_backup_passwords():
        print("\n❌ No se pudo crear el backup. Abortando migración.")
        return
    
    # Paso 2: Obtener usuarios
    print("\n📋 Paso 2: Obteniendo usuarios...")
    try:
        usuarios = supabase.table("usuarios").select("*").execute()
        total_usuarios = len(usuarios.data)
        print(f"   Encontrados: {total_usuarios} usuarios")
    except Exception as e:
        print(f"❌ Error al obtener usuarios: {e}")
        return
    
    # Paso 3: Confirmación
    print(f"\n⚠️  ATENCIÓN: Se migrarán {total_usuarios} contraseñas")
    confirmacion = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")
    
    if confirmacion != "SI":
        print("\n❌ Migración cancelada por el usuario")
        return
    
    # Paso 4: Migrar
    print("\n🔄 Paso 3: Migrando contraseñas...")
    migrados = 0
    errores = 0
    ya_migrados = 0
    
    for usuario in usuarios.data:
        rut = usuario.get('rut_usuario')
        password_actual = usuario.get('Contraseña', '')
        
        # Verificar si ya está hasheada
        if password_actual and (password_actual.startswith('$2b$') or password_actual.startswith('$2a$')):
            print(f"   ⏭️  {rut}: Ya tiene hash bcrypt, omitiendo...")
            ya_migrados += 1
            continue
        
        if not password_actual:
            print(f"   ⚠️  {rut}: No tiene contraseña, omitiendo...")
            continue
        
        try:
            # Generar hash
            password_hash = hash_password(password_actual)
            
            # Actualizar en base de datos
            supabase.table("usuarios").update({
                'password_hash': password_hash,
                'Contraseña': password_hash  # Actualizar también este campo
            }).eq("rut_usuario", rut).execute()
            
            print(f"   ✅ {rut}: Migrado exitosamente")
            migrados += 1
            
        except Exception as e:
            print(f"   ❌ {rut}: Error - {e}")
            errores += 1
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE MIGRACIÓN")
    print("="*60)
    print(f"Total usuarios: {total_usuarios}")
    print(f"✅ Migrados: {migrados}")
    print(f"⏭️  Ya migrados: {ya_migrados}")
    print(f"❌ Errores: {errores}")
    print("="*60 + "\n")
    
    if errores == 0:
        print("✅ Migración completada exitosamente")
        print("\nAhora puedes:")
        print("1. Verificar que los usuarios pueden iniciar sesión")
        print("2. Si todo funciona, eliminar el backup de contraseñas")
    else:
        print("⚠️  Migración completada con errores")
        print("Revisa los usuarios con error e intenta migrarlos manualmente")


if __name__ == "__main__":
    try:
        migrar_passwords()
    except KeyboardInterrupt:
        print("\n\n❌ Migración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
