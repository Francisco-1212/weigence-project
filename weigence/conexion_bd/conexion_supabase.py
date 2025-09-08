import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables del .env

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Configuración de Supabase
SUPABASE_URL = "https://yxptnftmezemrvowosto.supabase.co"  # Esta variable debe estar en tu archivo .env
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Esta variable debe estar en tu archivo .env

# Crear cliente de Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_dato(peso, alerta=False, idproducto=1, pesado_por="00000000-0000-0000-0000-000000000000"):
    """
    Guarda un registro en la tabla pesajes de Supabase
    
    Args:
        peso (float): valor leído del sensor
        alerta (bool): si está bajo el peso de referencia
        idproducto (int): id del producto relacionado
        pesado_por (str): uuid del usuario que realizó el pesaje
    
    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    try:
        data = supabase.table("pesajes").insert({
            "idproducto": idproducto,
            "peso_unitario": peso,
            "pesado_por": pesado_por,
            "alerta": alerta  # Agregué el campo alerta que tenías como parámetro
        }).execute()

        print(f"✅ Registro guardado en Supabase: {data.data}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar en Supabase: {e}")
        return False

# Función para verificar la conexión
def verificar_conexion():
    """
    Verifica si la conexión con Supabase está funcionando
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        # Intenta hacer una consulta simple para verificar la conexión
        result = supabase.table("pesajes").select("*").limit(1).execute()
        print("✅ Conexión con Supabase exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión con Supabase: {e}")
        return False

# Ejemplo de uso
if __name__ == "__main__":
    # Verificar conexión al ejecutar el archivo directamente
    if verificar_conexion():
        print("🔗 Cliente de Supabase listo para usar")
    else:
        print("⚠️ Revisar configuración de Supabase")