"""Test final de mensajes ML con datos reales"""
from app.ia.ia_service import generar_recomendacion
import json

r = generar_recomendacion('auditoria')
cards = r.get('ml_insights_cards', [])

print(f"\n🎯 TOTAL DE INSIGHTS ML: {len(cards)}\n")
print("=" * 80)

for i, c in enumerate(cards, 1):
    print(f"\n{i}. [{c['modulo'].upper()}] {c['emoji']} {c['ml_severity'].upper()}")
    print(f"   TÍTULO: {c['titulo']}")
    print(f"   DESC: {c['descripcion']}")
    print(f"   PLAN: {c['plan_accion']}")
    print("-" * 80)
