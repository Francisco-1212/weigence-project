from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime
from .utils import requiere_login, safe_int, safe_float



@bp.route("/inventario")
@requiere_login
def inventario():
    try:
        productos = supabase.table("productos").select("*").execute().data

        estadisticas = {
            "total_productos": len(productos),
            "total_stock": sum(p.get("stock", 0) for p in productos),
            "total_valor": sum(p.get("stock", 0) * p.get("precio_unitario", 0) for p in productos),
            "productos_baja_rotacion": len([p for p in productos if p.get("stock", 0) <= 5])
        }

        for producto in productos:
            stock = producto.get("stock", 0)
            if stock == 0:
                producto["status"] = "Agotado"
                producto["status_class"] = "text-red-500 bg-red-100 dark:bg-red-900"
            elif stock <= 5:
                producto["status"] = "Stock Bajo"
                producto["status_class"] = "text-yellow-500 bg-yellow-100 dark:bg-yellow-900"
            else:
                producto["status"] = "Normal"
                producto["status_class"] = "text-green-500 bg-green-100 dark:bg-green-900"

            producto["precio_formato"] = f"${producto.get('precio_unitario', 0):,.0f}"
            producto["valor_total"] = f"${(stock * producto.get('precio_unitario', 0)):,.0f}"

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

        supabase.table("productos").update({"stock": nuevo_stock}).eq("idproducto", id).execute()

        supabase.table("historial").insert({
            "idproducto": id,
            "fecha_cambio": datetime.now().isoformat(),
            "cambio_de_peso": amount if action == "add" else -amount,
            "realizado_por": session.get("usuario_id"),
            "id_estante": producto.get("id_estante")
        }).execute()

        return jsonify({"message": "Stock actualizado", "nuevo_stock": nuevo_stock})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
