from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from livereload import Server
from functools import wraps
from sys import path
import os
from functools import wraps

# ruta del proyecto para importar conexion_supabase
path.append(r"e:\Github\weigence-project\weigence")
from conexion_bd.conexion_supabase import supabase

app = Flask(__name__)
app.secret_key = 'weigence_secret_key_2024'
app.config['DEBUG'] = True

# Evitar caché en templates
app.config['TEMPLATES_AUTO_RELOAD'] = True


def requiere_login(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_logueado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorador

# --- LOGIN ---
@app.route("/", methods=["GET", "POST"])
def login():
    # Limpiar sesión al entrar por primera vez
    session.clear()

    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        password_input = request.form.get("password")

        if not usuario_input or not password_input:
            flash("Por favor completa todos los campos", "error")
            return render_template("login.html")

        usuarios = supabase.table("usuarios").select("*").execute().data

        usuario_encontrado = next(
            (u for u in usuarios if u.get("nombre") == usuario_input 
             or u.get("correo") == usuario_input 
             or u.get("rut_usuario") == usuario_input),
            None
        )

        if usuario_encontrado:
            if usuario_encontrado.get("Contraseña") == password_input:
                session["usuario_logueado"] = True
                session["usuario_nombre"] = usuario_encontrado.get("nombre")
                session["usuario_rol"] = usuario_encontrado.get("rol")
                session["usuario_id"] = usuario_encontrado.get("rut_usuario")
                return redirect(url_for("dashboard"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("login.html")



# --- PÁGINA PRINCIPAL / DASHBOARD ---
@app.route("/dashboard")
@requiere_login
def dashboard():
    # --- Obtener datos de Supabase ---
    productos = supabase.table("productos").select("*").execute().data
    pesajes = supabase.table("pesajes").select("*").execute().data
    usuarios = supabase.table("usuarios").select("*").execute().data
    estantes = supabase.table("estantes").select("*").execute().data
    historial = supabase.table("historial").select("*").execute().data
    alertas_db = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data

    # --- Obtener ventas y detalle de ventas ---
    ventas_data = supabase.table("ventas").select("*").execute().data
    detalle_ventas = supabase.table("detalle_ventas").select("*").execute().data

    # --- Calcular tarjetas resumen ---
    valor_total_inventario = sum(p["stock"] * p["precio_unitario"] for p in productos)
    articulos_vendidos = sum(dv["cantidad"] for dv in detalle_ventas)
    ventas_totales = sum(dv.get("subtotal", dv["cantidad"]*dv["precio_unitario"]) for dv in detalle_ventas)



    # Producto más vendido
    from collections import Counter
    productos_vendidos = Counter()
    for dv in detalle_ventas:
        productos_vendidos[dv["idproducto"]] += dv["cantidad"]
    if productos_vendidos:
        id_mas_vendido = productos_vendidos.most_common(1)[0][0]
        producto_mas_vendido = next((p["nombre"] for p in productos if p["idproducto"] == id_mas_vendido), "Sin datos")
    else:
        producto_mas_vendido = "Sin datos"

    # Productos agotados
    productos_agotados = len([p for p in productos if p["stock"] == 0])

    # --- Generar alertas dinámicas ---
    alertas_dinamicas = []

    # 1. Bajo stock
    for p in productos:
        if p["stock"] <= 5:
            alertas_dinamicas.append({
                "titulo": "Bajo stock",
                "descripcion": f"Quedan solo {p['stock']} unidades de {p['nombre']}",
                "icono": "priority_high",
                "tipo_color": "danger"
            })

    # 2. Peso crítico
    for pesaje in pesajes:
        producto = next((prod for prod in productos if prod["idproducto"] == pesaje["idproducto"]), None)
        if producto:
            if isinstance(pesaje.get("fecha_pesaje"), str):
                pesaje["fecha_pesaje"] = datetime.fromisoformat(pesaje["fecha_pesaje"])
            if pesaje["peso_unitario"] < producto["peso"] * 0.5 or pesaje["peso_unitario"] > producto["peso"] * 1.5:
                alertas_dinamicas.append({
                    "titulo": "Peso crítico",
                    "descripcion": f"El producto {producto['nombre']} tiene un pesaje anómalo: {pesaje['peso_unitario']}kg",
                    "icono": "error",
                    "tipo_color": "danger"
                })

    # 3. Producto inactivo (últimos 7 días sin pesaje)
    limite = datetime.now() - timedelta(days=7)
    for p in productos:
        ult_pesaje = [ps for ps in pesajes if ps["idproducto"] == p["idproducto"]]
        for ps in ult_pesaje:
            if isinstance(ps.get("fecha_pesaje"), str):
                ps["fecha_pesaje"] = datetime.fromisoformat(ps["fecha_pesaje"])
        if not ult_pesaje or max(ps["fecha_pesaje"] for ps in ult_pesaje) < limite:
            alertas_dinamicas.append({
                "titulo": "Producto inactivo",
                "descripcion": f"No se ha pesado {p['nombre']} en la última semana",
                "icono": "warning",
                "tipo_color": "warning"
            })

    # --- Combinar alertas ---
    alertas_completas = alertas_db + alertas_dinamicas
    alertas_criticas = [a for a in alertas_completas if a.get("tipo_color") in ["danger", "rojo"]][-3:]
    alertas_criticas = alertas_criticas[-3:]  # Últimas 3 críticas

    # --- Notificaciones recientes (para campana) ---
    notificaciones = alertas_completas[:5]

    # --- Renderizar plantilla ---
    return render_template(
        "pagina/index.html",
        productos=productos,
        pesajes=pesajes,
        usuarios=usuarios,
        estantes=estantes,
        historial=historial,
        notificaciones=notificaciones,
        alertas_criticas=alertas_criticas,
        valor_total_inventario=valor_total_inventario,
        articulos_vendidos=articulos_vendidos,
        producto_mas_vendido=producto_mas_vendido,
        productos_agotados=productos_agotados,
        ventas_totales=ventas_totales
    )


# --- INVENTARIO ---
@app.route("/inventario")
@requiere_login
def inventario():
    productos = supabase.table("productos").select("*").execute().data
    total_productos = len(productos)
    total_stock = sum(p.get("stock", 0) for p in productos)
    total_valor = sum(p.get("stock", 0) * p.get("precio", 0) for p in productos)
    productos_baja_rotacion = len([p for p in productos if p.get("stock", 0) <= 5])

    estadisticas = {
        "total_productos": total_productos,
        "total_stock": total_stock,
        "total_valor": total_valor,
        "productos_baja_rotacion": productos_baja_rotacion
    }

    for producto in productos:
        stock = producto.get("stock", 0)
        if stock <= 5:
            producto["status"] = "Low Stock"
            producto["status_class"] = "low-stock"
        else:
            producto["status"] = "Normal"
            producto["status_class"] = "normal"

    return render_template("pagina/inventario.html", productos=productos, estadisticas=estadisticas)


# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Página de ventas ---

@app.route("/ventas")
def ventas():
    ventas = supabase.table("ventas").select("*").execute().data
    detalle_ventas = supabase.table("detalle_ventas").select("*").execute().data
    productos = supabase.table("productos").select("*").execute().data

    productos_dict = {p["idproducto"]: p["nombre"] for p in productos}

    total_ventas = sum(v["total"] for v in ventas) if ventas else 0
    promedio_ventas = total_ventas / len(ventas) if ventas else 0
    num_transacciones = len(ventas)

    productos_cant = {}
    for det in detalle_ventas:
        productos_cant[det["idproducto"]] = productos_cant.get(det["idproducto"], 0) + det["cantidad"]
    top_producto = max(productos_cant.items(), key=lambda x: x[1]) if productos_cant else None
    nombre_top = productos_dict.get(top_producto[0], f"ID {top_producto[0]}") if top_producto else "-"
    top_producto_str = f"{nombre_top} ({top_producto[1]})" if top_producto else "-"

    # --- Datos últimos 30 días ---
    hoy = datetime.now().date()
    fecha_inicio = hoy - timedelta(days=29)
    labels = [(fecha_inicio + timedelta(days=i)).strftime("%d/%m") for i in range(30)]
    data_ventas_diarias = []
    for i in range(30):
        dia = fecha_inicio + timedelta(days=i)
        total_dia = sum(
            v["total"] for v in ventas
            if datetime.fromisoformat(v["fecha_venta"]).date() == dia
        )
        data_ventas_diarias.append(float(total_dia))

    # --- Cálculo porcentaje cambio ---
    total_ayer = data_ventas_diarias[-2] if len(data_ventas_diarias) > 1 else 0
    total_hoy = data_ventas_diarias[-1] if data_ventas_diarias else 0
    ventas_cambio = ((total_hoy - total_ayer) / total_ayer * 100) if total_ayer else 0
    total_ventas_class = "text-green-500" if ventas_cambio >= 0 else "text-red-500"
    ventas_cambio_icon = "arrow_upward" if ventas_cambio >= 0 else "arrow_downward"

    return render_template(
        "pagina/ventas.html",
        ventas=ventas,
        detalle_ventas=detalle_ventas,
        productos_dict=productos_dict,
        total_ventas_str=f"{total_ventas:,.0f}".replace(",", "."),
        promedio_ventas_str=f"{promedio_ventas:,.2f}".replace(",", "."),
        num_transacciones=num_transacciones,
        top_producto_str=top_producto_str,
        labels=labels,
        data_ventas=data_ventas_diarias,
        ventas_cambio=f"{ventas_cambio:.2f}",
        ventas_cambio_icon=ventas_cambio_icon,
        total_ventas_class=total_ventas_class
    )

@app.route("/api/tendencia_ventas")
def api_tendencia_ventas():
    hoy = datetime.now().date()
    fechas = [hoy - timedelta(days=i) for i in reversed(range(30))]
    
    # Diccionario fecha -> total ventas
    tendencia = {f: 0 for f in fechas}

    ventas = supabase.table("ventas").select("fecha_venta, total").execute().data
    for v in ventas:
        fecha = datetime.fromisoformat(v["fecha_venta"]).date()
        if fecha in tendencia:
            tendencia[fecha] += float(v["total"])

    # Convertir a listas para JS
    labels = [f.strftime("%d/%m") for f in fechas]
    data_ventas = [tendencia[f] for f in fechas]

    return jsonify({
        "labels": labels,
        "data_ventas": data_ventas
    })




#--- Ruta Alertas ---
@app.route("/alertas")
def alertas():
    # Obtener datos de las tablas necesarias
    alertas = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data
    productos = supabase.table("productos").select("idproducto, nombre").execute().data
    usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data

    # Crear diccionarios para búsqueda rápida
    productos_dict = {p["idproducto"]: p["nombre"] for p in productos}
    usuarios_dict = {u["rut_usuario"]: u["nombre"] for u in usuarios}

    # Enriquecer alertas con información adicional
    for alerta in alertas:
        alerta["nombre_producto"] = productos_dict.get(alerta.get("idproducto"), "Sin producto")
        alerta["nombre_usuario"] = usuarios_dict.get(alerta.get("idusuario"), "Sistema")
        # Formatear fecha
        if alerta.get("fecha_creacion"):
            fecha = datetime.fromisoformat(str(alerta["fecha_creacion"]).replace('Z', '+00:00'))
            alerta["fecha_formateada"] = fecha.strftime("%d/%m/%Y %H:%M")
        else:
            alerta["fecha_formateada"] = "-"

    # Estadísticas básicas
    total_alertas = len(alertas)
    alertas_pendientes = len([a for a in alertas if a.get("estado") == "pendiente"])
    alertas_resueltas = len([a for a in alertas if a.get("estado") == "resuelto"])

    return render_template(
        "pagina/alertas.html",
        alertas=alertas,
        total_alertas=total_alertas,
        alertas_pendientes=alertas_pendientes,
        alertas_resueltas=alertas_resueltas
    )
@app.context_processor
def agregar_alertas_y_notificaciones():
    productos = supabase.table("productos").select("*").execute().data
    pesajes = supabase.table("pesajes").select("*").execute().data
    alertas_db = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data

    # --- Generar alertas dinámicas ---
    alertas_dinamicas = []

    for p in productos:
        if p["stock"] <= 5:
            alertas_dinamicas.append({
                "titulo": "Bajo stock",
                "descripcion": f"Quedan solo {p['stock']} unidades de {p['nombre']}",
                "icono": "priority_high",
                "tipo_color": "danger"
            })

    alertas_completas = alertas_db + alertas_dinamicas
    alertas_criticas = [a for a in alertas_completas if a.get("tipo_color") in ["danger", "rojo"]]
    notificaciones = alertas_completas[:5]

    return dict(
        notificaciones=notificaciones,
        alertas_criticas=alertas_criticas
    )


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


