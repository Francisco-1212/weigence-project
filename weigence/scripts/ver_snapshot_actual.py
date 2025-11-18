"""
Muestra los valores del snapshot actual para entender
qué datos está viendo el modelo ML.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ia.ia_snapshots import snapshot_builder
from app.ia.ia_ml_anomalies import get_detector


def main():
    print("=" * 70)
    print("📊 SNAPSHOT ACTUAL - VALORES RAW")
    print("=" * 70)
    
    # Construir snapshot
    snapshot = snapshot_builder.build(contexto="auditoria")
    
    # Mostrar todos los atributos relevantes
    print(f"\n💰 VENTAS:")
    print(f"   • Tendencia: {snapshot.sales_trend_percent:.2f}%")
    print(f"   • Score anomalía: {snapshot.sales_anomaly_score:.3f}")
    print(f"   • Volatilidad: {snapshot.sales_volatility:.2f}")
    
    print(f"\n⚖️  PESO:")
    print(f"   • Volatilidad: {snapshot.weight_volatility:.2f}")
    print(f"   • Tasa cambio: {snapshot.weight_change_rate:.2f}")
    
    print(f"\n📦 MOVIMIENTOS:")
    print(f"   • Por hora: {snapshot.movements_per_hour:.2f}")
    print(f"   • Horas inactividad: {snapshot.inactivity_hours:.2f}")
    
    print(f"\n🚨 ALERTAS:")
    print(f"   • Críticas: {snapshot.critical_alerts}")
    print(f"   • Warnings: {snapshot.warning_alerts}")
    
    print(f"\n📡 SEÑAL:")
    print(f"   • Strength: {snapshot.signal_strength:.2f}")
    
    # Extraer features normalizadas
    print(f"\n" + "=" * 70)
    print("🔢 FEATURES EXTRAÍDAS (lo que ve el modelo):")
    print("=" * 70)
    
    detector = get_detector()  # Singleton con auto-load
    features = detector.extract_features(snapshot)
    
    feature_names = [
        'sales_trend_percent',
        'sales_anomaly_score',
        'sales_volatility',
        'weight_volatility',
        'weight_change_rate',
        'movements_per_hour',
        'inactivity_hours',
        'critical_alerts',
        'warning_alerts',
        'signal_strength'
    ]
    
    for i, name in enumerate(feature_names):
        val = features.flat[i] if hasattr(features, 'flat') else features[i]
        print(f"   {i+1:2}. {name:25} = {float(val):10.3f}")
    
    # Probar detección
    print(f"\n" + "=" * 70)
    print("🤖 RESULTADO DE DETECCIÓN ML:")
    print("=" * 70)
    
    insights = detector.get_anomaly_insights(snapshot)
    
    print(f"\n¿Anomalía? {'🔴 SÍ' if insights['is_anomaly'] else '🟢 NO'}")
    print(f"Score: {insights['anomaly_score']:.3f}")
    print(f"Severidad: {insights['severity'].upper()}")
    
    if insights['top_contributors']:
        print(f"\nTop contribuyentes:")
        for feature, contrib in insights['top_contributors']:
            print(f"   • {feature}: {contrib:.1%}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
