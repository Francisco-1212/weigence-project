import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
