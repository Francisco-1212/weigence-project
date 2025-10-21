from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime
from .utils import obtener_notificaciones   # <-- Importa la función


@bp.route("/alertas")
def alertas():
    try:
        # --- Datos base ---
        alertas = supabase.table("alertas").select("*").order('fecha_creacion', desc=True).execute().data
        productos = supabase.table("productos").select("idproducto, nombre").execute().data
        usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data

        productos_dict = {p["idproducto"]: p["nombre"] for p in productos}
        usuarios_dict = {u["rut_usuario"]: u["nombre"] for u in usuarios}

        for alerta in alertas:
            alerta["nombre_producto"] = productos_dict.get(alerta.get("idproducto"), "Sin producto")
            alerta["nombre_usuario"] = usuarios_dict.get(alerta.get("idusuario"), "Sistema")
            if alerta.get("fecha_creacion"):
                fecha = datetime.fromisoformat(str(alerta["fecha_creacion"]).replace('Z', '+00:00'))
                alerta["fecha_formateada"] = fecha.strftime("%d/%m/%Y %H:%M")
            else:
                alerta["fecha_formateada"] = "-"

        # --- Notificaciones globales ---
        notificaciones, notificaciones_agrupadas = obtener_notificaciones(session.get("usuario_id"))

        # --- Estadísticas ---
        total_alertas = len(alertas)
        alertas_pendientes = len([a for a in alertas if a.get("estado") == "pendiente"])
        alertas_resueltas = len([a for a in alertas if a.get("estado") == "resuelto"])

        # --- Renderizado ---
        return render_template(
            "pagina/alertas.html",
            alertas=alertas,
            total_alertas=total_alertas,
            alertas_pendientes=alertas_pendientes,
            alertas_resueltas=alertas_resueltas,
            notificaciones=notificaciones,
            notificaciones_agrupadas=notificaciones_agrupadas
        )

    except Exception as e:
        print(f"Error en ruta alertas: {e}")
        flash("Error al cargar las alertas", "error")
        return redirect(url_for("main.dashboard"))
