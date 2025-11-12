#!/usr/bin/env python3
"""
Script de prueba para verificar configuración de email
Ejecutar: python test_email.py
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("=" * 60)
print("🔍 VERIFICACIÓN DE CONFIGURACIÓN DE EMAIL")
print("=" * 60)

# 1. Verificar que .env se cargó
print("\n1️⃣  Verificando archivo .env...")
if os.path.exists(".env"):
    print("   ✅ Archivo .env encontrado")
else:
    print("   ❌ Archivo .env NO encontrado en la raíz del proyecto")
    sys.exit(1)

# 2. Verificar variables
print("\n2️⃣  Verificando variables de entorno...")

variables_requeridas = {
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": "587",
    "MAIL_USERNAME": "tu_email@gmail.com",
    "MAIL_PASSWORD": "contraseña",
    "MAIL_FROM": "tu_email@gmail.com",
    "BASE_URL": "http://localhost:5000",
}

todas_configuradas = True
for var, desc in variables_requeridas.items():
    valor = os.getenv(var)
    if valor:
        # Ocultar contraseña para seguridad
        if var == "MAIL_PASSWORD":
            print(f"   ✅ {var:20} = {'*' * 10}")
        else:
            print(f"   ✅ {var:20} = {valor}")
    else:
        print(f"   ❌ {var:20} = NO CONFIGURADA")
        todas_configuradas = False

if not todas_configuradas:
    print("\n⚠️  Algunas variables no están configuradas.")
    print("   Revisa el archivo .env y completa los valores.")
    sys.exit(1)

# 3. Verificar tabla en Supabase
print("\n3️⃣  Verificando tabla en Supabase...")
try:
    from api.conexion_supabase import supabase
    
    # Intentar consultar la tabla
    resultado = supabase.table("password_reset_tokens").select("count").execute()
    print("   ✅ Tabla 'password_reset_tokens' existe en Supabase")
except Exception as e:
    print(f"   ⚠️  No se pudo verificar tabla: {e}")
    print("   💡 Ejecuta el SQL de: migrations/password_reset_tokens.sql")

# 4. Probar conexión SMTP
print("\n4️⃣  Probando conexión SMTP...")
try:
    import smtplib
    
    server = smtplib.SMTP(os.getenv("MAIL_SERVER"), int(os.getenv("MAIL_PORT")))
    server.starttls()
    print("   ✅ Conexión SMTP establecida")
    
    # Intentar autenticación
    try:
        server.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        print("   ✅ Autenticación SMTP exitosa")
        server.quit()
    except smtplib.SMTPAuthenticationError:
        print("   ❌ Error de autenticación SMTP")
        print("   💡 Verifica que MAIL_PASSWORD sea correcto")
        print("   💡 Para Gmail, usa contraseña de aplicación (no tu contraseña normal)")
        server.quit()
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Error de conexión SMTP: {e}")
    sys.exit(1)

# 5. Probar importación de módulo de email
print("\n5️⃣  Verificando módulo de email...")
try:
    from app.email_utils import enviar_correo_recuperacion
    print("   ✅ Módulo email_utils importado correctamente")
except ImportError as e:
    print(f"   ❌ Error importando email_utils: {e}")
    sys.exit(1)

# 6. Prueba de envío (opcional)
print("\n6️⃣  ¿Deseas hacer una prueba de envío? (s/n)")
respuesta = input("   > ").lower().strip()

if respuesta == 's':
    email_prueba = input("   Ingresa email de prueba: ").strip()
    print(f"\n   📧 Enviando correo de prueba a: {email_prueba}...")
    
    try:
        resultado = enviar_correo_recuperacion(email_prueba, "Usuario Prueba")
        if resultado:
            print("   ✅ Correo enviado exitosamente")
            print("   💡 Revisa tu bandeja en 2-3 segundos")
        else:
            print("   ❌ Error al enviar correo (revisa los logs)")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

# Resumen final
print("\n" + "=" * 60)
print("✅ TODO ESTÁ CONFIGURADO CORRECTAMENTE")
print("=" * 60)
print("\n🚀 Ahora puedes:")
print("   1. Ejecutar: python app.py")
print("   2. Ir a: http://localhost:5000")
print("   3. Hacer clic en '¿Olvidaste tu contraseña?'")
print("   4. Recibir correo de recuperación")
print("\n")
