"""
Script de depuración para verificar usuarios conectados
"""
import sys
sys.path.insert(0, 'E:/Github/weigence-project/weigence')

from app.utils.sesiones_activas import obtener_usuarios_conectados, obtener_total_conectados
from datetime import datetime

def verificar_usuarios_conectados():
    """Muestra el estado actual de usuarios conectados"""
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE USUARIOS CONECTADOS")
    print("="*60)
    print(f"⏰ Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Obtener usuarios conectados
    usuarios_ruts, detalles = obtener_usuarios_conectados(timeout_minutos=2)
    total = obtener_total_conectados()
    
    print(f"📊 Total usuarios conectados: {total}")
    print()
    
    if not usuarios_ruts:
        print("⚠️  No hay usuarios conectados actualmente")
    else:
        print("👥 Lista de usuarios conectados:")
        print("-" * 60)
        for rut in usuarios_ruts:
            if rut in detalles:
                info = detalles[rut]
                nombre = info.get('nombre', 'N/A')
                rol = info.get('rol', 'N/A')
                ultima = info.get('ultima_actividad', 'N/A')
                
                print(f"  • {nombre}")
                print(f"    RUT: {rut}")
                print(f"    Rol: {rol}")
                print(f"    Última actividad: {ultima}")
                print()
    
    print("="*60)
    print()

if __name__ == "__main__":
    try:
        verificar_usuarios_conectados()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
