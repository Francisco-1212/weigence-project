from datetime import datetime, timedelta

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from api.conexion_supabase import supabase

from . import bp
from .decorators import requiere_rol
from .utils import obtener_notificaciones, requiere_login


@bp.route("/alertas")
@requiere_rol("operador", "supervisor", "administrador")
def alertas():
    from app.utils.eventohumano import registrar_evento_humano

    if session.get("last_page") != "alertas":
        usuario_nombre = session.get("usuario_nombre", "Usuario")
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingreso a Alertas")
        session["last_page"] = "alertas"

    try:
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

            fecha_valor = alerta.get("fecha_creacion")
            if fecha_valor:
                try:
                    fecha = datetime.fromisoformat(str(fecha_valor).replace("Z", "+00:00"))
                    alerta["fecha_formateada"] = fecha.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    alerta["fecha_formateada"] = "-"
            else:
                alerta["fecha_formateada"] = "-"

        notificaciones, notificaciones_agrupadas = obtener_notificaciones(session.get("usuario_id"))

        total_alertas = len(alertas)
        alertas_pendientes = len([a for a in alertas if a.get("estado") == "pendiente"])
        alertas_resueltas = len([a for a in alertas if a.get("estado") == "resuelto"])

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
# FUNCION DE GENERACION AUTOMATICA DE ALERTAS
# =========================================================
def generar_alertas_basicas():
    """
    Crea o actualiza alertas segun stock y fechas de vencimiento.
    - Marca pendiente si el stock esta bajo o agotado.
    - Marca resuelto si el producto vuelve a stock normal (>5).
    - Crea alertas de vencimiento basado en fecha_ingreso.
    - Solo procesa productos activos (activo=True o sin columna activo).
    """
    try:
        nuevas = []
        fecha_hoy = datetime.now()

        existentes = supabase.table("alertas").select("id, titulo, estado, idproducto").execute().data or []
        titulos_activos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "pendiente"}
        titulos_resueltos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "resuelto"}

        # Obtener solo productos activos
        try:
            productos = supabase.table("productos").select("idproducto, nombre, stock, fecha_ingreso, activo").eq("activo", True).execute().data or []
        except:
            # Si la columna activo no existe, obtener todos
            productos = supabase.table("productos").select("idproducto, nombre, stock, fecha_ingreso").execute().data or []
        
        # Obtener IDs de productos activos
        ids_productos_activos = {p.get("idproducto") for p in productos}
        
        # Resolver alertas de productos que ya no existen o están inactivos
        for alerta in existentes:
            id_prod = alerta.get("idproducto")
            if id_prod and id_prod not in ids_productos_activos and alerta.get("estado") in ["pendiente", "activo"]:
                supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alerta["id"]).execute()
                print(f"[ALERTA] Resuelta alerta de producto inexistente/inactivo: {alerta.get('titulo')}")

        for p in productos:
            nombre = p.get("nombre", "Producto sin nombre")
            stock = p.get("stock", 0)
            idproducto = p.get("idproducto")
            fecha_ingreso_str = p.get("fecha_ingreso")

            titulo_bajo = f"Bajo stock: {nombre}".lower()
            titulo_agotado = f"Stock agotado: {nombre}".lower()

            if stock > 5:
                for alerta in existentes:
                    titulo = alerta.get("titulo", "").lower()
                    if nombre.lower() in titulo and "stock" in titulo and alerta.get("estado") == "pendiente":
                        supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alerta["id"]).execute()

            elif stock == 0:
                if titulo_agotado not in titulos_activos:
                    if titulo_agotado in titulos_resueltos:
                        supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_agotado]).execute()
                    else:
                        nuevas.append(
                            {
                                "titulo": f"Stock agotado: {nombre}",
                                "descripcion": "El producto se ha agotado completamente.",
                                "icono": "cancel",
                                "tipo_color": "rojo",
                                "estado": "pendiente",
                                "idproducto": idproducto,
                                "fecha_creacion": datetime.now().isoformat(),
                            }
                        )

            elif 0 < stock <= 5:
                if titulo_bajo not in titulos_activos:
                    if titulo_bajo in titulos_resueltos:
                        supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_bajo]).execute()
                    else:
                        nuevas.append(
                            {
                                "titulo": f"Bajo stock: {nombre}",
                                "descripcion": f"Quedan {stock} unidades disponibles.",
                                "icono": "inventory_2",
                                "tipo_color": "amarilla",
                                "estado": "pendiente",
                                "idproducto": idproducto,
                                "fecha_creacion": datetime.now().isoformat(),
                            }
                        )

            if fecha_ingreso_str:
                try:
                    fecha_ingreso = (
                        datetime.fromisoformat(fecha_ingreso_str.replace("Z", "+00:00"))
                        if isinstance(fecha_ingreso_str, str)
                        else fecha_ingreso_str
                    )

                    dias_desde_ingreso = (fecha_hoy - fecha_ingreso.replace(tzinfo=None)).days
                    dias_vida_util = 180
                    dias_restantes = dias_vida_util - dias_desde_ingreso

                    titulo_vence_30 = f"Vencimiento proximo (30 dias): {nombre}".lower()
                    titulo_vence_15 = f"Vencimiento proximo (15 dias): {nombre}".lower()
                    titulo_vence_7 = f"Vencimiento critico (7 dias): {nombre}".lower()
                    titulo_vencido = f"Producto vencido: {nombre}".lower()

                    if dias_restantes > 30:
                        for titulo_venc in [titulo_vence_30, titulo_vence_15, titulo_vence_7, titulo_vencido]:
                            if titulo_venc in titulos_activos:
                                alerta_id = titulos_activos[titulo_venc]
                                supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alerta_id).execute()

                    elif dias_restantes <= 0:
                        if titulo_vencido not in titulos_activos:
                            if titulo_vencido in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vencido]).execute()
                            else:
                                nuevas.append(
                                    {
                                        "titulo": f"Producto vencido: {nombre}",
                                        "descripcion": f"El producto ha superado su vida util de {dias_vida_util} dias. Dias vencidos: {abs(dias_restantes)}.",
                                        "icono": "dangerous",
                                        "tipo_color": "negro",
                                        "estado": "pendiente",
                                        "idproducto": idproducto,
                                        "fecha_creacion": datetime.now().isoformat(),
                                    }
                                )

                    elif 0 < dias_restantes <= 7:
                        if titulo_vence_7 not in titulos_activos:
                            if titulo_vence_7 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_7]).execute()
                            else:
                                nuevas.append(
                                    {
                                        "titulo": f"Vencimiento critico (7 dias): {nombre}",
                                        "descripcion": f"El producto vencera en {dias_restantes} dias. Accion urgente requerida!",
                                        "icono": "warning",
                                        "tipo_color": "rojo",
                                        "estado": "pendiente",
                                        "idproducto": idproducto,
                                        "fecha_creacion": datetime.now().isoformat(),
                                    }
                                )

                    elif 7 < dias_restantes <= 15:
                        if titulo_vence_15 not in titulos_activos:
                            if titulo_vence_15 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_15]).execute()
                            else:
                                nuevas.append(
                                    {
                                        "titulo": f"Vencimiento proximo (15 dias): {nombre}",
                                        "descripcion": f"El producto vencera en {dias_restantes} dias. Considere priorizar su venta.",
                                        "icono": "schedule",
                                        "tipo_color": "naranja",
                                        "estado": "pendiente",
                                        "idproducto": idproducto,
                                        "fecha_creacion": datetime.now().isoformat(),
                                    }
                                )

                    elif 15 < dias_restantes <= 30:
                        if titulo_vence_30 not in titulos_activos:
                            if titulo_vence_30 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_30]).execute()
                            else:
                                nuevas.append(
                                    {
                                        "titulo": f"Vencimiento proximo (30 dias): {nombre}",
                                        "descripcion": f"El producto vencera en {dias_restantes} dias. Monitoree su rotacion.",
                                        "icono": "event",
                                        "tipo_color": "amarilla",
                                        "estado": "pendiente",
                                        "idproducto": idproducto,
                                        "fecha_creacion": datetime.now().isoformat(),
                                    }
                                )

                except Exception as e:
                    print(f"Error procesando fecha de vencimiento para {nombre}: {e}")

        if nuevas:
            supabase.table("alertas").insert(nuevas).execute()
            print(f"{len(nuevas)} nuevas alertas creadas.")

        return True

    except Exception as e:
        print(f"Error generando alertas: {e}")
        return False


@bp.route("/api/descartar_alerta/<int:alerta_id>", methods=["POST"])
def descartar_alerta(alerta_id):
    try:
        supabase.table("alertas").update({"estado": "descartada"}).eq("id", alerta_id).execute()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error al descartar alerta {alerta_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/actualizar_alerta/<int:alerta_id>", methods=["POST"])
@requiere_login
def actualizar_alerta(alerta_id):
    try:
        datos = request.json or {}
        nuevo_estado = datos.get("estado")

        if nuevo_estado not in {"pendiente", "resuelto"}:
            return jsonify({"success": False, "error": "Estado invalido"}), 400

        supabase.table("alertas").update({"estado": nuevo_estado}).eq("id", alerta_id).execute()

        print(f"Alerta #{alerta_id} actualizada a estado: {nuevo_estado}")
        return jsonify({"success": True, "mensaje": "Alerta actualizada correctamente"})
    except Exception as e:
        print(f"Error al actualizar alerta {alerta_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/generar_alertas_basicas")
def generar_alertas_basicas_api():
    resultado = generar_alertas_basicas()
    if resultado:
        return jsonify({"success": True, "mensaje": "Alertas generadas correctamente"})
    return jsonify({"success": False, "mensaje": "Error al generar alertas"}), 500
