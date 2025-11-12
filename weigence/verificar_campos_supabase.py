#!/usr/bin/env python
"""Script para verificar los campos reales en Supabase"""

import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.conexion_supabase import supabase
from dotenv import load_dotenv

load_dotenv()

try:
    print("="*60)
    print("Verificando estructura de la tabla 'usuarios'")
    print("="*60)
    
    # Obtener un registro
    response = supabase.table("usuarios").select("*").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        print("\n✅ Se encontró al menos un registro")
        usuario = response.data[0]
        campos = list(usuario.keys())
        
        print(f"\n📋 Campos en la tabla 'usuarios':")
        print(f"{'='*60}")
        for i, campo in enumerate(campos, 1):
            valor = usuario.get(campo)
            valor_str = str(valor)[:50] if valor else "NULL"
            print(f"{i:2}. {campo:20} = {valor_str}")
        
        print(f"\n{'='*60}")
        print("Resumen:")
        print(f"Total de campos: {len(campos)}")
        print(f"Campos: {campos}")
        
    else:
        print("❌ No se encontraron registros en la tabla 'usuarios'")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
