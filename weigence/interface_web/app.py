from flask import Flask, render_template
import mysql.connector
from datetime import datetime

app = Flask(__name__)

def obtener_datos():
    # Datos simulados para no conectar a MySQL
    return (
        (1000.0, False, '2025-07-18 18:00:00'),
        (950.5, True, '2025-07-18 18:05:00'),
        (1020.3, False, '2025-07-18 18:10:00'),
        (980.2, True, '2025-07-18 18:15:00'),
        (990.0, False, '2025-07-18 18:20:00'),
        (1000.5, False, '2025-07-18 18:00:00'),
        (950.0, True, '2025-07-18 18:05:00'),
        (1010.2, False, '2025-07-18 18:10:00'),
    )
    cursor = db.cursor()
    cursor.execute("SELECT peso, alerta, fecha FROM pesajes ORDER BY fecha DESC LIMIT 10")
    datos = cursor.fetchall()
    db.close()
    return datos

@app.route("/")
def index():
    datos = obtener_datos()
    return render_template("index.html", registros=datos)
@app.route("/alertas")

def alertas():
    # Simulación de datos de alertas con producto y estado de revisión
    registros = [
        {"peso": 250, "alerta": True, "fecha": "2025-07-18 13:00:00", "producto": "Estante A", "revisada": False},
        {"peso": 180, "alerta": True, "fecha": "2025-07-18 14:00:00", "producto": "Estante B", "revisada": True},
        {"peso": 300, "alerta": True, "fecha": "2025-07-18 15:30:00", "producto": "Estante C", "revisada": False},
    ]

    # Filtrar alertas no revisadas para mostrar contador
    alertas_activas = sum(1 for r in registros if not r["revisada"])

    return render_template("alertas.html", registros=registros, alertas_activas=alertas_activas)


if __name__ == "__main__":
    app.run(debug=True)
