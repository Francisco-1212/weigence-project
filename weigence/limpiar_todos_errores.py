"""
Script para limpiar TODOS los errores del sistema de la base de datos
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.conexion_supabase import supabase

def limpiar_todos_errores():
    """Elimina todos los errores del sistema de la tabla auditoria_eventos"""
    try:
        print("🗑️  Limpiando TODOS los errores del sistema...\n")
        
        # Obtener count antes de eliminar
        count_response = (
            supabase.table("auditoria_eventos")
            .select("id", count="exact")
            .like("accion", "error_sistema%")
            .execute()
        )
        
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        if total == 0:
            print("✅ No hay errores para eliminar")
            return
        
        print(f"📊 Se encontraron {total} errores del sistema")
        
        # Eliminar todos los errores
        response = (
            supabase.table("auditoria_eventos")
            .delete()
            .like("accion", "error_sistema%")
            .execute()
        )
        
        print(f"✅ Se eliminaron {total} errores del sistema")
        print("\n🎯 Base de datos limpia - contador CRIT debería estar en 0")
        print("💡 Ahora solo se registrarán errores nuevos y reales del sistema")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al limpiar: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    limpiar_todos_errores()
