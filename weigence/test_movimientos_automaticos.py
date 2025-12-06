"""
Script de prueba para validar el sistema de movimientos automáticos desde lecturas de peso.
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"  # Ajusta según tu configuración
API_KEY = "tu_api_key_aqui"  # Si usas autenticación por API key

def test_procesar_lectura_peso():
    """
    Prueba el endpoint que procesa lecturas de peso y genera movimientos automáticos.
    """
    print("=" * 60)
    print("TEST: Procesamiento de lectura de peso automática")
    print("=" * 60)
    
    # Datos de prueba (simula una lectura del sensor)
    lectura_data = {
        "id_lectura": 999,  # ID de prueba
        "id_estante": 6,  # Estante del ejemplo CSV
        "peso_leido": 156.0,  # Peso detectado
        "diferencia_anterior": 22.0,  # Diferencia con lectura anterior
        "timestamp": datetime.now().isoformat(),
        "es_anomalia": False
    }
    
    print("\n📊 Datos de lectura:")
    print(json.dumps(lectura_data, indent=2))
    
    # Hacer request al endpoint de testing (sin autenticación)
    endpoint = f"{BASE_URL}/api/lecturas_peso/test"
    
    try:
        response = requests.post(
            endpoint,
            json=lectura_data,
            headers={
                "Content-Type": "application/json",
                # "Authorization": f"Bearer {API_KEY}"  # Si usas auth
            }
        )
        
        print(f"\n📡 Status Code: {response.status_code}")
        print(f"📄 Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("\n✅ Movimiento automático creado exitosamente!")
                print(f"ID Movimiento: {result.get('movimiento_id')}")
                print(f"Tipo: {result.get('tipo_movimiento')}")
                print(f"Cantidad detectada: {result.get('cantidad_unidades')} unidades")
                print(f"Peso total: {result.get('peso_total')} kg")
            else:
                print(f"\n⚠️ Error: {result.get('message')}")
        else:
            print(f"\n❌ Error en request: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("Asegúrate de que la aplicación esté corriendo en", BASE_URL)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")

def test_obtener_movimientos_automaticos():
    """
    Verifica que los movimientos automáticos se muestren correctamente.
    """
    print("\n" + "=" * 60)
    print("TEST: Obtención de movimientos (incluyendo automáticos)")
    print("=" * 60)
    
    endpoint = f"{BASE_URL}/api/movimientos"
    
    try:
        response = requests.get(endpoint)
        
        if response.status_code == 200:
            movimientos = response.json()
            
            # Filtrar movimientos automáticos
            automaticos = [m for m in movimientos if m.get("tipo_evento") == "Automático"]
            
            print(f"\n📊 Total de movimientos: {len(movimientos)}")
            print(f"🤖 Movimientos automáticos: {len(automaticos)}")
            
            if automaticos:
                print("\n🔍 Últimos 5 movimientos automáticos:")
                for mov in automaticos[:5]:
                    print(f"  - ID: {mov.get('id_movimiento')} | "
                          f"Peso: {mov.get('peso_total')}kg | "
                          f"Estante: {mov.get('ubicacion')} | "
                          f"Timestamp: {mov.get('timestamp')}")
            else:
                print("\n⚠️ No se encontraron movimientos automáticos.")
                
        else:
            print(f"\n❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

def main():
    """
    Ejecuta todas las pruebas.
    """
    print("\n🚀 Iniciando pruebas del sistema de movimientos automáticos\n")
    
    # Test 1: Procesar lectura de peso
    test_procesar_lectura_peso()
    
    # Test 2: Verificar movimientos automáticos
    test_obtener_movimientos_automaticos()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
    print("=" * 60)

if __name__ == "__main__":
    main()
