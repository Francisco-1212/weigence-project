"""
Script para crear las tablas del sistema de chat
"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

def crear_tablas_chat():
    """Crea las tablas necesarias para el sistema de chat"""
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Error: Variables de entorno SUPABASE_URL y SUPABASE_KEY no encontradas")
        return False
    
    try:
        supabase = create_client(url, key)
        print("✅ Conectado a Supabase")
        
        # Leer el archivo SQL
        with open('migrations/create_chat_tables.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("\n📝 Ejecutando migración de tablas de chat...")
        print("⚠️  Nota: Debes ejecutar este SQL manualmente en el SQL Editor de Supabase")
        print("\n" + "="*60)
        print(sql)
        print("="*60)
        print("\n✅ Copia el SQL anterior y ejecútalo en Supabase SQL Editor")
        print("   URL: https://supabase.com/dashboard/project/_/sql")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    crear_tablas_chat()
