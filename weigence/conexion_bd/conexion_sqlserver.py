import pyodbc
import sys
import os

# Agregar la carpeta raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lectura_sensores.lector_peso import leer_peso

def conectar_bd():
    """Conecta a la base de datos SQL Server"""
    try:
        # Configuración basada en tu SSMS (Windows Authentication)
        conexion_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=(localdb)\\weigence;"  # Tu servidor mostrado en SSMS
            "DATABASE=weigence;"
            "Trusted_Connection=yes;"
            "Connection Timeout=30;"
        )
        
        
        print("🔄 Intentando conectar a SQL Server...")
        conexion = pyodbc.connect(conexion_string)
        print("✅ Conexión exitosa a SQL Server!")
        return conexion
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def probar_conexion():
    """Prueba la conexión a la base de datos"""
    print("Iniciando prueba de conexión...")
    
    db = conectar_bd()
    if db:
        try:
            cursor = db.cursor()
            # Prueba simple: obtener la versión de SQL Server
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"✅ Versión de SQL Server: {version[0][:50]}...")
            
            # Verificar si existe la base de datos
            cursor.execute("SELECT DB_NAME()")
            db_name = cursor.fetchone()
            print(f"✅ Base de datos actual: {db_name[0]}")
            
            cursor.close()
            db.close()
            print("✅ Prueba de conexión completada exitosamente.")
            
        except Exception as e:
            print(f"❌ Error durante la prueba: {e}")
            if db:
                db.close()
    else:
        print("❌ No se pudo establecer la conexión con la BD.")

def guardar_dato(peso, alerta=False):
    """Guarda un dato de peso en la base de datos"""
    db = conectar_bd()
    if db:
        try:
            cursor = db.cursor()
            query = """
                INSERT INTO pesajes (peso, alerta, fecha) 
                VALUES (?, ?, GETDATE())
            """
            cursor.execute(query, (peso, alerta))
            db.commit()
            print(f"✅ Dato guardado: {peso}g, Alerta: {alerta}")
            cursor.close()
            db.close()
            return True
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            if db:
                db.close()
            return False
    return False

def crear_tabla_si_no_existe():
    """Crea la tabla pesajes si no existe"""
    db = conectar_bd()
    if db:
        try:
            cursor = db.cursor()
            query = """
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='pesajes' AND xtype='U')
                CREATE TABLE pesajes (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    peso DECIMAL(10,2) NOT NULL,
                    alerta BIT DEFAULT 0,
                    fecha DATETIME DEFAULT GETDATE()
                )
            """
            cursor.execute(query)
            db.commit()
            print("✅ Tabla 'pesajes' verificada/creada correctamente")
            cursor.close()
            db.close()
        except Exception as e:
            print(f"❌ Error al crear tabla: {e}")
            if db:
                db.close()

if __name__ == "__main__":
    # Primero probar la conexión
    probar_conexion()
    
    # Crear tabla si no existe
    crear_tabla_si_no_existe()
    
    # Prueba de lectura de sensor y guardado
    try:
        peso_actual = leer_peso()
        print(f"📊 Peso leído del sensor: {peso_actual}g")
        
        alerta = peso_actual < 800  # Ejemplo de lógica de alerta
        guardar_dato(peso_actual, alerta)
        
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")