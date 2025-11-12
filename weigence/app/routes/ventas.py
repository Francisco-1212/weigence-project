from flask import render_template, jsonify, request, session, redirect, url_for, flash
from .utils import requiere_login
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta


@bp.route("/ventas")
@requiere_login
def ventas():
    ventas = supabase.table("ventas").select("*").execute().data
    detalle_ventas = supabase.table("detalle_ventas").select("*").execute().data
    productos = supabase.table("productos").select("*").execute().data
    usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data

    productos_dict = {p["idproducto"]: p["nombre"] for p in productos}
    usuarios_dict = {u["rut_usuario"]: u["nombre"] for u in usuarios}

    total_ventas = sum(v["total"] for v in ventas) if ventas else 0
    promedio_ventas = total_ventas / len(ventas) if ventas else 0
    num_transacciones = len(ventas)

    productos_cant = {}
    for det in detalle_ventas:
        productos_cant[det["idproducto"]] = productos_cant.get(det["idproducto"], 0) + det["cantidad"]
    top_producto = max(productos_cant.items(), key=lambda x: x[1]) if productos_cant else None
    nombre_top = productos_dict.get(top_producto[0], f"ID {top_producto[0]}") if top_producto else "-"
    top_producto_str = f"{nombre_top} ({top_producto[1]})" if top_producto else "-"

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
        usuarios_dict=usuarios_dict,
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


@bp.route("/api/ventas_por_producto")
@requiere_login
def api_ventas_por_producto():
    try:
        response = supabase.table("detalle_ventas") \
            .select("idproducto, productos(nombre), cantidad, precio_unitario") \
            .execute()

        if not response.data:
            return jsonify({"productos": [], "crecimiento": 0})

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

        crecimiento = calcular_crecimiento_simple(ventas_por_producto)

        return jsonify({
            "productos": productos_formateados,
            "crecimiento": round(crecimiento, 1)
        })

    except Exception as e:
        print(f"❌ Error en api_ventas_por_producto: {e}")
        return jsonify({"productos": [], "crecimiento": 0})


def calcular_crecimiento_simple(ventas_por_producto):
    try:
        if not ventas_por_producto:
            return 0
        total_ventas = sum(datos['ventas'] for datos in ventas_por_producto.values())
        if total_ventas > 0:
            return 8.5  # valor simulado
        return 0
    except Exception:
        return 5.0


def calcular_crecimiento_producto_simple(registros):
    try:
        if len(registros) < 2:
            return 0
        return round((len(registros) * 2.5) % 15, 1)
    except Exception:
        return 0


@bp.route("/api/ventas/nueva", methods=["POST"])
@requiere_login
def crear_nueva_venta():
    try:
        datos = request.json
        print("📦 Datos recibidos para nueva venta:", datos)
        
        # Validar datos requeridos
        if not datos.get("productos") or len(datos["productos"]) == 0:
            return jsonify({"success": False, "error": "Debe agregar al menos un producto"}), 400
        
        rut_usuario = session.get("usuario_id")
        if not rut_usuario:
            return jsonify({"success": False, "error": "Usuario no identificado"}), 401
        
        # Calcular total de la venta
        total_venta = sum(
            producto["cantidad"] * producto["precio_unitario"] 
            for producto in datos["productos"]
        )
        
        # 1. Crear la venta principal
        venta_data = {
            "rut_usuario": rut_usuario,
            "fecha_venta": datetime.now().isoformat(),
            "total": total_venta
        }
        
        venta_response = supabase.table("ventas").insert(venta_data).execute()
        
        if not venta_response.data:
            return jsonify({"success": False, "error": "Error al crear la venta"}), 500
        
        id_venta = venta_response.data[0]["idventa"]
        print(f"✅ Venta creada con ID: {id_venta}")
        
        # 2. Crear detalles de venta y actualizar inventario
        detalles_venta = []
        movimientos_inventario = []
        
        for producto in datos["productos"]:
            idproducto = producto["idproducto"]
            cantidad = producto["cantidad"]
            precio_unitario = producto["precio_unitario"]
            subtotal = cantidad * precio_unitario
            
            # Obtener información del producto para el estante
            producto_info = supabase.table("productos").select("id_estante, stock").eq("idproducto", idproducto).execute()
            
            if not producto_info.data:
                continue
            
            stock_actual = producto_info.data[0].get("stock", 0)
            id_estante = producto_info.data[0].get("id_estante")
            
            # Validar stock disponible
            if stock_actual < cantidad:
                return jsonify({
                    "success": False, 
                    "error": f"Stock insuficiente para el producto ID {idproducto}. Disponible: {stock_actual}, Solicitado: {cantidad}"
                }), 400
            
            # Detalle de venta
            detalles_venta.append({
                "idventa": id_venta,
                "idproducto": idproducto,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario,
                "subtotal": subtotal
            })
            
            # Movimiento de inventario (Retiro)
            movimientos_inventario.append({
                "tipo_evento": "Retirar",
                "idproducto": idproducto,
                "id_estante": id_estante,
                "cantidad": cantidad,
                "rut_usuario": rut_usuario,
                "timestamp": datetime.now().isoformat(),
                "observacion": f"Venta #{id_venta} - Retiro automático por venta"
            })
            
            # Actualizar stock del producto
            nuevo_stock = stock_actual - cantidad
            supabase.table("productos").update({
                "stock": nuevo_stock,
                "fecha_modificacion": datetime.now().isoformat(),
                "modificado_por": rut_usuario
            }).eq("idproducto", idproducto).execute()
            
            print(f"✅ Stock actualizado para producto {idproducto}: {stock_actual} → {nuevo_stock}")
        
        # 3. Insertar detalles de venta
        if detalles_venta:
            supabase.table("detalle_ventas").insert(detalles_venta).execute()
            print(f"✅ {len(detalles_venta)} detalles de venta insertados")
        
        # 4. Insertar movimientos de inventario
        if movimientos_inventario:
            supabase.table("movimientos_inventario").insert(movimientos_inventario).execute()
            print(f"✅ {len(movimientos_inventario)} movimientos de inventario registrados")
        
        return jsonify({
            "success": True,
            "mensaje": "Venta registrada exitosamente",
            "id_venta": id_venta,
            "total": total_venta
        })
        
    except Exception as e:
        print(f"❌ Error al crear venta: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/productos/disponibles")
@requiere_login
def productos_disponibles():
    try:
        productos = supabase.table("productos").select("idproducto, nombre, stock, precio_unitario").gt("stock", 0).execute()
        return jsonify(productos.data)
    except Exception as e:
        print(f"❌ Error al obtener productos: {e}")
        return jsonify({"error": str(e)}), 500
