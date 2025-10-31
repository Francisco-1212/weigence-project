from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from .utils import requiere_login, safe_int, safe_float


@bp.route("/inventario")
@requiere_login
def inventario():
    try:
        # === 1. Cargar productos ===
        productos = supabase.table("productos").select("*").execute().data or []

        # === 2. Calcular estadísticas ===
        total_stock = sum(p.get("stock", 0) for p in productos)
        total_valor = sum(p.get("stock", 0) * p.get("precio_unitario", 0) for p in productos)
        productos_baja_rotacion = len([p for p in productos if p.get("stock", 0) <= 5])

        estadisticas = {
            "total_productos": len(productos),
            "total_stock": total_stock,
            "total_valor": total_valor,
            "productos_baja_rotacion": productos_baja_rotacion,
        }

        # === 3. Clasificación visual de productos ===
        for producto in productos:
            stock = producto.get("stock", 0)
            precio = producto.get("precio_unitario", 0)
            nombre = producto.get("nombre", "Producto sin nombre")

            if stock == 0:
                producto["status"] = "Agotado"
                producto["status_class"] = "text-red-500 bg-red-100 dark:bg-red-900"
            elif stock <= 5:
                producto["status"] = "Stock Bajo"
                producto["status_class"] = "text-yellow-500 bg-yellow-100 dark:bg-yellow-900"
            else:
                producto["status"] = "Normal"
                producto["status_class"] = "text-green-500 bg-green-100 dark:bg-green-900"

            producto["precio_formato"] = f"${precio:,.0f}".replace(",", ".")
            producto["valor_total"] = f"${(stock * precio):,.0f}".replace(",", ".")

            if producto.get("fecha_modificacion"):
                try:
                    fecha = datetime.fromisoformat(str(producto["fecha_modificacion"]).replace("Z", "+00:00"))
                    producto["fecha_formato"] = fecha.strftime("%d/%m/%Y %H:%M")
                except Exception:
                    producto["fecha_formato"] = "-"
            else:
                producto["fecha_formato"] = "-"

        # === 4. Crear alertas automáticas en BD (solo stock) ===
        alertas_nuevas = []
        existentes = supabase.table("alertas").select("titulo").eq("estado", "pendiente").execute().data or []
        titulos_existentes = {a["titulo"].lower() for a in existentes}

        for p in productos:
            nombre = p.get("nombre", "Producto sin nombre")
            stock = p.get("stock", 0)

            if stock == 0:
                titulo = f"Stock agotado: {nombre}"
                if titulo.lower() not in titulos_existentes:
                    alertas_nuevas.append({
                        "titulo": titulo,
                        "descripcion": "El producto se ha agotado completamente.",
                        "icono": "cancel",
                        "tipo_color": "rojo"
                    })
            elif stock <= 5:
                titulo = f"Bajo stock: {nombre}"
                if titulo.lower() not in titulos_existentes:
                    alertas_nuevas.append({
                        "titulo": titulo,
                        "descripcion": f"Quedan {stock} unidades disponibles.",
                        "icono": "inventory_2",
                        "tipo_color": "amarilla"
                    })

        if alertas_nuevas:
            supabase.table("alertas").insert(alertas_nuevas).execute()

        # === 5. Crear alertas personalizadas para el panel de Inventario ===
        alertas_sugeridas = []
        try:
            # --- Alerta 1: Stock ---
            bajos = [p for p in productos if p["stock"] <= 5]
            if bajos:
                producto = bajos[0]
                color = "rojo" if producto["stock"] == 0 else "amarilla"
                alertas_sugeridas.append({
                    "titulo": "Stock Crítico" if producto["stock"] == 0 else "Stock Bajo",
                    "descripcion": f"{producto['nombre']} tiene {producto['stock']} unidades restantes.",
                    "icono": "inventory_2",
                    "color": color
                })
            else:
                alertas_sugeridas.append({
                    "titulo": "Stock Estable",
                    "descripcion": "Todos los productos tienen stock suficiente.",
                    "icono": "check_circle",
                    "color": "verde"
                })

            # --- Alerta 2: Estantes ---
            estantes = supabase.table("v_estantes_estado").select("*").execute().data or []
            estado_riesgo = next((e for e in estantes if e["estado"] in ("advertencia", "critico")), None)
            if estado_riesgo:
                alertas_sugeridas.append({
                    "titulo": f"Estante {estado_riesgo['id_estante']} en {estado_riesgo['estado'].capitalize()}",
                    "descripcion": f"Ocupación {round(estado_riesgo['ocupacion_pct'], 1)}%",
                    "icono": "warehouse",
                    "color": "rojo" if estado_riesgo["estado"] == "critico" else "amarilla"
                })
            else:
                alertas_sugeridas.append({
                    "titulo": "Estantes Estables",
                    "descripcion": "Todos los estantes se encuentran en estado óptimo.",
                    "icono": "done_all",
                    "color": "verde"
                })

            # --- Alerta 3: Positiva general ---
            alertas_sugeridas.append({
                "titulo": "Operación sin incidentes",
                "descripcion": "No se detectaron anomalías recientes en el sistema.",
                "icono": "verified",
                "color": "verde"
            })

        except Exception as err:
            print(f"Error al generar alertas sugeridas en inventario: {err}")
            alertas_sugeridas = []

        # === 6. Render final ===
        return render_template(
            "pagina/inventario.html",
            productos=productos,
            estadisticas=estadisticas,
            categorias=sorted(set(p.get("categoria") for p in productos if p.get("categoria"))),
            alertas_sugeridas=alertas_sugeridas
        )

    except Exception as e:
        print(f"Error en ruta inventario: {e}")
        flash("Error al cargar el inventario", "error")
        return redirect(url_for("main.dashboard"))




@bp.route("/api/productos/agregar", methods=["POST"])
@requiere_login
def agregar_producto():
    try:
        data = request.json
        if not data.get('nombre') or not data.get('categoria'):
            return jsonify({"success": False, "error": "Nombre y categoría son requeridos"}), 400

        nuevo_producto = {
            "nombre": data["nombre"],
            "categoria": data.get("categoria"),
            "stock": safe_int(data.get("stock")),
            "precio_unitario": safe_float(data.get("precio_unitario")),
            "peso": safe_float(data.get("peso"), default=1.0),
            "descripcion": data.get("descripcion", ""),
            "id_estante": safe_int(data.get("id_estante")) if data.get("id_estante") else None,
            "fecha_ingreso": datetime.now().isoformat(),
            "ingresado_por": session.get("usuario_id"),
            "fecha_modificacion": datetime.now().isoformat(),
            "modificado_por": session.get("usuario_id")
        }

        result = supabase.table("productos").insert(nuevo_producto).execute()

        if result.data:
            producto_id = result.data[0].get('idproducto')
            supabase.table("historial").insert({
                "idproducto": producto_id,
                "fecha_cambio": datetime.now().isoformat(),
                "id_estante": nuevo_producto.get("id_estante"),
                "cambio_de_peso": nuevo_producto.get("peso"),
                "realizado_por": session.get("usuario_id")
            }).execute()

        return jsonify({"success": True, "mensaje": "Producto agregado correctamente"})
    except Exception as e:
        print(f"Error al agregar producto: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/productos/<int:id>", methods=["DELETE"])
@requiere_login
def eliminar_producto(id):
    try:
        result = supabase.table("productos").delete().eq("idproducto", id).execute()
        return jsonify({"success": True, "result": result.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/productos/filtrar", methods=["GET"])
@requiere_login
def filtrar_productos():
    try:
        search = request.args.get('search', '').lower()
        category = request.args.get('category')
        status = request.args.get('status')
        date_start = request.args.get('dateStart')
        date_end = request.args.get('dateEnd')

        productos = supabase.table("productos").select("*").execute().data
        filtrados = productos.copy()

        if search:
            filtrados = [p for p in filtrados if search in p.get('nombre', '').lower()]
        if category:
            filtrados = [p for p in filtrados if p.get('categoria') == category]
        if status:
            if status == 'normal':
                filtrados = [p for p in filtrados if p.get('stock', 0) >= 10]
            elif status == 'bajo':
                filtrados = [p for p in filtrados if 0 < p.get('stock', 0) < 10]
            elif status == 'agotado':
                filtrados = [p for p in filtrados if p.get('stock', 0) == 0]
        if date_start and date_end:
            start = datetime.strptime(date_start, '%Y-%m-%d')
            end = datetime.strptime(date_end, '%Y-%m-%d')
            filtrados = [p for p in filtrados
                         if start <= datetime.fromisoformat(p.get('fecha_modificacion')).date() <= end]

        for p in filtrados:
            p["precio_formato"] = f"${p.get('precio_unitario', 0):,.0f}"
            p["valor_total"] = f"${(p.get('stock', 0) * p.get('precio_unitario', 0)):,.0f}"
            if p.get("fecha_modificacion"):
                p["fecha_formato"] = datetime.fromisoformat(p["fecha_modificacion"]).strftime("%d/%m/%Y %H:%M")
            else:
                p["fecha_formato"] = "-"

        return jsonify(filtrados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/productos/<int:id>/stock", methods=["PUT"])
@requiere_login
def actualizar_stock(id):
    try:
        data = request.json
        resp = supabase.table("productos").select("*").eq("idproducto", id).execute()
        if not resp.data:
            return jsonify({"error": "Producto no encontrado"}), 404

        producto = resp.data[0]
        nuevo_stock = producto["stock"]
        amount = safe_int(data.get("amount"))
        action = data.get("action")

        if action == "add":
            nuevo_stock += amount
        elif action == "remove":
            if nuevo_stock >= amount:
                nuevo_stock -= amount
            else:
                return jsonify({"error": "Stock insuficiente"}), 400
        else:
            return jsonify({"error": "Acción inválida"}), 400

        # --- Actualizar stock en Supabase ---
        supabase.table("productos").update({
            "stock": nuevo_stock,
            "fecha_modificacion": datetime.now().isoformat(),
            "modificado_por": session.get("usuario_id")
        }).eq("idproducto", id).execute()

        # --- Registrar en historial ---
        supabase.table("historial").insert({
            "idproducto": id,
            "fecha_cambio": datetime.now().isoformat(),
            "cambio_de_peso": amount if action == "add" else -amount,
            "realizado_por": session.get("usuario_id"),
            "id_estante": producto.get("id_estante")
        }).execute()

        # --- Generar alertas automáticamente ---
        try:
            from .inventario import generar_alertas_basicas
            generar_alertas_basicas()
        except Exception as e:
            print(f"Error generando alertas tras actualizar stock: {e}")

        return jsonify({
            "message": "Stock actualizado",
            "nuevo_stock": nuevo_stock
        })

    except Exception as e:
        print(f"Error en actualizar_stock: {e}")
        return jsonify({"error": str(e)}), 500


# api inventario

@bp.route("/api/estantes_estado")
@requiere_login
def estantes_estado():
    try:
        data = supabase.table("v_estantes_estado").select("*").execute().data
        return jsonify(data)
    except Exception as e:
        print("Error en /api/estantes_estado:", e)
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# 2) Alertas activas (pendientes)
# ------------------------------------------------------------
@bp.route("/api/alertas_activas")
@requiere_login
def alertas_activas():
    try:
        alertas = (
            supabase.table("alertas")
            .select("*")
            .eq("estado", "pendiente")
            .order("fecha_creacion", desc=True)
            .limit(3)
            .execute()
            .data
        )
        return jsonify(alertas)
    except Exception as e:
        print("Error obteniendo alertas:", e)
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# 3) Actualizar estado de una alerta (resuelta o ignorada)
# ------------------------------------------------------------
@bp.route("/api/alertas/<int:id>/estado", methods=["PUT"])
@requiere_login
def actualizar_estado_alerta(id):
    try:
        nuevo_estado = request.json.get("estado")
        if nuevo_estado not in ["pendiente", "resuelto", "ignorada"]:
            return jsonify({"error": "Estado inválido"}), 400

        supabase.table("alertas").update({
            "estado": nuevo_estado,
            "fecha_modificacion": datetime.now().isoformat(),
            "idusuario": session.get("usuario_id")
        }).eq("id", id).execute()

        return jsonify({"success": True, "mensaje": f"Alerta marcada como {nuevo_estado}"})
    except Exception as e:
        print("Error al actualizar alerta:", e)
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------------
# 4) Proyección de consumo (últimos 30 días)
# ------------------------------------------------------------
@bp.route("/api/proyeccion_consumo")
@requiere_login
def proyeccion_consumo():
    try:
        dias = int(request.args.get("dias", 30))
        fecha_inicio = (datetime.now() - timedelta(days=dias)).date().isoformat()

        consumo = supabase.table("v_consumo_diario") \
            .select("*") \
            .gte("fecha", fecha_inicio) \
            .execute().data

        # agrupar por fecha
        resumen = {}
        for c in consumo:
            f = c["fecha"]
            resumen[f] = resumen.get(f, 0) + float(c["consumo"] or 0)

        serie = [{"fecha": f, "consumo": round(v, 2)} for f, v in sorted(resumen.items())]
        return jsonify(serie)
    except Exception as e:
        print("Error en /api/proyeccion_consumo:", e)
        return jsonify({"error": str(e)}), 500


