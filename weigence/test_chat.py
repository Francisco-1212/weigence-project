"""
Script de prueba para verificar el sistema de chat
"""
from api.conexion_supabase import supabase

def test_chat():
    print("="*60)
    print("🔍 PRUEBA DEL SISTEMA DE CHAT")
    print("="*60)
    
    try:
        # Test 1: Verificar tabla conversaciones_chat
        print("\n✓ Test 1: Verificando tabla 'conversaciones_chat'...")
        result = supabase.table('conversaciones_chat').select('*').limit(1).execute()
        print(f"  ✅ Tabla existe. Registros: {len(result.data)}")
        
        # Test 2: Verificar tabla participantes_chat
        print("\n✓ Test 2: Verificando tabla 'participantes_chat'...")
        result = supabase.table('participantes_chat').select('*').limit(1).execute()
        print(f"  ✅ Tabla existe. Registros: {len(result.data)}")
        
        # Test 3: Verificar tabla mensajes_chat
        print("\n✓ Test 3: Verificando tabla 'mensajes_chat'...")
        result = supabase.table('mensajes_chat').select('*').limit(1).execute()
        print(f"  ✅ Tabla existe. Registros: {len(result.data)}")
        
        # Test 4: Verificar usuarios disponibles
        print("\n✓ Test 4: Verificando usuarios disponibles...")
        result = supabase.table('usuarios').select('idusuario, nombre, apellido, email').limit(5).execute()
        print(f"  ✅ Usuarios encontrados: {len(result.data)}")
        for user in result.data[:3]:
            print(f"     - {user.get('nombre')} {user.get('apellido')} ({user.get('email')})")
        
        print("\n" + "="*60)
        print("✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        print("="*60)
        print("\n📌 El sistema de chat está listo para usar")
        print("   Navega a: http://localhost:5000/chat")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 SOLUCIÓN:")
        print("   1. Verifica que hayas ejecutado el SQL en Supabase")
        print("   2. Revisa CHAT_INSTALACION_RAPIDA.md para instrucciones")
        return False

if __name__ == "__main__":
    test_chat()
