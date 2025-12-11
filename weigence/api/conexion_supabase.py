# conexion_bd/conexion_supabase.py
import os
from supabase import create_client, Client, ClientOptions
from dotenv import load_dotenv
import httpx

# Cargar variables del .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configurar httpx con límites de conexión y timeouts más generosos
# HTTP/2 puede causar problemas en Windows con sockets no bloqueantes
# Usar HTTP/1.1 para mayor estabilidad
httpx_client = httpx.Client(
    timeout=httpx.Timeout(30.0, connect=10.0, read=20.0, write=20.0, pool=5.0),
    limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
    http2=False,  # Deshabilitado para evitar WinError 10035 en Windows
    follow_redirects=True
)

# Crear cliente con ClientOptions y httpx personalizado
supabase: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_KEY,
    options=ClientOptions(
        postgrest_client_timeout=30,
        storage_client_timeout=30,
        schema="public",
        headers={
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=30, max=100"
        }
    )
)

# Inyectar el cliente httpx personalizado en el cliente postgrest de Supabase
# Esto mejora la estabilidad en Windows evitando errores de socket
try:
    if hasattr(supabase, 'postgrest') and hasattr(supabase.postgrest, 'session'):
        supabase.postgrest.session = httpx_client
except Exception as e:
    print(f"⚠️ No se pudo configurar cliente httpx personalizado: {e}")

def guardar_dato(peso, alerta=False, idproducto=1, pesado_por="00000000-0000-0000-0000-000000000000"):
   
   # Guarda un registro en la tabla pesajes de Supabase
   # - peso: valor leído del sensor
   # - alerta: bool si está bajo el peso de referencia
   # - idproducto: id del producto relacionado
   # - pesado_por: uuid del usuario que realizó el pesaje
   
    try:
        data = supabase.table("pesajes").insert({
            "idproducto": idproducto,
            "peso_unitario": peso,
            "pesado_por": pesado_por
        }).execute()

        print(f"✅ Registro guardado en Supabase: {data.data}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar en Supabase: {e}")
        return False

supabase.table("productos").select("idproducto").limit(1).execute()
print("Conexión a Supabase exitosa.")