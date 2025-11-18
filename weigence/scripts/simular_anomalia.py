"""
Script para simular datos anómalos y probar la detección ML.
Crea alertas críticas y datos de ventas/inventario anómalos TEMPORALES.

Ejecutar: python scripts/simular_anomalia.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone, timedelta
from api.conexion_supabase import supabase
from app.ia.ia_snapshots import snapshot_builder
from app.ia.ia_ml_anomalies import get_detector
import random


def crear_alertas_criticas():
    """Crea 3-4 alertas críticas para simular presión operativa."""
    print("\n🚨 Creando alertas críticas...")
    
    alertas = [
        {
            "tipo_color": "rojo",
            "titulo": "Stock crítico detectado por ML",
            "descripcion": "Producto X bajo nivel mínimo - reposición urgente",
            "estado": "activa",
            "fecha_creacion": datetime.now(timezone.utc).isoformat(),
        },
        {
            "tipo_color": "rojo",
            "titulo": "Sensor desconectado - Estante A3",
            "descripcion": "Fallo de comunicación con sensor de peso",
            "estado": "activa",
            "fecha_creacion": datetime.now(timezone.utc).isoformat(),
        },
        {
            "tipo_color": "rojo",
            "titulo": "Anomalía en peso detectada",
            "descripcion": "Variación mayor a 20% en últimas 2 horas",
            "estado": "activa",
            "fecha_creacion": datetime.now(timezone.utc).isoformat(),
        },
        {
            "tipo_color": "amarillo",
            "titulo": "Baja actividad en turno nocturno",
            "descripcion": "Movimientos por debajo del 40% esperado",
            "estado": "activa",
            "fecha_creacion": datetime.now(timezone.utc).isoformat(),
        },
    ]
    
    ids_creados = []
    for alerta in alertas:
        try:
            response = supabase.table("alertas").insert(alerta).execute()
            if response.data:
                ids_creados.append(response.data[0]['id'])
                print(f"   ✅ {alerta['titulo']}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    return ids_creados


def crear_ventas_bajas():
    """Crea ventas con valores anormalmente bajos."""
    print("\n📉 Creando ventas anómalas (bajas)...")
    
    # Obtener un usuario válido
    try:
        usuarios = supabase.table("usuarios").select("rut_usuario").limit(1).execute()
        if not usuarios.data:
            print("   ⚠️  No hay usuarios en la BD")
            return []
        rut_usuario = usuarios.data[0]['rut_usuario']
    except:
        rut_usuario = "11111111-1"  # Fallback
    
    ventas = []
    ahora = datetime.now(timezone.utc)
    
    # Crear 5 ventas muy bajas (simulando caída)
    for i in range(5):
        venta = {
            "total": random.uniform(500, 1500),  # Muy bajo comparado con normal
            "fecha_venta": (ahora - timedelta(hours=i)).isoformat(),
            "rut_usuario": rut_usuario,
        }
        try:
            response = supabase.table("ventas").insert(venta).execute()
            if response.data:
                ventas.append(response.data[0]['idventa'])
                print(f"   ✅ Venta ${venta['total']:.0f}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    return ventas


def crear_movimientos_cero():
    """Simula inactividad prolongada (sin movimientos recientes)."""
    print("\n⏱️  Simulando inactividad prolongada...")
    print("   ℹ️  No se crearán movimientos en las últimas 6 horas")
    print("   (la ausencia de datos simula inactividad)")
    return True


def probar_deteccion():
    """Genera snapshot y prueba detección ML."""
    print("\n🔍 Probando detección ML con datos anómalos...")
    print("="*60)
    
    # Construir snapshot actual
    snapshot = snapshot_builder.build(contexto="auditoria")
    
    # Detectar anomalías
    detector = get_detector()
    insights = detector.get_anomaly_insights(snapshot)
    
    print("📋 RESULTADO DE DETECCIÓN ML:")
    print("="*60)
    print(f"¿Anomalía detectada? {'🔴 SÍ' if insights['is_anomaly'] else '🟢 NO'}")
    print(f"Score de anomalía: {insights['anomaly_score']:.3f}")
    print(f"Severidad ML: {insights['severity'].upper()}")
    
    if insights['top_contributors']:
        print(f"\n🎯 Top 3 features que indican anomalía:")
        for feature, contribution in insights['top_contributors']:
            print(f"   • {feature}: {contribution:.1%}")
    
    if insights['recommended_actions']:
        print(f"\n💡 Acciones recomendadas por ML:")
        for action in insights['recommended_actions']:
            print(f"   {action}")
    
    print("="*60)
    
    # Mostrar métricas del snapshot
    print(f"\n📊 Métricas del snapshot:")
    print(f"   • Alertas críticas: {snapshot.critical_alerts}")
    print(f"   • Alertas warning: {snapshot.warning_alerts}")
    print(f"   • Tendencia ventas: {snapshot.sales_trend_percent:.1%}")
    print(f"   • Inactividad (h): {snapshot.inactivity_hours:.1f}")
    print(f"   • Movimientos/h: {snapshot.movements_per_hour:.2f}")
    print(f"   • Señal compuesta: {snapshot.signal_strength:.2f}")
    
    return insights


def limpiar_datos_simulados(alertas_ids, ventas_ids):
    """Limpia los datos simulados de la BD."""
    print("\n🧹 Limpiando datos simulados automáticamente...")
    print("\n🗑️  Eliminando datos...")
    
    # Limpiar alertas
    for alerta_id in alertas_ids:
        try:
            supabase.table("alertas").delete().eq("id", alerta_id).execute()
            print(f"   ✅ Alerta {alerta_id} eliminada")
        except Exception as e:
            print(f"   ⚠️  Error eliminando alerta: {e}")
    
    # Limpiar ventas
    for venta_id in ventas_ids:
        try:
            supabase.table("ventas").delete().eq("idventa", venta_id).execute()
            print(f"   ✅ Venta {venta_id} eliminada")
        except Exception as e:
            print(f"   ⚠️  Error eliminando venta: {e}")
    
    print("\n✅ Limpieza completada")


def main():
    print("="*60)
    print("🧪 SIMULADOR DE ANOMALÍAS PARA ML")
    print("="*60)
    print("\nEste script creará datos anómalos TEMPORALES para probar el ML:")
    print("• 3-4 alertas críticas activas")
    print("• 5 ventas con valores muy bajos")
    print("• Simulación de inactividad prolongada")
    print("\n▶️  Ejecutando simulación...")
    
    # Crear datos anómalos
    alertas_ids = crear_alertas_criticas()
    ventas_ids = crear_ventas_bajas()
    crear_movimientos_cero()
    
    print("\n✅ Datos anómalos creados")
    print("\n⏳ Esperando 2 segundos para que se propaguen los datos...")
    import time
    time.sleep(2)
    
    # Probar detección
    insights = probar_deteccion()
    
    # Instrucciones
    print("\n" + "="*60)
    print("📱 PRUEBA EN EL FRONTEND:")
    print("="*60)
    print("1. Ve a http://localhost:5000/auditoria")
    print("2. Espera a que se cargue la recomendación IA")
    print("3. Deberías ver:")
    if insights['is_anomaly']:
        print("   🤖 Badge ML en la card")
        print("   📊 Panel 'Análisis ML' con score y severidad")
        print("   💡 Acciones recomendadas actualizadas")
    else:
        print("   ⚠️  El ML NO detectó anomalía suficiente")
        print("   💡 Prueba creando más alertas o esperando más tiempo")
    print("\n4. Refresca la página (F5) si no ves cambios")
    print("="*60)
    
    # Limpiar
    limpiar_datos_simulados(alertas_ids, ventas_ids)
    
    print("\n🎉 ¡Simulación completada!")


if __name__ == '__main__':
    main()
