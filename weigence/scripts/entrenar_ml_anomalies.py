"""
Script para entrenar el modelo de detección de anomalías con datos históricos.
Ejecutar: python scripts/entrenar_ml_anomalies.py
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from app.ia.ia_snapshots import snapshot_builder
from app.ia.ia_ml_anomalies import get_detector


def entrenar_modelo(dias_historicos: int = 7):
    """
    Entrena el modelo con snapshots históricos simulados.
    
    Args:
        dias_historicos: Número de días de histórico a simular
    """
    print(f"🤖 Entrenando modelo de ML con {dias_historicos} días de histórico...")
    
    # Generar snapshots históricos (uno por día)
    snapshots = []
    for i in range(dias_historicos):
        print(f"📊 Generando snapshot día -{i}...")
        try:
            snapshot = snapshot_builder.build(contexto="auditoria")
            snapshots.append(snapshot)
        except Exception as e:
            print(f"⚠️  Error generando snapshot: {e}")
    
    if len(snapshots) < 5:
        print(f"❌ Snapshots insuficientes ({len(snapshots)}). Mínimo: 5")
        print("💡 Asegúrate de tener datos en las tablas:")
        print("   - ventas (últimas 48-72h)")
        print("   - pesajes (últimas 72h)")
        print("   - movimientos_inventario (últimas 48h)")
        print("   - alertas (últimas 48h)")
        return False
    
    print(f"\n✅ {len(snapshots)} snapshots generados correctamente")
    
    # Entrenar modelo
    detector = get_detector()
    success = detector.fit_from_snapshots(snapshots)
    
    if success:
        print("\n🎉 ¡Modelo entrenado exitosamente!")
        print(f"📈 Features utilizadas: {len(detector._feature_names)}")
        print(f"📊 Features: {', '.join(detector._feature_names)}")
        
        # Probar con snapshot actual
        print("\n🔍 Probando detección con snapshot actual...")
        current_snapshot = snapshot_builder.build(contexto="auditoria")
        insights = detector.get_anomaly_insights(current_snapshot)
        
        print(f"\n{'='*60}")
        print("📋 RESULTADO DE DETECCIÓN:")
        print(f"{'='*60}")
        print(f"¿Anomalía detectada? {'🔴 SÍ' if insights['is_anomaly'] else '🟢 NO'}")
        print(f"Score de anomalía: {insights['anomaly_score']:.3f}")
        print(f"Severidad: {insights['severity'].upper()}")
        
        if insights['top_contributors']:
            print(f"\n🎯 Top 3 features contribuyentes:")
            for feature, contribution in insights['top_contributors']:
                print(f"   • {feature}: {contribution:.1%}")
        
        if insights['recommended_actions']:
            print(f"\n💡 Acciones recomendadas:")
            for action in insights['recommended_actions']:
                print(f"   {action}")
        
        print(f"{'='*60}\n")
        
        return True
    else:
        print("\n❌ Error al entrenar el modelo")
        return False


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Entrenar modelo ML de detección de anomalías')
    parser.add_argument(
        '--dias',
        type=int,
        default=7,
        help='Número de días de histórico a usar (default: 7)'
    )
    
    args = parser.parse_args()
    
    success = entrenar_modelo(dias_historicos=args.dias)
    sys.exit(0 if success else 1)
