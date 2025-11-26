from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime   
from .utils import requiere_login
from .decorators import requiere_rol

@bp.route("/alertas")
@requiere_rol('operador', 'supervisor', 'administrador')
def alertas():
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'alertas':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó a Alertas")
        session['last_page'] = 'alertas'
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
    Crea o actualiza alertas según el stock de productos y fechas de vencimiento.
    - Marca como 'pendiente' si el stock está bajo o agotado.
    - Marca como 'resuelto' si el producto vuelve a stock normal (>5).
    - Crea alertas de vencimiento próximo basándose en fecha_ingreso.
    """
    try:
        from datetime import timedelta
        nuevas = []
        fecha_hoy = datetime.now()

        # Obtener alertas existentes
        existentes = supabase.table("alertas").select("id, titulo, estado").execute().data or []
        titulos_activos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "pendiente"}
        titulos_resueltos = {a["titulo"].lower(): a["id"] for a in existentes if a.get("estado") == "resuelto"}

        # --- Obtener productos ---
        productos = supabase.table("productos").select("idproducto, nombre, stock, fecha_ingreso").execute().data or []

        for p in productos:
            nombre = p.get("nombre", "Producto sin nombre")
            stock = p.get("stock", 0)
            idproducto = p.get("idproducto")
            fecha_ingreso_str = p.get("fecha_ingreso")
            
            titulo_bajo = f"Bajo stock: {nombre}".lower()
            titulo_agotado = f"Stock agotado: {nombre}".lower()

            # --- Caso 1: stock normal (>5) → resolver alertas existentes de stock ---
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
                            "idproducto": idproducto,
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
                            "idproducto": idproducto,
                            "fecha_creacion": datetime.now().isoformat()
                        })

            # --- Caso 4: Alertas de Vencimiento basadas en fecha_ingreso ---
            if fecha_ingreso_str:
                try:
                    # Parsear fecha_ingreso (puede venir en varios formatos)
                    if isinstance(fecha_ingreso_str, str):
                        fecha_ingreso = datetime.fromisoformat(fecha_ingreso_str.replace('Z', '+00:00'))
                    else:
                        fecha_ingreso = fecha_ingreso_str
                    
                    # Calcular días desde el ingreso (asumiendo vida útil de 180 días)
                    dias_desde_ingreso = (fecha_hoy - fecha_ingreso.replace(tzinfo=None)).days
                    dias_vida_util = 180  # 6 meses de vida útil
                    dias_restantes = dias_vida_util - dias_desde_ingreso
                    
                    # Definir alertas de vencimiento
                    titulo_vence_30 = f"Vencimiento próximo (30 días): {nombre}".lower()
                    titulo_vence_15 = f"Vencimiento próximo (15 días): {nombre}".lower()
                    titulo_vence_7 = f"Vencimiento crítico (7 días): {nombre}".lower()
                    titulo_vencido = f"Producto vencido: {nombre}".lower()
                    
                    # Resolver alertas de vencimiento si el producto está fresco
                    if dias_restantes > 30:
                        for titulo_venc in [titulo_vence_30, titulo_vence_15, titulo_vence_7, titulo_vencido]:
                            if titulo_venc in titulos_activos:
                                alerta_id = titulos_activos[titulo_venc]
                                supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alerta_id).execute()
                    
                    # Producto vencido
                    elif dias_restantes <= 0:
                        if titulo_vencido not in titulos_activos:
                            if titulo_vencido in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vencido]).execute()
                            else:
                                nuevas.append({
                                    "titulo": f"Producto vencido: {nombre}",
                                    "descripcion": f"El producto ha superado su vida útil de {dias_vida_util} días. Días vencidos: {abs(dias_restantes)}.",
                                    "icono": "dangerous",
                                    "tipo_color": "negro",
                                    "estado": "pendiente",
                                    "idproducto": idproducto,
                                    "fecha_creacion": datetime.now().isoformat()
                                })
                    
                    # Vencimiento crítico (7 días)
                    elif 0 < dias_restantes <= 7:
                        if titulo_vence_7 not in titulos_activos:
                            if titulo_vence_7 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_7]).execute()
                            else:
                                nuevas.append({
                                    "titulo": f"Vencimiento crítico (7 días): {nombre}",
                                    "descripcion": f"El producto vencerá en {dias_restantes} días. ¡Acción urgente requerida!",
                                    "icono": "warning",
                                    "tipo_color": "rojo",
                                    "estado": "pendiente",
                                    "idproducto": idproducto,
                                    "fecha_creacion": datetime.now().isoformat()
                                })
                    
                    # Vencimiento próximo (15 días)
                    elif 7 < dias_restantes <= 15:
                        if titulo_vence_15 not in titulos_activos:
                            if titulo_vence_15 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_15]).execute()
                            else:
                                nuevas.append({
                                    "titulo": f"Vencimiento próximo (15 días): {nombre}",
                                    "descripcion": f"El producto vencerá en {dias_restantes} días. Considere priorizar su venta.",
                                    "icono": "schedule",
                                    "tipo_color": "naranja",
                                    "estado": "pendiente",
                                    "idproducto": idproducto,
                                    "fecha_creacion": datetime.now().isoformat()
                                })
                    
                    # Vencimiento próximo (30 días)
                    elif 15 < dias_restantes <= 30:
                        if titulo_vence_30 not in titulos_activos:
                            if titulo_vence_30 in titulos_resueltos:
                                supabase.table("alertas").update({"estado": "pendiente"}).eq("id", titulos_resueltos[titulo_vence_30]).execute()
                            else:
                                nuevas.append({
                                    "titulo": f"Vencimiento próximo (30 días): {nombre}",
                                    "descripcion": f"El producto vencerá en {dias_restantes} días. Monitoree su rotación.",
                                    "icono": "event",
                                    "tipo_color": "amarilla",
                                    "estado": "pendiente",
                                    "idproducto": idproducto,
                                    "fecha_creacion": datetime.now().isoformat()
                                })
                
                except Exception as e:
                    print(f"⚠️ Error procesando fecha de vencimiento para {nombre}: {e}")

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


@bp.route("/api/actualizar_alerta/<int:alerta_id>", methods=["POST"])
@requiere_login
def actualizar_alerta(alerta_id):
    try:
        datos = request.json
        nuevo_estado = datos.get("estado")
        
        if not nuevo_estado or nuevo_estado not in ["pendiente", "resuelto"]:
            return jsonify({"success": False, "error": "Estado inválido"}), 400
        
        # Actualizar la alerta
        supabase.table("alertas").update({"estado": nuevo_estado}).eq("id", alerta_id).execute()
        
        print(f"✅ Alerta #{alerta_id} actualizada a estado: {nuevo_estado}")
        return jsonify({"success": True, "mensaje": "Alerta actualizada correctamente"})
    except Exception as e:
        print(f"❌ Error al actualizar alerta {alerta_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/generar_alertas_basicas")
def generar_alertas_basicas_api():
    resultado = generar_alertas_basicas()
    if resultado:
        return jsonify({"success": True, "mensaje": "Alertas generadas correctamente"})
    else:
        return jsonify({"success": False, "mensaje": "Error al generar alertas"}), 500