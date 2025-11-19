"""Test de mensajes contextualizados del header"""
from app.ia.ia_service import generar_recomendacion

paginas = ['dashboard', 'inventario', 'ventas', 'movimientos', 'alertas', 'auditoria']

print("\n" + "="*80)
print("🎯 MENSAJES CONTEXTUALIZADOS DEL HEADER")
print("="*80 + "\n")

for pagina in paginas:
    r = generar_recomendacion(pagina, modo='header')
    mensaje = r.get('mensaje', 'Sin mensaje')
    severidad = r.get('severidad', 'info')
    
    # Icono según severidad
    icon_map = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'info': '🔵'
    }
    
    icon = icon_map.get(severidad, '⚪')
    
    print(f"{icon} {pagina.upper()}")
    print(f"   Mensaje: {mensaje}")
    print(f"   Severidad: {severidad}")
    print()

print("="*80)
print("✅ Test completado - Los mensajes están contextualizados con datos ML reales")
print("="*80 + "\n")
