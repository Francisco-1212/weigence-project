"""
Muestra las recomendaciones ML completas en lenguaje amigable.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ia.ia_snapshots import snapshot_builder
from app.ia.ia_ml_anomalies import get_detector


def main():
    print("=" * 70)
    print("💡 RECOMENDACIONES ML - LENGUAJE AMIGABLE")
    print("=" * 70)
    
    # Construir snapshot
    snapshot = snapshot_builder.build(contexto="auditoria")
    
    # Obtener insights ML
    detector = get_detector()
    insights = detector.get_anomaly_insights(snapshot)
    
    print(f"\n{'🔴 ANOMALÍA DETECTADA' if insights['is_anomaly'] else '🟢 OPERACIÓN NORMAL'}")
    print(f"Nivel: {insights['severity'].upper()}")
    
    print(f"\n" + "=" * 70)
    print("📋 RECOMENDACIONES:")
    print("=" * 70)
    
    for i, rec in enumerate(insights['recommended_actions'], 1):
        print(f"\n{i}. {rec}")
    
    print("\n" + "=" * 70)
    print("📊 MÉTRICAS CLAVE:")
    print("=" * 70)
    print(f"• Alertas críticas: {snapshot.critical_alerts}")
    print(f"• Tendencia ventas: {snapshot.sales_trend_percent:.1f}%")
    print(f"• Inactividad: {snapshot.inactivity_hours:.1f}h")
    print(f"• Movimientos/h: {snapshot.movements_per_hour:.2f}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
