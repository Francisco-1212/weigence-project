"""
Script de prueba para verificar que el módulo de Auditoría + ML funciona correctamente.
Ejecutar: python scripts/test_auditoria_ml.py
"""
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ia.ia_service import generar_recomendacion


def test_auditoria_ml():
    """Prueba el flujo completo de Auditoría + ML"""
    
    print("=" * 60)
    print("🧪 TESTING: Módulo de Auditoría + ML")
    print("=" * 60)
    
    # Generar recomendación para auditoría
    print("\n📊 Generando recomendación para módulo 'auditoria'...")
    resultado = generar_recomendacion(contexto="auditoria")
    
    # Verificar estructura básica
    print("\n✅ Estructura de respuesta:")
    print(f"   - ok: {resultado.get('ok', False)}")
    print(f"   - contexto: {resultado.get('contexto', 'N/A')}")
    print(f"   - severidad: {resultado.get('severidad', 'N/A')}")
    
    # Verificar ML
    print("\n🤖 Datos de ML:")
    print(f"   - Anomalía detectada: {resultado.get('ml_anomaly_detected', False)}")
    print(f"   - Score: {resultado.get('ml_anomaly_score', 0):.3f}")
    print(f"   - Severidad ML: {resultado.get('ml_severity', 'N/A')}")
    
    # Verificar hallazgos (debe haber 6)
    insights_cards = resultado.get('ml_insights_cards', [])
    print(f"\n🎠 Hallazgos ML ({len(insights_cards)} tarjetas):")
    
    if len(insights_cards) != 6:
        print(f"   ⚠️ ERROR: Se esperaban 6 tarjetas, se recibieron {len(insights_cards)}")
    else:
        print("   ✅ Correcto: 6 tarjetas generadas")
    
    # Mostrar cada hallazgo
    modulos_esperados = {'dashboard', 'inventario', 'movimientos', 'ventas', 'alertas', 'auditoria'}
    modulos_encontrados = set()
    
    for i, card in enumerate(insights_cards, 1):
        modulo = card.get('modulo', 'N/A')
        titulo = card.get('titulo', card.get('title', 'N/A'))
        emoji = card.get('emoji', card.get('icono', '?'))
        
        print(f"\n   {i}. {emoji} {titulo}")
        print(f"      Módulo: {modulo}")
        print(f"      Descripción: {card.get('descripcion', card.get('description', 'N/A'))[:60]}...")
        
        modulos_encontrados.add(modulo)
    
    # Verificar que todos los módulos estén presentes
    print("\n🔍 Verificación de módulos:")
    modulos_faltantes = modulos_esperados - modulos_encontrados
    modulos_extras = modulos_encontrados - modulos_esperados
    
    if modulos_faltantes:
        print(f"   ⚠️ Módulos faltantes: {modulos_faltantes}")
    if modulos_extras:
        print(f"   ⚠️ Módulos no esperados: {modulos_extras}")
    
    if not modulos_faltantes and not modulos_extras:
        print("   ✅ Todos los módulos presentes correctamente")
    
    # Verificar mensajes
    print("\n💬 Mensajes generados:")
    print(f"   - Título: {resultado.get('titulo', 'N/A')}")
    print(f"   - Mensaje: {resultado.get('mensaje', 'N/A')[:80]}...")
    print(f"   - Solución: {resultado.get('solucion', 'N/A')[:80]}...")
    
    # Resumen final
    print("\n" + "=" * 60)
    if len(insights_cards) == 6 and not modulos_faltantes and not modulos_extras:
        print("🎉 ¡TEST EXITOSO! El módulo funciona correctamente.")
    else:
        print("❌ TEST FALLIDO. Revisar errores arriba.")
    print("=" * 60)


if __name__ == '__main__':
    try:
        test_auditoria_ml()
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
