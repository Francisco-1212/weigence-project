from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from collections import Counter
from jinja2 import Undefined
from .utils import requiere_login, agrupar_notificaciones_por_fecha
from .decorators import requiere_rol

@bp.route("/dashboard")
@requiere_rol('operador', 'supervisor', 'administrador')
def dashboard():
    from app.utils.eventohumano import registrar_evento_humano
    from app.utils.sesiones_activas import registrar_usuario_activo
    
    # Registrar al usuario actual como activo
    rut = session.get('usuario_id')
    nombre = session.get('usuario_nombre')
    rol = session.get('usuario_rol')
    if rut and nombre:
        registrar_usuario_activo(rut, nombre, rol)
    
    if session.get('last_page') != 'dashboard':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó al Dashboard")
        session['last_page'] = 'dashboard'
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

    alertas_criticas = [a for a in alertas_db if a.get("tipo_color") in ["danger", "rojo"] and a.get("estado") == "pendiente"][-3:]


    def limpiar_json(obj):
        if isinstance(obj, list):
            return [limpiar_json(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: limpiar_json(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, Undefined):
            return None
        return obj

    return render_template(
        "pagina/index.html",
        productos=limpiar_json(productos),
        pesajes=limpiar_json(pesajes),
        usuarios=limpiar_json(usuarios),
        estantes=limpiar_json(estantes),
        historial=limpiar_json(historial),
        alertas_criticas=limpiar_json(alertas_criticas),
        valor_total_inventario=valor_total_inventario,
        articulos_vendidos=articulos_vendidos,
        producto_mas_vendido=producto_mas_vendido,
        productos_agotados=productos_agotados,
        ventas_totales=ventas_totales,
        movimientos=[]
    )
    


@bp.route('/api/dashboard_filtrado')
@requiere_rol('farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador')
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

    ventas = supabase.table("ventas").select("*") \
        .gte("fecha_venta", start.isoformat()) \
        .lte("fecha_venta", now.isoformat()) \
        .execute().data or []

    ids_ventas = [v["idventa"] for v in ventas]
    detalles = supabase.table("detalle_ventas").select("*") \
        .in_("idventa", ids_ventas) \
        .execute().data or []

    productos_info = supabase.table("productos").select("idproducto,nombre").execute().data or []

    ventas_por_producto = {p["idproducto"]: {"nombre": p["nombre"], "ventas": 0.0, "cantidad": 0} for p in productos_info}
    articulos_vendidos = 0

    for dv in detalles:
        idprod = dv["idproducto"]
        if idprod in ventas_por_producto:
            cantidad = dv.get("cantidad", 0)
            precio = dv.get("precio_unitario", 0)
            ventas_por_producto[idprod]["ventas"] += cantidad * precio
            ventas_por_producto[idprod]["cantidad"] += cantidad
            articulos_vendidos += cantidad

    productos_arr = list(ventas_por_producto.values())
    productos_por_ventas = sorted(productos_arr, key=lambda x: x["ventas"], reverse=True)
    productos_por_cantidad_desc = sorted(productos_arr, key=lambda x: x["cantidad"], reverse=True)
    productos_por_cantidad_asc = sorted(productos_arr, key=lambda x: x["cantidad"])

    producto_mas_vendido = productos_por_cantidad_desc[0]["nombre"] if productos_por_cantidad_desc else "Sin datos"
    ventas_totales = sum(p["ventas"] for p in productos_arr)

    grafico = {
        "productos": productos_por_ventas[:6],
        "labels": [p["nombre"] for p in productos_por_ventas[:6]],
        "data": [p["ventas"] for p in productos_por_ventas[:6]],
    }

    productos_top = [{"nombre": p["nombre"], "cantidad": int(p.get("cantidad", 0)), "ventas": round(float(p.get("ventas", 0)), 0)} for p in productos_por_cantidad_desc[:5]]
    productos_low = [{"nombre": p["nombre"], "cantidad": int(p.get("cantidad", 0)), "ventas": round(float(p.get("ventas", 0)), 0)} for p in productos_por_cantidad_asc[:5]]

    return jsonify({
        "grafico": grafico,
        "ventas_totales": int(ventas_totales),
        "ventas_cambio": 0,
        "articulos_vendidos": articulos_vendidos,
        "producto_mas_vendido": producto_mas_vendido,
        "productos_top": productos_top,
        "productos_low": productos_low
    })
