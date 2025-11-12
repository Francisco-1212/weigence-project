"""
Script de prueba para las funciones de validación de perfil
Ejecutar: python test_perfil_validation.py
"""

import re

def validar_email(email):
    """Valida que el email tenga un formato correcto"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    """Valida que el teléfono contenga solo dígitos y espacios"""
    if not telefono:
        return True  # Campo opcional
    return re.match(r'^[\d\s\-\+\(\)]+$', telefono) is not None

# ========== PRUEBAS DE EMAIL ==========
print("=" * 50)
print("🧪 PRUEBAS DE VALIDACIÓN DE EMAIL")
print("=" * 50)

emails_validos = [
    "usuario@ejemplo.com",
    "juan.perez@dominio.co.uk",
    "test123@prueba.org",
    "user+tag@ejemplo.com",
    "nombre_usuario@dominio.com",
]

emails_invalidos = [
    "usuarioejemplo.com",          # Falta @
    "usuario@",                     # Falta dominio
    "@ejemplo.com",                 # Falta usuario
    "usuario @ejemplo.com",         # Espacio
    "usuario@dominio",              # Falta TLD
    "usuario@.com",                 # Falta dominio
]

print("\n✅ EMAILS VÁLIDOS:")
for email in emails_validos:
    resultado = validar_email(email)
    icono = "✅" if resultado else "❌"
    print(f"  {icono} {email}: {resultado}")

print("\n❌ EMAILS INVÁLIDOS:")
for email in emails_invalidos:
    resultado = validar_email(email)
    icono = "❌" if not resultado else "✅"
    print(f"  {icono} {email}: {resultado}")

# ========== PRUEBAS DE TELÉFONO ==========
print("\n" + "=" * 50)
print("🧪 PRUEBAS DE VALIDACIÓN DE TELÉFONO")
print("=" * 50)

telefonos_validos = [
    "+56 9 1234 5678",
    "912345678",
    "+56-9-1234-5678",
    "(+56) 9 1234-5678",
    "9 1234 5678",
]

telefonos_invalidos = [
    "+56 9 1234 ABC5",      # Contiene letras
    "912345678@",           # Contiene @
    "912345678#",           # Contiene #
    "912345678!",           # Contiene !
]

print("\n✅ TELÉFONOS VÁLIDOS:")
for telefono in telefonos_validos:
    resultado = validar_telefono(telefono)
    icono = "✅" if resultado else "❌"
    print(f"  {icono} {telefono}: {resultado}")

print("\n❌ TELÉFONOS INVÁLIDOS:")
for telefono in telefonos_invalidos:
    resultado = validar_telefono(telefono)
    icono = "❌" if not resultado else "✅"
    print(f"  {icono} {telefono}: {resultado}")

# ========== PRUEBAS DE CAMPOS VACÍOS ==========
print("\n" + "=" * 50)
print("🧪 PRUEBAS DE CAMPOS VACÍOS")
print("=" * 50)

print("\n📧 Email vacío (opcional):")
print(f"  ✅ validar_email(''): {validar_email('')}")

print("\n📱 Teléfono vacío (opcional):")
print(f"  ✅ validar_telefono(''): {validar_telefono('')}")

# ========== RESUMEN ==========
print("\n" + "=" * 50)
print("📊 RESUMEN DE PRUEBAS")
print("=" * 50)

total_emails_validos = sum(1 for e in emails_validos if validar_email(e))
total_emails_invalidos = sum(1 for e in emails_invalidos if not validar_email(e))
total_telefonos_validos = sum(1 for t in telefonos_validos if validar_telefono(t))
total_telefonos_invalidos = sum(1 for t in telefonos_invalidos if not validar_telefono(t))

print(f"\nEmails válidos: {total_emails_validos}/{len(emails_validos)}")
print(f"Emails inválidos (detectados): {total_emails_invalidos}/{len(emails_invalidos)}")
print(f"Teléfonos válidos: {total_telefonos_validos}/{len(telefonos_validos)}")
print(f"Teléfonos inválidos (detectados): {total_telefonos_invalidos}/{len(telefonos_invalidos)}")

# Verificar si todas las pruebas pasaron
todas_pasaron = (
    total_emails_validos == len(emails_validos) and
    total_emails_invalidos == len(emails_invalidos) and
    total_telefonos_validos == len(telefonos_validos) and
    total_telefonos_invalidos == len(telefonos_invalidos)
)

print("\n" + "=" * 50)
if todas_pasaron:
    print("✅ ¡TODAS LAS PRUEBAS PASARON!")
else:
    print("❌ Algunas pruebas fallaron. Revisar arriba.")
print("=" * 50)
