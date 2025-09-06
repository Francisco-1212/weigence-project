from flask import Flask, render_template, jsonify, request
import pyodbc
import sys
import os
from datetime import datetime, timedelta

# Agregar la carpeta raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

def conectar_bd():
    """Conecta a la base de datos SQL Server"""
    try:
        conexion_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost\SQLEXPRESS;"
            "DATABASE=weigence_db;"
            "Trusted_Connection=yes;"
            "Connection Timeout=30;"
        )
        
        conexion = pyodbc.connect(conexion_string)
        return conexion
        
    except Exception as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None

def obtener_resumen_dashboard():
    """Obtiene datos de resumen para el dashboard"""
    db = conectar_bd()
    if not db:
        return {"total_pesajes": 0, "total_alertas": 0, "ultima_fecha": "Sin datos"}
    
    try:
        cursor = db.cursor()
        
        # Total de pesajes
        cursor.execute("SELECT COUNT(*) FROM pesajes")
        total_pesajes = cursor.fetchone()[0]
        
        # Total de alertas activas
        cursor.execute("SELECT COUNT(*) FROM alertas WHERE estado = 'activa'")
        total_alertas = cursor.fetchone()[0]
        
        # Última fecha de pesaje
        cursor.execute("SELECT TOP 1 fecha FROM pesajes ORDER BY fecha DESC")
        result = cursor.fetchone()
        ultima_fecha = result[0].strftime('%Y-%m-%d %H:%M') if result else "Sin datos"
        
        cursor.close()
        db.close()
        
        return {
            "total_pesajes": total_pesajes,
            "total_alertas": total_alertas,
            "ultima_fecha": ultima_fecha
        }
        
    except Exception as e:
        print(f"❌ Error al obtener resumen: {e}")
        if db:
            db.close()
        return {"total_pesajes": 0, "total_alertas": 0, "ultima_fecha": "Error"}

def obtener_ultimos_pesajes(limit=10):
    """Obtiene los últimos pesajes de la base de datos"""
    db = conectar_bd()
    if not db:
        return []
    
    try:
        cursor = db.cursor()
        query = """
            SELECT TOP (?) 
                p.peso, 
                p.alerta, 
                p.fecha,
                e.codigo as estante_codigo,
                pr.nombre as producto_nombre
            FROM pesajes p
            LEFT JOIN estantes e ON p.estante_id = e.id
            LEFT JOIN productos pr ON p.producto_id = pr.id
            ORDER BY p.fecha DESC
        """
        cursor.execute(query, limit)
        datos = cursor.fetchall()
        
        # Convertir a lista de diccionarios para mejor manejo
        registros = []
        for row in datos:
            registros.append({
                'peso': float(row[0]),
                'alerta': bool(row[1]),
                'fecha': row[2].strftime('%Y-%m-%d %H:%M:%S'),
                'estante': row[3] if row[3] else 'N/A',
                'producto': row[4] if row[4] else 'N/A'
            })
        
        cursor.close()
        db.close()
        return registros
        
    except Exception as e:
        print(f"❌ Error al obtener pesajes: {e}")
        if db:
            db.close()
        return []

def obtener_alertas_activas():
    """Obtiene las alertas activas desde la vista"""
    db = conectar_bd()
    if not db:
        return []
    
    try:
        cursor = db.cursor()
        query = """
            SELECT 
                a.tipo_alerta,
                a.titulo,
                a.descripcion,
                a.gravedad,
                a.fecha_creacion,
                a.estado,
                e.codigo as estante,
                p.nombre as producto,
                pe.peso,
                pe.fecha as fecha_pesaje
            FROM alertas a
            JOIN pesajes pe ON a.pesaje_id = pe.id
            JOIN estantes e ON pe.estante_id = e.id
            LEFT JOIN productos p ON pe.producto_id = p.id
            WHERE a.estado = 'activa'
            ORDER BY a.fecha_creacion DESC
        """
        cursor.execute(query)
        datos = cursor.fetchall()
        
        alertas = []
        for row in datos:
            alertas.append({
                'tipo_alerta': row[0],
                'titulo': row[1],
                'descripcion': row[2],
                'gravedad': row[3],
                'fecha_creacion': row[4].strftime('%Y-%m-%d %H:%M:%S'),
                'estado': row[5],
                'estante': row[6],
                'producto': row[7] if row[7] else 'N/A',
                'peso': float(row[8]),
                'fecha': row[9].strftime('%Y-%m-%d %H:%M:%S'),
                'revisada': False  # Siempre False para alertas activas
            })
        
        cursor.close()
        db.close()
        return alertas
        
    except Exception as e:
        print(f"❌ Error al obtener alertas: {e}")
        if db:
            db.close()
        return []

def obtener_historial_completo():
    """Obtiene el historial completo de pesajes"""
    db = conectar_bd()
    if not db:
        return []
    
    try:
        cursor = db.cursor()
        query = """
            SELECT 
                p.peso,
                p.alerta,
                p.fecha,
                e.codigo as estante_codigo,
                pr.nombre as producto_nombre,
                COALESCE(pr.nombre, e.codigo, 'Estante ' + CAST(e.id AS VARCHAR)) as display_name
            FROM pesajes p
            LEFT JOIN estantes e ON p.estante_id = e.id
            LEFT JOIN productos pr ON p.producto_id = pr.id
            ORDER BY p.fecha DESC
        """
        cursor.execute(query)
        datos = cursor.fetchall()
        
        registros = []
        for row in datos:
            registros.append({
                'peso': float(row[0]),
                'alerta': bool(row[1]),
                'fecha': row[2].strftime('%Y-%m-%d %H:%M'),
                'producto': row[5]  # display_name
            })
        
        cursor.close()
        db.close()
        return registros
        
    except Exception as e:
        print(f"❌ Error al obtener historial: {e}")
        if db:
            db.close()
        return []

@app.route("/")
def index():
    """Página principal con dashboard"""
    # Obtener datos reales de la base de datos
    resumen = obtener_resumen_dashboard()
    registros = obtener_ultimos_pesajes(8)
    
    # Convertir registros al formato que espera el template
    registros_template = []
    for r in registros:
        registros_template.append((
            r['peso'], 
            r['alerta'], 
            r['fecha']
        ))

    return render_template("index.html", 
                           total_pesajes=resumen['total_pesajes'], 
                           total_alertas=resumen['total_alertas'], 
                           ultima_fecha=resumen['ultima_fecha'], 
                           registros=registros_template)

@app.route("/alertas")
def alertas():
    """Página de alertas activas"""
    registros = obtener_alertas_activas()
    alertas_activas = len([r for r in registros if not r['revisada']])

    return render_template("alertas.html", 
                           registros=registros, 
                           alertas_activas=alertas_activas)

@app.route("/historial")
def historial():
    """Página de historial completo"""
    registros = obtener_historial_completo()
    return render_template("historial.html", registros=registros)

@app.route("/api/datos-grafico")
def api_datos_grafico():
    """API para obtener datos del gráfico"""
    db = conectar_bd()
    if not db:
        return jsonify({"error": "No se puede conectar a la base de datos"})
    
    try:
        cursor = db.cursor()
        
        # Datos de pesajes por día (última semana)
        query_pesajes = """
            SELECT 
                CAST(fecha AS DATE) as dia,
                AVG(CAST(peso AS FLOAT)) as peso_promedio,
                COUNT(*) as cantidad_pesajes
            FROM pesajes 
            WHERE fecha >= DATEADD(DAY, -7, GETDATE())
            GROUP BY CAST(fecha AS DATE)
            ORDER BY dia
        """
        cursor.execute(query_pesajes)
        datos_pesajes = cursor.fetchall()
        
        # Datos de alertas por día (última semana)
        query_alertas = """
            SELECT 
                CAST(a.fecha_creacion AS DATE) as dia,
                COUNT(*) as cantidad_alertas
            FROM alertas a
            WHERE a.fecha_creacion >= DATEADD(DAY, -7, GETDATE())
            GROUP BY CAST(a.fecha_creacion AS DATE)
            ORDER BY dia
        """
        cursor.execute(query_alertas)
        datos_alertas = cursor.fetchall()
        
        cursor.close()
        db.close()
        
        # Formatear datos para Chart.js
        labels = []
        pesajes = []
        alertas = []
        
        # Crear diccionarios para facilitar el procesamiento
        dict_pesajes = {row[0]: row[1] for row in datos_pesajes}
        dict_alertas = {row[0]: row[1] for row in datos_alertas}
        
        # Generar últimos 7 días
        for i in range(6, -1, -1):
            fecha = datetime.now().date() - timedelta(days=i)
            labels.append(fecha.strftime('%a'))  # Lun, Mar, etc.
            pesajes.append(round(dict_pesajes.get(fecha, 0), 1))
            alertas.append(dict_alertas.get(fecha, 0))
        
        return jsonify({
            "labels": labels,
            "pesajes": pesajes,
            "alertas": alertas
        })
        
    except Exception as e:
        print(f"❌ Error al obtener datos del gráfico: {e}")
        return jsonify({"error": str(e)})

@app.route("/api/marcar-alerta-revisada/<int:alerta_id>", methods=["POST"])
def marcar_alerta_revisada(alerta_id):
    """API para marcar una alerta como revisada"""
    db = conectar_bd()
    if not db:
        return jsonify({"error": "No se puede conectar a la base de datos"}), 500
    
    try:
        cursor = db.cursor()
        query = """
            UPDATE alertas 
            SET estado = 'revisada', 
                fecha_revision = GETDATE(),
                usuario_revision = 'Sistema Web'
            WHERE Sid = ?
        """
        cursor.execute(query, alerta_id)
        db.commit()
        
        cursor.close()
        db.close()
        
        return jsonify({"success": True, "message": "Alerta marcada como revisada"})
        
    except Exception as e:
        print(f"❌ Error al marcar alerta: {e}")
        if db:
            db.close()
        return jsonify({"error": str(e)}), 500

@app.route("/test-conexion")
def test_conexion():
    """Endpoint para probar la conexión a la base de datos"""
    db = conectar_bd()
    if db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT COUNT(*) FROM pesajes")
            count = cursor.fetchone()[0]
            cursor.close()
            db.close()
            return f"✅ Conexión exitosa. Total pesajes: {count}"
        except Exception as e:
            if db:
                db.close()
            return f"❌ Error en consulta: {e}"
    else:
        return "❌ No se pudo conectar a la base de datos"

if __name__ == "__main__":
    print("🚀 Iniciando aplicación Flask con SQL Server...")
    print("🔗 Probando conexión a la base de datos...")
    
    # Probar conexión al inicio
    if conectar_bd():
        print("✅ Conexión a SQL Server exitosa")
    else:
        print("❌ Problema con la conexión a SQL Server")
        print("📝 Verifica que SQL Server esté ejecutándose y la base de datos 'weigence' exista")
    
    app.run(debug=True, host='0.0.0.0', port=5000)