"""
Script para verificar que los errores están en la base de datos
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.conexion_supabase import supabase

def verificar_errores():
    """Verifica que los errores están en auditoria_eventos"""
    try:
        print("🔍 Buscando errores en auditoria_eventos...")
        
        # Buscar errores con acción que contenga 'error_sistema'
        resultado = supabase.table("auditoria_eventos").select(
            "id, fecha, usuario, accion, detalle"
        ).like("accion", "error_sistema%").order("fecha", desc=True).limit(10).execute()
        
        if resultado.data:
            print(f"\n✅ Se encontraron {len(resultado.data)} errores:\n")
            for i, error in enumerate(resultado.data, 1):
                print(f"{i}. ID: {error.get('id')}")
                print(f"   Fecha: {error.get('fecha')}")
                print(f"   Usuario: {error.get('usuario')}")
                print(f"   Acción: {error.get('accion')}")
                print(f"   Detalle: {error.get('detalle')[:100]}...")
                print()
        else:
            print("❌ No se encontraron errores con acción 'error_sistema%'")
            
        # Verificar todos los eventos recientes
        print("\n📋 Últimos 5 eventos en auditoria_eventos:")
        todos = supabase.table("auditoria_eventos").select(
            "fecha, accion"
        ).order("fecha", desc=True).limit(5).execute()
        
        for evento in todos.data:
            print(f"  - {evento.get('fecha')}: {evento.get('accion')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verificar_errores()
