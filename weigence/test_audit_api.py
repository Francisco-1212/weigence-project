"""
Test para verificar que /api/auditoria/logs retorna eventos error_sistema
"""

import requests
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/login"
AUDIT_URL = f"{BASE_URL}/api/auditoria/logs"

# Crear sesión
session = requests.Session()

print("🔐 Iniciando sesión...")
login_data = {
    "email": "admin@weigence.cl",
    "password": "admin123"
}

# Login
response = session.post(LOGIN_URL, data=login_data, allow_redirects=False)
print(f"   Login status: {response.status_code}")

# Obtener logs
print("\n📊 Solicitando logs de auditoría...")
params = {
    "horas": 24,
    "limit": 200
}

response = session.get(AUDIT_URL, params=params)
print(f"   API status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    if data.get("ok"):
        logs = data.get("logs", [])
        print(f"\n✅ Total de logs recibidos: {len(logs)}")
        
        # Filtrar errores del sistema
        errores_sistema = [log for log in logs if log.get("tipo_evento") == "error_sistema"]
        print(f"🔍 Errores del sistema encontrados: {len(errores_sistema)}")
        
        if errores_sistema:
            print("\n📋 Detalles de errores del sistema:")
            for i, error in enumerate(errores_sistema[:5], 1):
                print(f"\n{i}. Timestamp: {error.get('timestamp')}")
                print(f"   Severidad: {error.get('severidad')}")
                print(f"   Usuario: {error.get('usuario')}")
                print(f"   Mensaje: {error.get('mensaje')[:100]}...")
        else:
            print("\n⚠️ No se encontraron errores del sistema en los logs")
            
            # Mostrar tipos de eventos presentes
            tipos_presentes = {}
            for log in logs:
                tipo = log.get("tipo_evento", "sin_tipo")
                tipos_presentes[tipo] = tipos_presentes.get(tipo, 0) + 1
            
            print("\n📊 Tipos de eventos presentes:")
            for tipo, count in sorted(tipos_presentes.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {tipo}: {count}")
    else:
        print(f"❌ Error en respuesta: {data.get('error')}")
else:
    print(f"❌ Error HTTP: {response.status_code}")
    print(f"   Respuesta: {response.text[:200]}")
