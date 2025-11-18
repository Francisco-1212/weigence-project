from api.conexion_supabase import supabase
import json

# Obtener un registro de ejemplo
result = supabase.table('ia_auditoria_logs').select('*').limit(1).execute()

if result.data:
    print('✅ Estructura de ia_auditoria_logs:')
    print(json.dumps(result.data[0], indent=2, default=str))
else:
    print('⚠️ Tabla vacía - No hay registros para analizar')
