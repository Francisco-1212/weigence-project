"""
Crea datos anómalos PERMANENTES para testing del ML en frontend.
NO se auto-limpian - puedes verlos en http://localhost:5000/auditoria
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from random import uniform, choice

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.conexion_supabase import supabase

def crear_alertas_permanentes():
    """Crea 3 alertas críticas activas"""
    print("\n🚨 Creando 3 alertas críticas permanentes...")
    
    alertas = [
        {
            "tipo_color": "rojo",
            "titulo": "🤖 ML: Stock crítico Medicamento X",
            "descripcion": "Sistema ML detectó patrón anómalo de consumo",
            "estado": "activa",
            "fecha_creacion": datetime.now().isoformat()
        },
        {
            "tipo_color": "rojo",
            "titulo": "⚠️ Sensor desconectado - Zona crítica",
            "descripcion": "Pérdida de señal en sensor principal",
            "estado": "activa",
            "fecha_creacion": datetime.now().isoformat()
        },
        {
            "tipo_color": "rojo",
            "titulo": "📉 Anomalía en peso - Discrepancia 15%",
            "descripcion": "Peso reportado no coincide con inventario",
            "estado": "activa",
            "fecha_creacion": datetime.now().isoformat()
        }
    ]
    
    ids = []
    for alerta in alertas:
        try:
            response = supabase.table("alertas").insert(alerta).execute()
            alerta_id = response.data[0]['id']
            ids.append(alerta_id)
            print(f"   ✅ {alerta['titulo']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return ids


def crear_ventas_bajas_permanentes():
    """Crea 5 ventas con valores anormalmente bajos"""
    print("\n📉 Creando 5 ventas anómalas permanentes (bajas)...")
    
    # Obtener un usuario válido
    try:
        usuarios = supabase.table("usuarios").select("rut_usuario").limit(1).execute()
        if not usuarios.data:
            print("   ⚠️  No hay usuarios - usando fallback")
            rut_usuario = "11111111-1"
        else:
            rut_usuario = usuarios.data[0]['rut_usuario']
    except Exception as e:
        print(f"   ⚠️  Error al buscar usuario: {e}")
        rut_usuario = "11111111-1"
    
    # Ventas entre $500-$1500 (vs promedio normal ~$3000+)
    ids = []
    for i in range(5):
        monto = round(uniform(500, 1500), 2)
        venta = {
            "total": monto,
            "fecha_venta": (datetime.now() - timedelta(hours=uniform(0.5, 6))).isoformat(),
            "rut_usuario": rut_usuario
        }
        
        try:
            response = supabase.table("ventas").insert(venta).execute()
            venta_id = response.data[0]['idventa']
            ids.append(venta_id)
            print(f"   ✅ Venta ${monto:.0f} (ID: {venta_id})")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return ids


def main():
    print("=" * 70)
    print("🧪 CREAR DATOS ANÓMALOS PERMANENTES PARA TESTING ML")
    print("=" * 70)
    print("\n⚠️  IMPORTANTE: Estos datos NO se auto-eliminan")
    print("Úsalos para probar el ML en el frontend y luego limpia manualmente.")
    print("\nCreando datos en 3 segundos...")
    
    import time
    time.sleep(3)
    
    # Crear datos
    alertas_ids = crear_alertas_permanentes()
    ventas_ids = crear_ventas_bajas_permanentes()
    
    print("\n" + "=" * 70)
    print("✅ DATOS ANÓMALOS CREADOS")
    print("=" * 70)
    
    print(f"\n📊 Resumen:")
    print(f"   • {len(alertas_ids)} alertas críticas")
    print(f"   • {len(ventas_ids)} ventas anómalas")
    
    print(f"\n🌐 PRUEBA EN EL FRONTEND:")
    print(f"   1. Abre http://localhost:5000/auditoria")
    print(f"   2. Espera la recomendación IA (5-10 seg)")
    print(f"   3. Deberías ver:")
    print(f"      • 🤖 Badge 'ML' en la card")
    print(f"      • 📊 Panel 'Análisis ML' con score y severidad")
    print(f"      • ⚠️ Severidad: HIGH o CRITICAL")
    print(f"      • 💡 Acciones correctivas específicas")
    
    print(f"\n🗑️  PARA LIMPIAR DESPUÉS:")
    print(f"   python -c \"")
    print(f"from app.app_config import supabase")
    print(f"for id in {alertas_ids}: supabase.table('alertas').delete().eq('id', id).execute()")
    print(f"for id in {ventas_ids}: supabase.table('ventas').delete().eq('idventa', id).execute()")
    print(f"print('✅ Limpieza completada')")
    print(f"   \"")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
