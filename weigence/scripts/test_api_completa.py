"""
Simula una llamada completa a la API de recomendaciones para ver
todos los mensajes que llegarán al frontend.
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ia.ia_service import generar_recomendacion


def main():
    print("=" * 70)
    print("📡 RESPUESTA COMPLETA DE LA API")
    print("=" * 70)
    
    # Generar recomendación completa
    resultado = generar_recomendacion(contexto="auditoria")
    
    print(f"\n🎯 DATOS PRINCIPALES:")
    print(f"   Título: {resultado.get('titulo')}")
    print(f"   Severidad: {resultado.get('severidad')}")
    print(f"   ML Detectó anomalía: {resultado.get('ml_anomaly_detected')}")
    print(f"   ML Severidad: {resultado.get('ml_severity')}")
    
    print(f"\n📝 MENSAJE:")
    print(f"   {resultado.get('mensaje')}")
    
    print(f"\n💡 PLAN SUGERIDO:")
    print(f"   {resultado.get('solucion')}")
    
    print(f"\n📊 SITUACIÓN ACTUAL:")
    print(f"   {resultado.get('situacion_actual')}")
    
    print(f"\n🎠 HALLAZGOS DEL CARRUSEL ({len(resultado.get('ml_insights_cards', []))}):")
    for i, card in enumerate(resultado.get('ml_insights_cards', []), 1):
        print(f"\n   Card {i}:")
        print(f"   {card['icono']} {card['titulo']}")
        print(f"   → {card['descripcion'][:60]}...")
    
    print(f"\n" + "=" * 70)
    print("📋 JSON COMPLETO:")
    print("=" * 70)
    print(json.dumps({
        'titulo': resultado.get('titulo'),
        'mensaje': resultado.get('mensaje'),
        'situacion_actual': resultado.get('situacion_actual'),
        'ml_insights_cards': resultado.get('ml_insights_cards'),
        'severidad': resultado.get('severidad'),
        'ml_anomaly_detected': resultado.get('ml_anomaly_detected'),
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
