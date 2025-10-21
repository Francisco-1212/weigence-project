from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime


@bp.route("/movimientos")
def movimientos():
    movimientos = supabase.table("movimientos_inventario").select("*").execute().data
    productos = supabase.table("productos").select("idproducto, nombre").execute().data
    estantes = supabase.table("estantes").select("id_estante, categoria").execute().data
    usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data

    productos_dict = {p['idproducto']: p['nombre'] for p in productos}
    estantes_dict = {e['id_estante']: e['categoria'] for e in estantes}
    usuarios_dict = {u['rut_usuario']: u['nombre'] for u in usuarios}

    for m in movimientos:
        m["producto"] = productos_dict.get(m.get("idproducto"), "Desconocido")
        m["ubicacion"] = estantes_dict.get(m.get("id_estante"), "Desconocido")
        m["usuario_nombre"] = usuarios_dict.get(m.get("rut_usuario"), "Desconocido")

    return render_template("pagina/movimientos.html", movimientos=movimientos)
