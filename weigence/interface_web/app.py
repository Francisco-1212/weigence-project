from flask import Flask, render_template, jsonify
from livereload import Server
from sys import path
import os

# Agregar ruta del proyecto para importar conexion_supabase
path.append(r"e:\Github\weigence-project\weigence")
from conexion_bd.conexion_supabase import supabase

app = Flask(__name__)

# Evitar caché en templates
app.config['TEMPLATES_AUTO_RELOAD'] = True

# --- RUTAS ---
@app.route("/")
def index():
    # Traer datos desde Supabase
    productos = supabase.table("productos").select("*").execute().data
    pesajes = supabase.table("pesajes").select("*").execute().data
    usuarios = supabase.table("usuarios").select("*").execute().data
    estantes = supabase.table("estantes").select("*").execute().data
    historial = supabase.table("historial").select("*").execute().data

    # Generar alertas dinámicas
    alertas = []

    # 1. Bajo stock (stock <= 5)
    for p in productos:
        if p["stock"] <= 5:
            alertas.append({
                "titulo": "Bajo stock",
                "descripcion": f"Quedan solo {p['stock']} unidades de {p['nombre']}",
                "icono": "priority_high",
                "tipo_color": "danger"
            })

    # 2. Pesaje crítico (peso_unitario fuera de rango esperado)
    for pesaje in pesajes:
        producto = next((prod for prod in productos if prod["idproducto"] == pesaje["idproducto"]), None)
        if producto and (pesaje["peso_unitario"] < producto["peso"]*0.5 or pesaje["peso_unitario"] > producto["peso"]*1.5):
            alertas.append({
                "titulo": "Peso crítico",
                "descripcion": f"El producto {producto['nombre']} tiene un pesaje anómalo: {pesaje['peso_unitario']}kg",
                "icono": "error",
                "tipo_color": "danger"
            })

    # 3. Producto inactivo (sin pesajes últimos 7 días)
    import datetime
    limite = datetime.datetime.now() - datetime.timedelta(days=7)
    for p in productos:
        ult_pesaje = [ps for ps in pesajes if ps["idproducto"] == p["idproducto"]]
        if not ult_pesaje or max(ps["fecha_pesaje"] for ps in ult_pesaje) < limite:
            alertas.append({
                "titulo": "Producto inactivo",
                "descripcion": f"No se ha pesado {p['nombre']} en la última semana",
                "icono": "warning",
                "tipo_color": "warning"
            })
    # Limitar a 5 alertas
    alertascriticas = alertas[-3:]

    # Renderizar template con datos
    return render_template(
        "pagina/index.html",
        productos=productos,
        pesajes=pesajes,
        usuarios=usuarios,
        estantes=estantes,
        historial=historial,
        alertas=alertascriticas
    )


#--- Ruta Inventario ---
@app.route("/inventario")
def inventario():
    productos = supabase.table("productos").select("*").execute().data
    return render_template("pagina/inventario.html", productos=productos)

#--- Ruta Ventas ---
@app.route("/ventas")
def ventas():
    return render_template("pagina/ventas.html")

@app.route("/alertas")
def alertas():
    alertas = [
        {"icono": "error", "descripcion": "Sensor 1 sin conexión", "tipo_color": "danger"},
        {"icono": "warning", "descripcion": "Peso bajo en Estante A", "tipo_color": "warning"},
        {"icono": "info", "descripcion": "Actualización completada", "tipo_color": "info"},
    ]
    return render_template("pagina/alertas.html", alertas=alertas)

# --- MAIN ---
if __name__ == "__main__":
    server = Server(app.wsgi_app)

    # Observar todos los archivos HTML, CSS, JS y Python
    server.watch("templates/**/*.html")
    server.watch("static/**/*.css")
    server.watch("static/**/*.js")
    server.watch("**/*.py")  # Observa cambios en todos los .py del proyecto

    # Levantar servidor
    server.serve(port=5000, host="127.0.0.1", debug=True)


