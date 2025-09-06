from lectura_sensores.lector_peso import leer_peso
from procesamiento.procesador_datos import analizar_peso
from conexion_bd.conexion_supabase import guardar_dato   # <- ahora usa Supabase

import time

def ciclo_principal():
    print("🔁 Iniciando ciclo de pesaje...")

    peso_referencia = 1000.0  # peso esperado del producto (gramos)

    while True:
        peso_actual = leer_peso()
        print(f"📦 Peso leído: {peso_actual} g")

        resultado = analizar_peso(peso_actual, peso_referencia)
        print(f"📊 Resultado: {resultado}")

        # Guardar en Supabase
        try:
            guardar_dato(resultado["peso"], resultado["alerta"])
            print("✅ Datos guardados en Supabase.\n")
        except Exception as e:
            print("❌ Error al guardar:", e)

        time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura

if __name__ == "__main__":
    try:
        ciclo_principal()
    except KeyboardInterrupt:
        print("\n🛑 Interrupción manual. Finalizando proceso.")
