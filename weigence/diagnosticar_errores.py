"""
Script para obtener detalles completos de los errores y diagnosticar el problema
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.conexion_supabase import supabase

def diagnosticar_errores():
    """Obtiene los detalles completos de los errores del sistema"""
    try:
        print("🔍 Obteniendo detalles de errores...\n")
        
        # Obtener todos los errores del sistema
        response = (
            supabase.table("auditoria_eventos")
            .select("id,fecha,usuario,accion,detalle")
            .like("accion", "error_sistema%")
            .order("fecha", desc=True)
            .limit(10)
            .execute()
        )
        
        errores_auditoria = []
        errores_dashboard = []
        otros_errores = []
        
        for error in response.data:
            detalle = error.get('detalle', '')
            if '[auditoria]' in detalle:
                errores_auditoria.append(error)
            elif '[dashboard]' in detalle:
                errores_dashboard.append(error)
            else:
                otros_errores.append(error)
        
        print("=" * 80)
        print("📊 ERRORES DE AUDITORÍA")
        print("=" * 80)
        if errores_auditoria:
            for err in errores_auditoria[:3]:
                print(f"\nID: {err['id']}")
                print(f"Fecha: {err['fecha']}")
                print(f"Detalle completo:\n{err['detalle']}\n")
        else:
            print("✅ No hay errores de auditoría\n")
        
        print("=" * 80)
        print("📊 ERRORES DE DASHBOARD")
        print("=" * 80)
        if errores_dashboard:
            for err in errores_dashboard[:3]:
                print(f"\nID: {err['id']}")
                print(f"Fecha: {err['fecha']}")
                print(f"Detalle completo:\n{err['detalle']}\n")
        else:
            print("✅ No hay errores de dashboard\n")
        
        if otros_errores:
            print("=" * 80)
            print("📊 OTROS ERRORES")
            print("=" * 80)
            for err in otros_errores:
                print(f"\nID: {err['id']}")
                print(f"Fecha: {err['fecha']}")
                print(f"Detalle: {err['detalle'][:200]}...\n")
        
        return response.data
        
    except Exception as e:
        print(f"❌ Error al diagnosticar: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    diagnosticar_errores()
