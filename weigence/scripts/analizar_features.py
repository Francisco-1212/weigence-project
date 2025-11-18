"""
Analiza features del snapshot actual vs datos de entrenamiento
para entender por qué el modelo no detecta anomalías.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List

# Agregar app al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.ia.ia_snapshots import snapshot_builder, IASnapshot
from app.ia.ia_ml_anomalies import AnomalyDetector


def generar_snapshots_historicos(dias: int = 7) -> List[IASnapshot]:
    """Genera snapshots históricos para análisis"""
    print(f"📊 Generando {dias} snapshots históricos...\n")
    snapshots = []
    
    for i in range(dias):
        dias_atras = i
        snapshot = snapshot_builder.build(offset_days=dias_atras)
        snapshots.append(snapshot)
        
        print(f"  Día -{dias_atras}:")
        print(f"    • Tendencia ventas: {snapshot.sales_trend_percent:.1f}%")
        print(f"    • Alertas críticas: {snapshot.critical_alerts}")
        print(f"    • Inactividad (h): {snapshot.inactivity_hours:.1f}")
        print(f"    • Movimientos/h: {snapshot.movements_per_hour:.2f}")
    
    return snapshots


def analizar_distribucion(snapshots: List[IASnapshot]):
    """Analiza la distribución de features"""
    print("\n" + "=" * 60)
    print("📈 ANÁLISIS DE DISTRIBUCIÓN DE FEATURES")
    print("=" * 60)
    
    # Extraer features
    detector = AnomalyDetector()
    features_list = [detector.extract_features(s) for s in snapshots]
    
    import numpy as np
    features_array = np.array(features_list)
    
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
    
    print("\nEstadísticas de features (datos de entrenamiento):\n")
    for i, name in enumerate(feature_names):
        values = features_array[:, i]
        print(f"{name:25} | Min: {values.min():8.2f} | Max: {values.max():8.2f} | "
              f"Mean: {values.mean():8.2f} | Std: {values.std():8.2f}")


def comparar_con_actual():
    """Compara snapshot actual con histórico"""
    print("\n" + "=" * 60)
    print("🎯 COMPARACIÓN: ACTUAL vs HISTÓRICO")
    print("=" * 60)
    
    # Snapshot actual
    actual = snapshot_builder.build()
    
    # Extraer features
    detector = AnomalyDetector()
    features_actual = detector.extract_features(actual)
    
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
    
    print("\nFeatures del snapshot ACTUAL:\n")
    for i, name in enumerate(feature_names):
        value = features_actual[i]
        print(f"{name:25} = {value:8.2f}")
    
    # Análisis específico
    print("\n" + "=" * 60)
    print("🔍 ANÁLISIS DE ANOMALÍAS:")
    print("=" * 60)
    
    print(f"\n📉 Tendencia ventas: {actual.sales_trend_percent:.1f}%")
    if actual.sales_trend_percent < -50:
        print("   ⚠️  CRÍTICO: Caída mayor a 50%")
    elif actual.sales_trend_percent < -20:
        print("   ⚠️  ALTO: Caída mayor a 20%")
    
    print(f"\n🚨 Alertas críticas: {actual.critical_alerts}")
    if actual.critical_alerts >= 3:
        print("   ⚠️  CRÍTICO: 3+ alertas críticas activas")
    elif actual.critical_alerts >= 1:
        print("   ⚠️  MODERADO: Alertas críticas presentes")
    
    print(f"\n⏱️  Inactividad: {actual.inactivity_hours:.1f}h")
    if actual.inactivity_hours >= 3:
        print("   ⚠️  ALTO: Más de 3 horas sin actividad")
    elif actual.inactivity_hours >= 1:
        print("   ⚠️  MODERADO: Inactividad prolongada")
    
    print(f"\n📊 Movimientos/hora: {actual.movements_per_hour:.2f}")
    if actual.movements_per_hour < 0.5:
        print("   ⚠️  BAJO: Actividad muy reducida")


def main():
    print("🤖 ANALIZADOR DE FEATURES ML - DIAGNÓSTICO DE DETECCIÓN")
    print("=" * 60)
    
    # 1. Generar snapshots históricos
    snapshots = generar_snapshots_historicos(dias=7)
    
    # 2. Analizar distribución
    analizar_distribucion(snapshots)
    
    # 3. Comparar con actual
    comparar_con_actual()
    
    print("\n" + "=" * 60)
    print("✅ Análisis completado")
    print("=" * 60)


if __name__ == "__main__":
    main()
