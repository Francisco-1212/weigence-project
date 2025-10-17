from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from livereload import Server
from functools import wraps
from sys import path
import os
import json
from pathlib import Path

# ruta del proyecto para importar conexion_supabase
path.append(r"e:\Github\weigence-project\weigence")
from api.conexion_supabase import supabase

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
    session.clear()
    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        password_input = request.form.get("password")
        remember = request.form.get("remember")  # Opcional para "recordarme"

        if not usuario_input or not password_input:
            flash("Por favor completa todos los campos", "error")
            return render_template("login.html")

        # Aquí va la lógica de supabase o tu base de datos:
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
                session["usuario_correo"] = usuario_encontrado.get("correo")
                # Aquí puedes manejar el "remember" para sesiones más largas
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
    productos = supabase.table("productos").select("*").execute().data
    pesajes = supabase.table("pesajes").select("*").execute().data
    usuarios = supabase.table("usuarios").select("*").execute().data
    estantes = supabase.table("estantes").select("*").execute().data
    historial = supabase.table("historial").select("*").execute().data
    alertas_db = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data

    ventas_data = supabase.table("ventas").select("*").execute().data
    detalle_ventas = supabase.table("detalle_ventas").select("*").execute().data

    valor_total_inventario = sum(p["stock"] * p["precio_unitario"] for p in productos)
    articulos_vendidos = sum(dv["cantidad"] for dv in detalle_ventas)
    ventas_totales = sum(dv.get("subtotal", dv["cantidad"]*dv["precio_unitario"]) for dv in detalle_ventas)

    productos_vendidos = Counter()
    for dv in detalle_ventas:
        productos_vendidos[dv["idproducto"]] += dv["cantidad"]
    if productos_vendidos:
        id_mas_vendido = productos_vendidos.most_common(1)[0][0]
        producto_mas_vendido = next((p["nombre"] for p in productos if p["idproducto"] == id_mas_vendido), "Sin datos")
    else:
        producto_mas_vendido = "Sin datos"
    productos_agotados = len([p for p in productos if p["stock"] == 0])

    # ---------- REGISTRAR ALERTAS ÚNICAS EN BASE ----------
    for p in productos:
        if p["stock"] == 0:
            # Solo alerta de stock agotado
            existe = supabase.table("alertas").select("*") \
                .eq("idproducto", p["idproducto"]) \
                .eq("titulo", "Stock agotado") \
                .eq("estado", "pendiente").execute().data
            if not existe:
                supabase.table("alertas").insert({
                    "titulo": "Stock agotado",
                    "descripcion": f"El producto {p['nombre']} está agotado",
                    "icono": "❌",
                    "tipo_color": "rojo",
                    "fecha_creacion": datetime.now().isoformat(),  
                    "estado": "pendiente",
                    "idproducto": p["idproducto"]
                }).execute()
        elif p["stock"] <= 5:
            # Solo bajo stock si NO es 0
            existe = supabase.table("alertas").select("*") \
                .eq("idproducto", p["idproducto"]) \
                .eq("titulo", "Bajo stock") \
                .eq("estado", "pendiente").execute().data
            if not existe:
                supabase.table("alertas").insert({
                    "titulo": "Bajo stock",
                    "descripcion": f"Quedan solo {p['stock']} unidades de {p['nombre']}",
                    "icono": "❌",
                    "tipo_color": "rojo",
                    "fecha_creacion": datetime.now().isoformat(),  
                    "estado": "pendiente",
                    "idproducto": p["idproducto"]
                }).execute()


    # Peso crítico y variación brusca
    for pesaje in pesajes:
        producto = next((prod for prod in productos if prod["idproducto"] == pesaje["idproducto"]), None)
        if producto:
            if isinstance(pesaje.get("fecha_pesaje"), str):
                pesaje["fecha_pesaje"] = datetime.fromisoformat(pesaje["fecha_pesaje"])
            peso_val = pesaje["peso_unitario"]
            # Peso crítico
            if peso_val < producto["peso"] * 0.5 or peso_val > producto["peso"] * 1.5:
                existe = supabase.table("alertas").select("*") \
                    .eq("idproducto", producto["idproducto"]) \
                    .eq("titulo", "Peso crítico") \
                    .eq("estado", "pendiente").execute().data
                if not existe:
                    supabase.table("alertas").insert({
                        "titulo": "Peso crítico",
                        "descripcion": f"El producto {producto['nombre']} tiene pesaje anómalo: {peso_val}kg",
                        "icono": "❌",
                        "tipo_color": "rojo",
                        "fecha_creacion": datetime.now().isoformat(), 
                        "estado": "pendiente",
                        "idproducto": producto["idproducto"]
                    }).execute()
            # Variación brusca (ajusta según regla real de tu operación)
            if abs(peso_val - producto["peso"]) > producto["peso"] * 0.5:
                existe = supabase.table("alertas").select("*") \
                    .eq("idproducto", producto["idproducto"]) \
                    .eq("titulo", "Variación brusca de peso") \
                    .eq("estado", "pendiente").execute().data
                if not existe:
                    supabase.table("alertas").insert({
                        "titulo": "Variación brusca de peso",
                        "descripcion": f"Cambio brusco en el pesaje del producto {producto['nombre']}.",
                        "icono": "⚠️",
                        "tipo_color": "amarillo",
                        "fecha_creacion": datetime.now().isoformat(), 
                        "estado": "pendiente",
                        "idproducto": producto["idproducto"]
                    }).execute()
    # Producto sin registrar
    for pesaje in pesajes:
        if pesaje["idproducto"] is None or pesaje["idproducto"] not in [p["idproducto"] for p in productos]:
            existe = supabase.table("alertas").select("*") \
                .eq("titulo", "Producto sin registrar") \
                .eq("estado", "pendiente").execute().data
            if not existe:
                supabase.table("alertas").insert({
                    "titulo": "Producto sin registrar",
                    "descripcion": "Se detectó un pesaje o ingreso de un producto no registrado.",
                    "icono": "❌",
                    "tipo_color": "rojo",
                    "fecha_creacion": datetime.now().isoformat(), 
                    "estado": "pendiente",
                    "idproducto": pesaje.get("idproducto")
                }).execute()

    # Verificación manual requerida (ejemplo, personaliza la lógica/flag)
    # if alguna_condicion_de_verificacion:
    #     supabase.table("alertas").insert({
    #         "titulo": "Verificación manual requerida",
    #         "descripcion": "Se requiere verificación física para este producto/evento.",
    #         "icono": "⚠️",
    #         "tipo_color": "amarillo",
    #         "fecha_creacion": datetime.now().isoformat(),
    #         "estado": "pendiente",
    #         "idproducto": idproducto_asociado,
    #     }).execute()

    # Cuando el producto vuelve a estado normal, resuelve la alerta
    # if producto_normalizado:
    #     supabase.table("alertas").update({"estado": "resuelto"}) \
    #         .eq("idproducto", idproducto) \
    #         .eq("titulo", "ALERTA A RESOLVER").execute()
    #     supabase.table("alertas").insert({
    #         "titulo": "Producto correcto",
    #         "descripcion": "El producto ha vuelto a valores normales.",
    #         "icono": "✅",
    #         "tipo_color": "verde",
    #         "fecha_creacion": datetime.now().isoformat(),
    #         "estado": "resuelto",
    #         "idproducto": idproducto,
    #     }).execute()

    # Producto vencido (solo si tienes campo "fecha_vencimiento" en tu tabla)
    # for p in productos:
    #     if "fecha_vencimiento" in p:
    #         fecha_venc = datetime.fromisoformat(p["fecha_vencimiento"])
    #         if fecha_venc < datetime.now():
    #             existe = supabase.table("alertas").select("*") \
    #                 .eq("idproducto", p["idproducto"]) \
    #                 .eq("titulo", "Producto vencido") \
    #                 .eq("estado", "pendiente").execute().data
    #             if not existe:
    #                 supabase.table("alertas").insert({
    #                     "titulo": "Producto vencido",
    #                     "descripcion": f"El producto {p['nombre']} ha vencido.",
    #                     "icono": "❌",
    #                     "tipo_color": "rojo",
    #                     "fecha_creacion": fecha_venc.isoformat(),
    #                     "estado": "pendiente",
    #                     "idproducto": p["idproducto"]
    #                 }).execute()

    # --- Solo AVISO dinámico, NO en BD ---
    productos_inactivos = []
    limite = datetime.now() - timedelta(days=7)
    for p in productos:
        ult_pesaje = [ps for ps in pesajes if ps["idproducto"] == p["idproducto"]]
        for ps in ult_pesaje:
            if isinstance(ps.get("fecha_pesaje"), str):
                ps["fecha_pesaje"] = datetime.fromisoformat(ps["fecha_pesaje"])
        if not ult_pesaje or max(ps["fecha_pesaje"] for ps in ult_pesaje) < limite:
            productos_inactivos.append(p["nombre"])
    alertas_dinamicas = []
    if productos_inactivos:
        listado_corto = ", ".join(productos_inactivos[:3])
        extra = f" y {len(productos_inactivos)-3} más" if len(productos_inactivos) > 3 else ""
        alertas_dinamicas.append({
            "titulo": "Productos inactivos (solo aviso)",
            "descripcion": f"No se ha pesado en la última semana: {listado_corto}{extra}.",
            "icono": "⚠️",
            "tipo_color": "amarillo",
            "fecha_creacion": datetime.now().isoformat(),
            "solo_ui": True
        })

    # ------------------- Render tradicional -----------------------
    alertas_db = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data
    alertas_completas = alertas_db + alertas_dinamicas
    alertas_criticas = [a for a in alertas_completas if a.get("tipo_color") in ["danger", "rojo"] and a.get("estado") == "pendiente"][-3:]
    notificaciones = [a for a in alertas_db if a.get("estado") == "pendiente"]
    notificaciones_agrupadas = agrupar_notificaciones_por_fecha(notificaciones)

    return render_template(
        "pagina/index.html",
        productos=productos,
        pesajes=pesajes,
        usuarios=usuarios,
        estantes=estantes,
        historial=historial,
        notificaciones=notificaciones,
        notificaciones_agrupadas=notificaciones_agrupadas,
        alertas_criticas=alertas_criticas,
        valor_total_inventario=valor_total_inventario,
        articulos_vendidos=articulos_vendidos,
        producto_mas_vendido=producto_mas_vendido,
        productos_agotados=productos_agotados,
        ventas_totales=ventas_totales
    )

@app.route('/api/dashboard_filtrado')
@requiere_login
def api_dashboard_filtrado():
    rango = request.args.get('rango', 'hoy')
    mes = request.args.get('mes', type=int)
    year = request.args.get('year', type=int)
    now = datetime.now()

    if rango == 'hoy':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif rango == 'semana':
        start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif rango == 'mes' and mes and year:
        start = datetime(year, mes, 1)
        if mes == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, mes + 1, 1)
        now = end - timedelta(seconds=1)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Obtener ventas en rango seleccionado
    ventas = supabase.table("ventas").select("*") \
        .gte("fecha_venta", start.isoformat()) \
        .lte("fecha_venta", now.isoformat()) \
        .execute().data or []

    ids_ventas = [v["idventa"] for v in ventas]
    detalles = supabase.table("detalle_ventas").select("*") \
        .in_("idventa", ids_ventas) \
        .execute().data or []

    productos_info = supabase.table("productos").select("idproducto,nombre").execute().data or []

    # Inicializar estructura con todos los productos (incluso sin ventas)
    ventas_por_producto = {
        p["idproducto"]: {"nombre": p["nombre"], "ventas": 0.0, "cantidad": 0}
        for p in productos_info
    }

    articulos_vendidos = 0
    for dv in detalles:
        idprod = dv["idproducto"]
        if idprod in ventas_por_producto:
            cantidad = dv.get("cantidad", 0) or 0
            precio = dv.get("precio_unitario", 0) or 0
            ventas_por_producto[idprod]["ventas"] += cantidad * precio
            ventas_por_producto[idprod]["cantidad"] += cantidad
            articulos_vendidos += cantidad

    # Convertir a lista y ordenar por ventas para el gráfico, y por cantidad para top/low
    productos_arr = list(ventas_por_producto.values())
    # Para el gráfico, ordenamos por ventas
    productos_por_ventas = sorted(productos_arr, key=lambda x: x["ventas"], reverse=True)

    # Para top/low utilizamos la métrica cantidad (artículos vendidos)
    productos_por_cantidad_desc = sorted(productos_arr, key=lambda x: x["cantidad"], reverse=True)
    productos_por_cantidad_asc = sorted(productos_arr, key=lambda x: x["cantidad"])  # incluye ceros

    producto_mas_vendido = productos_por_cantidad_desc[0]["nombre"] if productos_por_cantidad_desc else "Sin datos"
    ventas_totales = sum(p["ventas"] for p in productos_arr)

    grafico = {
        "productos": productos_por_ventas[:6],
        "labels": [p["nombre"] for p in productos_por_ventas[:6]],
        "data": [p["ventas"] for p in productos_por_ventas[:6]],
    }

    # Preparar top 5 y low 5
    productos_top = [
        {"nombre": p["nombre"], "cantidad": int(p.get("cantidad", 0)), "ventas": round(float(p.get("ventas", 0)), 0)}
        for p in productos_por_cantidad_desc[:5]
    ]
    productos_low = [
        {"nombre": p["nombre"], "cantidad": int(p.get("cantidad", 0)), "ventas": round(float(p.get("ventas", 0)), 0)}
        for p in productos_por_cantidad_asc[:5]
    ]

    crecimiento = 0  # Placeholder para cálculo de % cambio si lo deseas

    return jsonify({
        "grafico": grafico,
        "ventas_totales": int(ventas_totales),
        "ventas_cambio": crecimiento,
        "articulos_vendidos": articulos_vendidos,
        "producto_mas_vendido": producto_mas_vendido,
        "productos_top": productos_top,
        "productos_low": productos_low
    })



def check_sistema_integral():
    estados = []

    try:
        res = supabase.table("productos").select("idproducto").limit(1).execute()

        # Cambia aquí:
        # Si ocurre excepción ya está en except
        # Para el SDK de supabase más usado en Python, no hay propiedad .error, solo .data y .status_code
        estados.append("db_ok")
    except Exception as ex:
        print("Exception en conexión Supabase:", ex)
        estados.append("db_fail")

    # Checks opcionales de otros microservicios:
    # ...

    alertas_pendientes = supabase.table("alertas").select("*").eq("estado", "pendiente").execute().data or []
    # NOTA: alertas de productos NO cuentan como "fallas del sistema".
    # En su lugar, detectamos errores de sistema registrados en el log de errores.

    # archivo para registrar errores del sistema (ligero, en filesystem)
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    errors_file = data_dir / 'errors_log.json'

    def read_error_log():
        try:
            if not errors_file.exists():
                return []
            with open(errors_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print('Error leyendo error log:', e)
            return []

    # Obtener errores recientes del log (si existen)
    errores = read_error_log()

    # Determina estado general:
    # - Si falla la DB -> offline
    # - Si hay errores de sistema recientes -> warning
    # - Si todo ok -> online
    if "db_fail" in estados:
        estado_general = "offline"
    elif errores:
        estado_general = "warning"
    else:
        estado_general = "online"

    # Construir lista de detalles legibles para el frontend
    detalles = []
    if "db_fail" in estados:
        detalles.append("No se pudo conectar a la base de datos")

    # Añadir errores (máximo 10) al detalle
    try:
        for e in errores[:10]:
            # cada entrada del log debe tener 'timestamp' y 'message'
            ts = e.get('timestamp') or e.get('time') or ''
            msg = e.get('message') or e.get('msg') or e.get('detail') or str(e)
            detalles.append(f"{ts} - {msg}")
    except Exception:
        pass

    return estado_general, detalles

last_manual_update = datetime.now()


@app.route('/api/refresh', methods=['POST'])
@requiere_login
def api_refresh():
    global last_manual_update
    last_manual_update = datetime.now()
    return jsonify({"success": True})


# Endpoint: movimientos / historial (movements)
@app.route('/api/history')
@requiere_login
def api_history():
    try:
        # Obtener historial desde la tabla 'historial' en supabase
        hist = supabase.table('historial').select('*').order('fecha_cambio', desc=True).limit(200).execute().data or []
        # Normalizar formato simple
        out = []
        for h in hist:
            out.append({
                'timestamp': h.get('fecha_cambio') or h.get('timestamp') or datetime.now().isoformat(),
                'message': h.get('descripcion') or h.get('accion') or f"Movimiento: {h.get('idproducto') or ''}"
            })
        return jsonify(out)
    except Exception as e:
        print('Error en api_history:', e)
        return jsonify([])


# Endpoint: GET errores del sistema (desde file log)
@app.route('/api/history_errors')
@requiere_login
def api_history_errors():
    data_dir = Path(__file__).parent / 'data'
    errors_file = data_dir / 'errors_log.json'
    try:
        if not errors_file.exists():
            return jsonify([])
        with open(errors_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        print('Error leyendo errores:', e)
        return jsonify([])


@app.route('/api/log_error', methods=['POST'])
@requiere_login
def api_log_error():
    # Body: { message: 'texto', level: 'error' }
    payload = request.get_json() or {}
    message = payload.get('message') or payload.get('msg') or 'Error sin mensaje'
    detail = payload.get('detail') or payload.get('info') or ''
    level = payload.get('level') or 'error'
    timestamp = datetime.now().isoformat()
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    errors_file = data_dir / 'errors_log.json'
    try:
        existing = []
        if errors_file.exists():
            with open(errors_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        # append
        existing.insert(0, { 'timestamp': timestamp, 'message': message, 'detail': detail, 'level': level })
        # keep reasonable size
        existing = existing[:200]
        with open(errors_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        print('Error escribiendo error log:', e)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
@requiere_login
def api_status():
    estado, estados_detalles = check_sistema_integral()
    global last_manual_update
    return jsonify({
        'connection_state': estado,
        'status_details': estados_detalles,
        'last_update': last_manual_update.isoformat(),
        'important_events': 0
    })

# --- RUTA INVENTARIO ---
@app.route("/inventario")
@requiere_login
def inventario():
    try:
        # Obtener productos con información básica
        productos = supabase.table("productos").select("*").execute().data

        # Calcular estadísticas
        estadisticas = {
            "total_productos": len(productos),
            "total_stock": sum(p.get("stock", 0) for p in productos),
            "total_valor": sum(p.get("stock", 0) * p.get("precio_unitario", 0) for p in productos),
            "productos_baja_rotacion": len([p for p in productos if p.get("stock", 0) <= 5])
        }

        # Enriquecer datos de productos
        for producto in productos:
            stock = producto.get("stock", 0)
            # Estado
            if stock == 0:
                producto["status"] = "Agotado"
                producto["status_class"] = "text-red-500 bg-red-100 dark:bg-red-900"
            elif stock <= 5:
                producto["status"] = "Stock Bajo"
                producto["status_class"] = "text-yellow-500 bg-yellow-100 dark:bg-yellow-900"
            else:
                producto["status"] = "Normal"
                producto["status_class"] = "text-green-500 bg-green-100 dark:bg-green-900"
            
            # Formato moneda y cálculos
            producto["precio_formato"] = f"${producto.get('precio_unitario', 0):,.0f}"
            producto["valor_total"] = f"${(stock * producto.get('precio_unitario', 0)):,.0f}"

            # Fecha
            if producto.get("fecha_modificacion"):
                fecha = datetime.fromisoformat(str(producto["fecha_modificacion"]).replace('Z', '+00:00'))
                producto["fecha_formato"] = fecha.strftime("%d/%m/%Y %H:%M")
            else:
                producto["fecha_formato"] = "-"

        return render_template(
            "pagina/inventario.html",
            productos=productos,
            estadisticas=estadisticas,
            categorias=sorted(set(p.get("categoria") for p in productos if p.get("categoria")))
        )
    except Exception as e:
        print(f"Error en ruta inventario: {e}")
        flash("Error al cargar el inventario", "error")
        return redirect(url_for("dashboard"))

# Funciones para conversiones seguras
def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

# --- API: AGREGAR PRODUCTO ---
@app.route("/api/productos/agregar", methods=["POST"])
@requiere_login
def agregar_producto():
    try:
        data = request.json

        # Validación campos obligatorios
        if not data.get('nombre') or not data.get('categoria'):
            return jsonify({"success": False, "error": "Nombre y categoría son requeridos"}), 400

        # Construir diccionario con datos validados y convertidos
        nuevo_producto = {
            "nombre": data["nombre"],
            "categoria": data.get("categoria"),
            "stock": safe_int(data.get("stock")),
            "precio_unitario": safe_float(data.get("precio_unitario")),
            "peso": safe_float(data.get("peso"), default=1.0),  # peso > 0 requerido
            "descripcion": data.get("descripcion", ""),
            "id_estante": safe_int(data.get("id_estante")) if data.get("id_estante") not in (None, "") else None,
            "fecha_ingreso": datetime.now().isoformat(),
            "ingresado_por": session.get("usuario_id"),
            "fecha_modificacion": datetime.now().isoformat(),
            "modificado_por": session.get("usuario_id")
        }

        # Insertar producto en la base de datos vía supabase
        result = supabase.table("productos").insert(nuevo_producto).execute()

        # Registrar historial si la inserción fue exitosa
        if result.data:
            producto_id = result.data[0].get('idproducto')
            supabase.table("historial").insert({
                "idproducto": producto_id,
                "fecha_cambio": datetime.now().isoformat(),
                "id_estante": nuevo_producto.get("id_estante"),
                "cambio_de_peso": nuevo_producto.get("peso"),
                "realizado_por": session.get("usuario_id")
            }).execute()

        return jsonify({"success": True, "mensaje": "Producto agregado correctamente", "data": result.data})

    except Exception as e:
        print(f"Error al agregar producto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    
# --- API: ELIMINAR PRODUCTO ---
@app.route("/api/productos/<int:id>", methods=["DELETE"])
@requiere_login
def eliminar_producto(id):
    try:
        result = supabase.table("productos").delete().eq("idproducto", id).execute()
        if result.error:
            return jsonify({"success": False, "error": str(result.error)}), 400
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500




# --- APIs de Inventario ---
@app.route("/api/productos/filtrar", methods=["GET"])
@requiere_login
def filtrar_productos():
    """API para filtrar productos"""
    try:
        search = request.args.get('search', '').lower()
        category = request.args.get('category')
        status = request.args.get('status')
        date_start = request.args.get('dateStart')
        date_end = request.args.get('dateEnd')

        productos = supabase.table("productos").select("*").execute().data
        productos_filtrados = productos.copy()

        # Aplicar filtros
        if search:
            productos_filtrados = [p for p in productos_filtrados 
                                 if search in p.get('nombre', '').lower()]
        
        if category:
            productos_filtrados = [p for p in productos_filtrados 
                                 if p.get('categoria') == category]
        
        if status:
            if status == 'normal':
                productos_filtrados = [p for p in productos_filtrados if p.get('stock', 0) >= 10]
            elif status == 'bajo':
                productos_filtrados = [p for p in productos_filtrados if 0 < p.get('stock', 0) < 10]
            elif status == 'agotado':
                productos_filtrados = [p for p in productos_filtrados if p.get('stock', 0) == 0]

        if date_start and date_end:
            start = datetime.strptime(date_start, '%Y-%m-%d')
            end = datetime.strptime(date_end, '%Y-%m-%d')
            productos_filtrados = [p for p in productos_filtrados 
                                 if start <= datetime.fromisoformat(p.get('fecha_modificacion', '')).date() <= end]

        # Enriquecer datos antes de enviar
        for p in productos_filtrados:
            p["precio_formato"] = f"${p.get('precio_unitario', 0):,.0f}"
            p["valor_total"] = f"${(p.get('stock', 0) * p.get('precio_unitario', 0)):,.0f}"
            p["fecha_formato"] = datetime.fromisoformat(str(p.get('fecha_modificacion'))).strftime("%d/%m/%Y %H:%M") if p.get('fecha_modificacion') else "-"

        return jsonify(productos_filtrados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/productos/<int:id>/stock", methods=["PUT"])
@requiere_login
def actualizar_stock(id):
    """API para gestionar stock"""
    try:
        data = request.json
        productos_resp = supabase.table("productos").select("*").eq("idproducto", id).execute()
        if not productos_resp.data:
            return jsonify({"error": "Producto no encontrado"}), 404
        
        producto = productos_resp.data[0]
        nuevo_stock = producto["stock"]

        amount = safe_int(data.get("amount"))
        if data.get("action") == "add":
            nuevo_stock += amount
        elif data.get("action") == "remove":
            if nuevo_stock >= amount:
                nuevo_stock -= amount
            else:
                return jsonify({"error": "Stock insuficiente"}), 400
        else:
            return jsonify({"error": "Acción inválida"}), 400
        
        supabase.table("productos").update({"stock": nuevo_stock}).eq("idproducto", id).execute()

        supabase.table("historial").insert({
            "idproducto": id,
            "fecha_cambio": datetime.now().isoformat(),
            "cambio_de_peso": amount if data.get("action") == "add" else -amount,
            "realizado_por": session.get("usuario_id"),
            "id_estante": producto.get("id_estante")
        }).execute()

        return jsonify({"message": "Stock actualizado", "nuevo_stock": nuevo_stock})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- LOGOUT ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- Página de movimientos ---

@app.route("/movimientos")
def movimientos():
    # Obtener todos los movimientos
    movimientos = supabase.table("movimientos_inventario").select("*").execute().data

    # Obtener productos y estantes (solo id y nombre/categoria)
    productos = supabase.table("productos").select("idproducto, nombre").execute().data
    estantes = supabase.table("estantes").select("id_estante, categoria").execute().data

    # Crear diccionarios de referencia para IDs
    productos_dict = {p['idproducto']: p['nombre'] for p in productos}
    estantes_dict = {e['id_estante']: e['categoria'] for e in estantes}

    usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data
    usuarios_dict = {u['rut_usuario']: u['nombre'] for u in usuarios}


    # Enriquecer cada movimiento con nombres descriptivos
    for m in movimientos:
        m["producto"] = productos_dict.get(m.get("idproducto"), "Desconocido")
        m["ubicacion"] = estantes_dict.get(m.get("id_estante"), "Desconocido")
        m["usuario_nombre"] = usuarios_dict.get(m.get("rut_usuario"), "Desconocido")

    return render_template("pagina/movimientos_inventario.html", movimientos=movimientos)




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

@app.route("/conexion_supabase/tendencia_ventas")
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

# Ventas por Producto (dinero vendido, top 8)
@app.route("/api/ventas_por_producto")
def api_ventas_por_producto():
    try:
        response = supabase.table("detalle_ventas")\
            .select("idproducto, productos(nombre), cantidad, precio_unitario")\
            .execute()

        if not response.data:
            return jsonify({"productos": [], "crecimiento": 0})

        # Agrupar ventas por producto
        ventas_por_producto = {}
        for registro in response.data:
            producto_id = registro['idproducto']
            nombre = registro.get('productos', {}).get('nombre', f'Producto {producto_id}')
            cantidad = registro['cantidad'] or 0
            precio = registro['precio_unitario'] or 0
            venta_total = cantidad * precio

            if producto_id not in ventas_por_producto:
                ventas_por_producto[producto_id] = {
                    "nombre": nombre,
                    "ventas": 0,
                    "registros": []
                }

            ventas_por_producto[producto_id]["ventas"] += venta_total
            ventas_por_producto[producto_id]["registros"].append(venta_total)

        # Ordenar y limitar a top 8
        productos_formateados = sorted(
            [
                {
                    "nombre": datos["nombre"],
                    "ventas": round(datos["ventas"], 2),
                    "crecimiento": calcular_crecimiento_producto_simple(datos["registros"])
                }
                for datos in ventas_por_producto.values()
            ],
            key=lambda x: x["ventas"],
            reverse=True
        )[:8]

        # Crecimiento total (aquí lo dejas simple o calculado después)
        crecimiento = calcular_crecimiento_simple(ventas_por_producto)

        return jsonify({
            "productos": productos_formateados,
            "crecimiento": round(crecimiento, 1)
        })

    except Exception as e:
        print(f"❌ Error en api_ventas_por_producto: {e}")
        return jsonify({"productos": [], "crecimiento": 0})


def calcular_crecimiento_simple(ventas_por_producto):
    """Calcula un crecimiento simple basado en las ventas totales"""
    try:
        if not ventas_por_producto:
            return 0
        
        # Simular crecimiento basado en la variación entre productos
        total_ventas = sum(datos['ventas'] for datos in ventas_por_producto.values())
        if total_ventas > 0:
            # Crecimiento simulado entre 5% y 15% para demostración
            return 8.5
        return 0
    except Exception as e:
        print(f"Error calculando crecimiento simple: {e}")
        return 5.0

def calcular_crecimiento_producto_simple(registros):
    """Calcula crecimiento simple para un producto"""
    try:
        if len(registros) < 2:
            return 0
        
        # Crecimiento simulado para demostración
        return round((len(registros) * 2.5) % 15, 1)
    except Exception as e:
        print(f"Error calculando crecimiento producto simple: {e}")
        return 0

# --- Ruta de debug para ver datos crudos ---
@app.route("/api/debug_datos")
def api_debug_datos():
    try:
        response = supabase.table("detalle_ventas")\
            .select("idproducto, productos(nombre), cantidad, precio_unitario")\
            .limit(10)\
            .execute()
        
        return jsonify({
            "total_registros": len(response.data) if response.data else 0,
            "datos": response.data if response.data else []
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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



def agrupar_notificaciones_por_fecha(notificaciones):
    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)
    grupos = defaultdict(list)

    for notif in notificaciones:
        # Usar fecha_creacion (alertas DB) o fecha relevante dinámica
        fecha_raw = notif.get("fecha_creacion") or notif.get("timestamp") or notif.get("fecha_formateada")
        fecha_notif = None
        if fecha_raw:
            try:
                # Descartar microsegundos si están presentes
                fecha_str = str(fecha_raw).split('.')[0]
                fecha = datetime.fromisoformat(fecha_str)
                fecha_notif = fecha.date()
            except Exception:
                fecha_notif = hoy
            if fecha_notif == hoy:
                grupos["Hoy"].append(notif)
            elif fecha_notif == ayer:
                grupos["Ayer"].append(notif)
            else:
                grupos[fecha_notif.strftime("%d/%m/%Y")].append(notif)
        else:
            grupos["Sin fecha"].append(notif)
    return grupos

@app.context_processor
def agregar_alertas_y_notificaciones():
    alertas_db = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data or []
    notificaciones = [a for a in alertas_db if a.get("estado") != "resuelto"]
    notificaciones_agrupadas = agrupar_notificaciones_por_fecha(notificaciones)

    productos = supabase.table("productos").select("*").execute().data or []
    pesajes = supabase.table("pesajes").select("*").execute().data or []
    limite = datetime.now() - timedelta(days=7)

    productos_inactivos = []
    for p in productos:
        ult_pesaje = [ps for ps in pesajes if ps["idproducto"] == p["idproducto"]]
        for ps in ult_pesaje:
            if isinstance(ps.get("fecha_pesaje"), str):
                ps["fecha_pesaje"] = datetime.fromisoformat(ps["fecha_pesaje"])
        if not ult_pesaje or max(ps["fecha_pesaje"] for ps in ult_pesaje) < limite:
            productos_inactivos.append(p["nombre"])

    alertas_dinamicas = []
    if productos_inactivos:
        listado_corto = ", ".join(productos_inactivos[:3])
        extra = f" y {len(productos_inactivos)-3} más" if len(productos_inactivos) > 3 else ""
        alertas_dinamicas.append({
            "titulo": "Productos inactivos (solo aviso)",
            "descripcion": f"No se ha pesado en la última semana: {listado_corto}{extra}.",
            "icono": "⚠️",
            "tipo_color": "amarillo",
            "fecha_creacion": datetime.now().isoformat(),
            "solo_ui": True
        })

    return dict(
        notificaciones=notificaciones + alertas_dinamicas,
        notificaciones_agrupadas=agrupar_notificaciones_por_fecha(notificaciones + alertas_dinamicas)
    )



# MAIN
if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.watch("templates/**/*.html")
    server.watch("static/**/*.css")
    server.watch("static/**/*.js")
    server.watch("**/*.py")
    server.serve(port=5000, host="127.0.0.1", debug=True)