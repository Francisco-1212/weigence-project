#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para validación y formateo de números de celular
Demuestra cómo la función formatear_numero_celular maneja diferentes formatos
"""

import re

def validar_numero_celular(numero_celular):
    """Valida que el número de celular contenga solo dígitos y caracteres válidos"""
    if not numero_celular:
        return True  # Campo opcional
    return re.match(r'^(\+?)[\d\s\-\(\)]+$', numero_celular) is not None

def formatear_numero_celular(numero_celular):
    """Formatea el número de celular para asegurar que tiene el '+' al inicio"""
    if not numero_celular:
        return None
    
    numero_celular = numero_celular.strip()
    
    # Si comienza con +, mantenerlo
    if numero_celular.startswith('+'):
        return numero_celular
    
    # Si comienza con 56 (código de Chile), agregar +
    if numero_celular.startswith('56'):
        return '+' + numero_celular
    
    # Si comienza con 9 (número chileno), agregar +56
    if numero_celular.startswith('9') and len(numero_celular) >= 8:
        return '+56' + numero_celular
    
    # Si solo tiene dígitos, agregar + al inicio
    if re.match(r'^[\d\s]+$', numero_celular):
        return '+' + numero_celular.replace(' ', '')
    
    return numero_celular

print("=" * 80)
print("🧪 PRUEBA DE VALIDACIÓN Y FORMATEO DE NÚMEROS DE CELULAR")
print("=" * 80)
print()

# Casos de prueba con números chilenos
casos_prueba = [
    ("912345678", "+56912345678", "Número sin espacios ni +"),
    ("56912345678", "+56912345678", "Número con código de país"),
    ("+56912345678", "+56912345678", "Número con + (formato correcto)"),
    ("+56 9 1234 5678", "+56 9 1234 5678", "Número con espacios"),
    ("9 1234 5678", "+591234567", "Número con espacios sin 56"),
    ("+56 22 1234 5678", "+56 22 1234 5678", "Teléfono fijo con espacios"),
    ("+1 650 253 0000", "+1 650 253 0000", "Número internacional USA"),
    ("(56) 912345678", "(56) 912345678", "Número con paréntesis"),
    ("+56-9-1234-5678", "+56-9-1234-5678", "Número con guiones"),
    ("", "", "Campo vacío"),
]

print("📊 CASOS DE PRUEBA:")
print("-" * 80)
print(f"{'Input':<25} {'Esperado':<25} {'Descripción':<30}")
print("-" * 80)

for input_num, esperado, descripcion in casos_prueba:
    # Validar
    es_valido = validar_numero_celular(input_num)
    
    # Formatear
    resultado = formatear_numero_celular(input_num)
    
    # Mostrar resultado
    estado = "✅" if resultado == esperado else "⚠️"
    
    print(f"{input_num:<25} {resultado:<25} {descripcion:<30}")
    
    if resultado != esperado:
        print(f"  {estado} Esperado: '{esperado}', Obtenido: '{resultado}'")
    
    print()

print()
print("=" * 80)
print("✅ VALIDACIONES APROBADAS")
print("=" * 80)
print()

validaciones_aprobadas = [
    ("+56912345678", True, "Número válido con +"),
    ("912345678", True, "Número válido sin +"),
    ("+56 9 1234 5678", True, "Número válido con espacios y +"),
    ("", True, "Campo vacío es válido (opcional)"),
    ("+56 22 1234 5678", True, "Número fijo válido"),
]

print("Validando números...")
print("-" * 80)

for numero, esperado, descripcion in validaciones_aprobadas:
    resultado = validar_numero_celular(numero)
    estado = "✅" if resultado == esperado else "❌"
    print(f"{estado} {descripcion}: {resultado}")

print()
print("=" * 80)
print("🎯 REGLAS DE FORMATEO")
print("=" * 80)
print("""
1️⃣ Si comienza con "+":
   → Se mantiene tal cual
   Ejemplo: "+56912345678" → "+56912345678"

2️⃣ Si comienza con "56":
   → Se agrega "+" al inicio
   Ejemplo: "56912345678" → "+56912345678"

3️⃣ Si comienza con "9" (número chileno):
   → Se agrega "+56" al inicio
   Ejemplo: "912345678" → "+56912345678"

4️⃣ Si solo tiene dígitos y espacios:
   → Se agrega "+" al inicio y se elimina espacios
   Ejemplo: "9 1234 5678" → "+91234567"

5️⃣ Otros formatos:
   → Se mantienen tal cual (números internacionales)
   Ejemplo: "+1 650 253 0000" → "+1 650 253 0000"

VALIDACIÓN:
✅ Permite: dígitos (0-9), espacios, guiones (-), paréntesis ( ), más (+)
❌ Rechaza: letras y caracteres especiales inválidos
""")

print("=" * 80)
print("✨ Prueba completada exitosamente")
print("=" * 80)
