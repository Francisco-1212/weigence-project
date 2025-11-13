from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime   
from .utils import requiere_login
from .decorators import requiere_rol

@bp.route("/alertas")
@requiere_rol('bodeguera', 'supervisor', 'jefe', 'administrador')
def alertas():
    from .utils import obtener_notificaciones
    try:
        # --- Datos base ---
        alertas = (
            supabase.table("alertas")
            .select("*")
            .order("fecha_creacion", desc=True)
            .execute()
            .data
            or []
        )

        productos = supabase.table("productos").select("idproducto, nombre").execute().data or []
        usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data or []

        productos_dict = {p["idproducto"]: p["nombre"] for p in productos}
        usuarios_dict = {u["rut_usuario"]: u["nombre"] for u in usuarios}

        for alerta in alertas:
            alerta["nombre_producto"] = productos_dict.get(alerta.get("idproducto"), "Sin producto")
            alerta["nombre_usuario"] = usuarios_dict.get(alerta.get("idusuario"), "Sistema")

            if alerta.get("fecha_creacion"):
                try:
                    fecha = datetime.fromisoformat(str(alerta["fecha_creacion"]).replace("Z", "+00:00"))
                    alerta["fecha_formateada"] = fecha.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    alerta["fecha_formateada"] = "-"
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
            notificaciones_agrupadas=notificaciones_agrupadas,
        )

    except Exception as e:
        print(f"Error en ruta alertas: {e}")
        flash("Error al cargar las alertas", "error")
        return redirect(url_for("main.dashboard"))


# =========================================================
# FUNCIÓN DE GENERACIÓN AUTOMÁTICA DE ALERTAS
# =========================================================
def generar_alertas_basicas():
    """
    Crea o actualiza alertas según el stock de productos.
    - Marca como 'pendiente' si el stock está bajo o agotado.
    - Marca como 'resuelto' si el producto vuelve a stock normal (>5).
    """
    try:
        nuevas = []

        # Obtener alertas existentes
        existentes = supabase.table("alertas").select("id, titulo, estado").execute().data or []
        titulos_activos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "pendiente"}
        titulos_resueltos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "resuelto"}

        # --- Obtener productos ---
        productos = supabase.table("productos").select("idproducto, nombre, stock").execute().data or []

        for p in productos:
            nombre = p.get("nombre", "Producto sin nombre")
            stock = p.get("stock", 0)
            titulo_bajo = f"Bajo stock: {nombre}".lower()
            titulo_agotado = f"Stock agotado: {nombre}".lower()

            # --- Caso 1: stock normal (>5) → resolver alertas existentes ---
            # --- Caso 1: stock normal (>5) → resolver alertas existentes ---
            if stock > 5:
                for alerta in existentes:
                    titulo = alerta.get("titulo", "").lower()
                    if nombre.lower() in titulo and "stock" in titulo and alerta.get("estado") == "pendiente":
                        supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alerta["id"]).execute()


            # --- Caso 2: stock == 0 → crear o reactivar alerta roja ---
            elif stock == 0:
                if titulo_agotado not in titulos_activos:
                    # Reactivar si estaba resuelta
                    if titulo_agotado in titulos_resueltos:
                        supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_agotado]).execute()
                    else:
                        nuevas.append({
                            "titulo": f"Stock agotado: {nombre}",
                            "descripcion": "El producto se ha agotado completamente.",
                            "icono": "cancel",
                            "tipo_color": "rojo",
                            "estado": "pendiente",
                            "fecha_creacion": datetime.now().isoformat()
                        })

            # --- Caso 3: stock entre 1–5 → crear o reactivar alerta amarilla ---
            elif 0 < stock <= 5:
                if titulo_bajo not in titulos_activos:
                    if titulo_bajo in titulos_resueltos:
                        supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_bajo]).execute()
                    else:
                        nuevas.append({
                            "titulo": f"Bajo stock: {nombre}",
                            "descripcion": f"Quedan {stock} unidades disponibles.",
                            "icono": "inventory_2",
                            "tipo_color": "amarilla",
                            "estado": "pendiente",
                            "fecha_creacion": datetime.now().isoformat()
                        })

        # Insertar nuevas alertas
        if nuevas:
            supabase.table("alertas").insert(nuevas).execute()
            print(f"✅ {len(nuevas)} nuevas alertas creadas.")

        return True

    except Exception as e:
        print(f"Error generando alertas: {e}")
        return False

@bp.route("/api/descartar_alerta/<int:alerta_id>", methods=["POST"])
def descartar_alerta(alerta_id):
    try:
        # Marca como descartada (mejor que borrar para mantener historial)
        supabase.table("alertas").update({"estado": "descartada"}).eq("id", alerta_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error al descartar alerta {alerta_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/generar_alertas_basicas")

def generar_alertas_basicas_api():
    resultado = generar_alertas_basicas()
    if resultado:
        return jsonify({"success": True, "mensaje": "Alertas generadas correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al generar alertas"}), 500