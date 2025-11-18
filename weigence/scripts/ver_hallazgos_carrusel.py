"""
Muestra los hallazgos ML que se mostrarán en el carrusel.
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ia.ia_snapshots import snapshot_builder
from app.ia.ia_ml_anomalies import get_detector


def main():
    print("=" * 70)
    print("🎠 HALLAZGOS DEL CARRUSEL ML")
    print("=" * 70)
    
    # Construir snapshot
    snapshot = snapshot_builder.build(contexto="auditoria")
    
    # Obtener insights ML
    detector = get_detector()
    insights = detector.get_anomaly_insights(snapshot)
    
    findings = insights.get('findings', [])
    
    print(f"\n📊 Total de hallazgos: {len(findings)}")
    print(f"🔴 Anomalía detectada: {'SÍ' if insights['is_anomaly'] else 'NO'}")
    print(f"📈 Severidad: {insights['severity'].upper()}")
    
    print(f"\n" + "=" * 70)
    print("🎯 HALLAZGOS PARA EL CARRUSEL:")
    print("=" * 70)
    
    for i, finding in enumerate(findings, 1):
        print(f"\n{'─' * 70}")
        print(f"Card {i}/{len(findings)}")
        print(f"{'─' * 70}")
        print(f"{finding['emoji']}  {finding['title']}")
        print(f"\n{finding['description']}")
    
    print(f"\n" + "=" * 70)
    print("\n📋 JSON para frontend:")
    print(json.dumps(findings, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
