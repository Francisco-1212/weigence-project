from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from .utils import requiere_login, safe_int, safe_float, asignar_estante, formatear_estante_codigo
from .decorators import requiere_rol, requiere_autenticacion


def obtener_catalogo_estantes():
    """Retorna un mapa con los estantes disponibles formateados."""
    catalogo = {}
    try:
        respuesta = supabase.table("estantes").select("id_estante").execute()
        estantes = respuesta.data or []
    except Exception as err:
        print(f"Advertencia al cargar estantes: {err}")
        estantes = []

    for estante in estantes:
        id_estante = estante.get("id_estante")
        try:
            id_int = int(id_estante)
        except (TypeError, ValueError):
            continue
        catalogo[id_int] = formatear_estante_codigo(id_int)

    if not catalogo:
        for idx in range(1, 7):
            catalogo[idx] = formatear_estante_codigo(idx)

    return catalogo


def construir_mapa_categorias(productos):
    """Genera un mapa categoría → id_estante basado en los productos existentes."""
    categorias_map = {}
    for producto in productos:
        categoria_nombre = (producto.get("categoria") or "").strip()
        if not categoria_nombre:
            continue
        if categoria_nombre in categorias_map:
            continue
        categorias_map[categoria_nombre] = asignar_estante(categoria_nombre)
    return categorias_map


@bp.route("/inventario")
@requiere_rol('operador', 'supervisor', 'administrador')
def inventario():
    from flask import session
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'inventario':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó al Inventario")
        session['last_page'] = 'inventario'
    try:
        # === 1. Cargar productos y categorías ===
        productos = supabase.table("productos").select("*").execute().data or []

        estantes_catalogo = obtener_catalogo_estantes()
        categorias_map = construir_mapa_categorias(productos)
        categorias_en_contexto = {}
        productos_a_actualizar = []

        for producto in productos:
            categoria_nombre = (producto.get("categoria") or "").strip()
            id_estante_original = producto.get("id_estante")
            id_estante_categoria = categorias_map.get(categoria_nombre) if categoria_nombre else None

            if id_estante_categoria is None and categoria_nombre:
                id_estante_categoria = asignar_estante(categoria_nombre)
                categorias_map[categoria_nombre] = id_estante_categoria

            if id_estante_categoria is not None:
                categorias_en_contexto[categoria_nombre] = id_estante_categoria

                if (
                    producto.get("idproducto") is not None
                    and id_estante_categoria != id_estante_original
                ):
                    productos_a_actualizar.append({
                        "idproducto": producto["idproducto"],
                        "id_estante": id_estante_categoria,
                    })

                producto["id_estante"] = id_estante_categoria
                producto["estante_codigo"] = estantes_catalogo.get(
                    id_estante_categoria,
                    formatear_estante_codigo(id_estante_categoria),
                )
            else:
                producto["estante_codigo"] = ""

        if productos_a_actualizar:
            try:
                supabase.table("productos").upsert(productos_a_actualizar).execute()
            except Exception as err:
                print(f"Advertencia al sincronizar id_estante de productos: {err}")

        productos.sort(key=lambda p: (
            p.get("id_estante") if p.get("id_estante") is not None else float("inf"),
            (p.get("categoria") or "").lower(),
            (p.get("nombre") or "").lower()
        ))

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
            producto["data_stock"] = stock
            precio = producto.get("precio_unitario", 0)
            nombre = producto.get("nombre", "Producto sin nombre")

            if stock == 0:
                producto["status"] = "agotado"
                producto["status_class"] = "text-red-500 bg-red-100 dark:bg-red-900"
            elif stock <= 5:
                producto["status"] = "bajo"
                producto["status_class"] = "text-yellow-500 bg-yellow-100 dark:bg-yellow-900"
            else:
                producto["status"] = "ormal"
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
        estantes_codigos = {int(k): v for k, v in estantes_catalogo.items()}
        estantes_validos = sorted(estantes_codigos.keys())
        categorias_ordenadas = sorted(nombre for nombre in categorias_en_contexto.keys() if nombre)

        return render_template(
            "pagina/inventario.html",
            productos=productos,
            estadisticas=estadisticas,
            categorias=categorias_ordenadas,
            categoria_estantes=categorias_en_contexto,
            alertas_sugeridas=alertas_sugeridas,
            estante_codigos=estantes_codigos,
            estantes_validos=estantes_validos,
        )

    except Exception as e:
        print(f"Error en ruta inventario: {e}")
        flash("Error al cargar el inventario", "error")
        return redirect(url_for("main.dashboard"))




@bp.route("/api/productos/agregar", methods=["POST"])
@requiere_rol('operador', 'supervisor', 'administrador')
def agregar_producto():
    try:
        data = request.json
        if not data.get('nombre') or not data.get('categoria'):
            return jsonify({"success": False, "error": "Nombre y categoría son requeridos"}), 400

        categoria_nombre = (data.get("categoria") or "").strip()
        id_estante_categoria = asignar_estante(categoria_nombre)

        nuevo_producto = {
            "nombre": data["nombre"],
            "categoria": categoria_nombre,
            "stock": safe_int(data.get("stock")),
            "precio_unitario": safe_float(data.get("precio_unitario")),
            "peso": safe_float(data.get("peso"), default=1.0),
            "descripcion": data.get("descripcion", ""),
            "id_estante": id_estante_categoria,
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
@requiere_rol('supervisor', 'administrador')
def eliminar_producto(id):
    try:
        result = supabase.table("productos").delete().eq("idproducto", id).execute()
        return jsonify({"success": True, "result": result.data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/productos/filtrar", methods=["GET"])
@requiere_rol('operador', 'supervisor', 'administrador')
def filtrar_productos():
    try:
        search = request.args.get('search', '').lower()
        category = request.args.get('category')
        status = request.args.get('status')
        date_start = request.args.get('dateStart')
        date_end = request.args.get('dateEnd')

        productos = supabase.table("productos").select("*").execute().data or []
        for producto in productos:
            categoria_nombre = (producto.get("categoria") or "").strip()
            if not categoria_nombre:
                continue
            id_estante_categoria = asignar_estante(categoria_nombre)
            if id_estante_categoria is not None:
                producto["id_estante"] = id_estante_categoria
                producto["estante_codigo"] = formatear_estante_codigo(id_estante_categoria)
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
@requiere_rol('operador', 'supervisor', 'administrador')
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
@requiere_rol('operador', 'supervisor', 'administrador')
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
@requiere_rol('operador', 'supervisor', 'administrador')
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
@requiere_rol('operador', 'supervisor', 'administrador')
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
@requiere_rol('operador', 'supervisor', 'administrador')
def proyeccion_consumo():
    try:
        dias = int(request.args.get("dias", 14))
        fecha_inicio = (datetime.now() - timedelta(days=dias)).date().isoformat()

        # Une ventas y detalles, agrupando por día
        query = (
            supabase.rpc(
                "custom_query",
                {
                    "query": f"""
                        SELECT
                            DATE(v.fecha_venta) AS fecha,
                            SUM(d.cantidad) AS unidades
                        FROM detalle_ventas d
                        JOIN ventas v ON v.idventa = d.idventa
                        WHERE v.fecha_venta >= '{fecha_inicio}'
                        GROUP BY DATE(v.fecha_venta)
                        ORDER BY fecha ASC;
                    """
                },
            )
            .execute()
        )

        data = query.data or []
        return jsonify(data)

    except Exception as e:
        print("[Error /api/proyeccion_consumo]:", e)
        return jsonify([])
    
def recalcular_estantes():
    # Recalcula peso actual de cada estante
    estantes = supabase.table("estantes").select("id_estante, peso_maximo").execute().data
    for e in estantes:
        total_peso = (
            supabase.table("productos")
            .select("peso, stock")
            .eq("id_estante", e["id_estante"])
            .execute()
            .data
        )
        total = sum(p["peso"] * p["stock"] for p in total_peso)
        estado = (
            "crítico"
            if total >= e["peso_maximo"]
            else "advertencia"
            if total >= e["peso_maximo"] * 0.8
            else "estable"
        )
        supabase.table("estantes").update(
            {
                "peso_actual": total,
                "estado": estado,
                "ultima_actualizacion": datetime.now(),
            }
        ).eq("id_estante", e["id_estante"]).execute()
