import mysql.connector

def conectar_db():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='tu_password',
            database='weigence'
        )
        return conexion
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None

def guardar_dato(peso):
    db = conectar_db()
    if db:
        cursor = db.cursor()
        query = "INSERT INTO pesajes (peso, fecha) VALUES (%s, NOW())"
        cursor.execute(query, (peso,))
        db.commit()
        db.close()
