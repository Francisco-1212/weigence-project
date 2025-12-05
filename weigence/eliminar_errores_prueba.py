"""
Script para eliminar los errores de prueba de la tabla auditoria_eventos
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from api.conexion_supabase import supabase

def eliminar_errores_prueba():
    """Elimina todos los errores de prueba de la tabla auditoria_eventos"""
    try:
        print("🗑️  Eliminando errores de prueba...")
        
        # Eliminar eventos con detalle que contenga "[prueba]"
        response = (
            supabase.table("auditoria_eventos")
            .delete()
            .like("detalle", "%[prueba]%")
            .execute()
        )
        
        count = len(response.data) if response.data else 0
        
        print(f"✅ Se eliminaron {count} errores de prueba")
        
        # Mostrar resumen
        print("\n📊 Verificando errores restantes...")
        remaining = (
            supabase.table("auditoria_eventos")
            .select("id,fecha,accion,detalle")
            .like("accion", "error_sistema%")
            .order("fecha", desc=True)
            .limit(5)
            .execute()
        )
        
        if remaining.data:
            print(f"\n⚠️  Quedan {len(remaining.data)} errores del sistema (no de prueba):")
            for error in remaining.data:
                detalle = error.get('detalle', '')[:60]
                print(f"   - {error.get('fecha')}: {detalle}...")
        else:
            print("\n✅ No quedan errores del sistema en la base de datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al eliminar errores de prueba: {e}")
        return False

if __name__ == "__main__":
    eliminar_errores_prueba()
