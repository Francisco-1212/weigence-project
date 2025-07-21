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
    # Datos de ejemplo
    total_pesajes = 124
    total_alertas = 7
    ultima_fecha = "2025-07-18 17:30"

    # Datos para la tabla (ejemplo)
    datos = [
        (1500, True, "2025-07-18 16:00"),
        (1200, False, "2025-07-18 15:30"),  
        (1300, True, "2025-07-18 15:00"),
        (1400, False, "2025-07-18 14:30"),
        (1350, True, "2025-07-18 14:00"),
        (1450, False, "2025-07-18 13:30"),
        (1550, True, "2025-07-18 13:00"),
        (1600, False, "2025-07-18 12:30"),               


    ]

    return render_template("index.html", 
                           total_pesajes=total_pesajes, 
                           total_alertas=total_alertas, 
                           ultima_fecha=ultima_fecha, 
                           registros=datos)

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

@app.route("/historial")
def historial():
    # Datos simulados
    registros = [
        {"producto": "Estante A", "peso": 1000, "alerta": False, "fecha": "2025-07-18 12:00"},
        {"producto": "Estante B", "peso": 950, "alerta": True, "fecha": "2025-07-18 13:00"},
        {"producto": "Estante C", "peso": 980, "alerta": False, "fecha": "2025-07-18 14:00"},
        {"producto": "Estante A", "peso": 920, "alerta": True, "fecha": "2025-07-18 15:00"},
        {"producto": "Estante B", "peso": 1100, "alerta": False, "fecha": "2025-07-08 16:00"},
        {"producto": "Estante C", "peso": 1050, "alerta": True, "fecha": "2025-07-07 17:00"},
        {"producto": "Estante A", "peso": 1150, "alerta": False, "fecha": "2025-07-19 18:00"},
        {"producto": "Estante B", "peso": 1200, "alerta": True, "fecha": "2025-07-19 19:00"},
    ]
    return render_template("historial.html", registros=registros)


if __name__ == "__main__":
    app.run(debug=True)
