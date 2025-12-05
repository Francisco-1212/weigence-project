"""
Script de prueba rápida para generar un error en auditoría
Ejecuta este script para ver un error registrado en la consola de auditoría
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timezone
from api.conexion_supabase import supabase

def generar_error_prueba():
    """Genera un error de prueba directamente en la tabla auditoria_eventos"""
    try:
        print("🧪 Generando error de prueba en auditoría...")
        
        # Registrar error directamente en la tabla
        payload = {
            "fecha": datetime.now(timezone.utc).isoformat(),
            "usuario": "admin@weigence.cl",  # Cambia esto por tu usuario
            "accion": "error_sistema_critical",
            "detalle": "[prueba] Error de prueba crítico. Este es un error generado manualmente para verificar el sistema de auditoría."
        }
        
        resultado = supabase.table("auditoria_eventos").insert(payload).execute()
        
        print("✅ Error registrado exitosamente en auditoría!")
        print(f"📋 Detalles:")
        print(f"   - Usuario: {payload['usuario']}")
        print(f"   - Acción: {payload['accion']}")
        print(f"   - Detalle: {payload['detalle']}")
        print(f"   - Fecha: {payload['fecha']}")
        print("\n🔍 Para verificar:")
        print("   1. Ve a http://localhost:5000/auditoria")
        print("   2. Busca el evento más reciente con acción 'error_sistema_critical'")
        print("   3. O haz clic en 'Ver historial' en el footer → pestaña 'Errores'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al registrar en auditoría: {e}")
        return False

if __name__ == "__main__":
    generar_error_prueba()
