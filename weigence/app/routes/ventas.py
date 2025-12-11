from flask import render_template, jsonify, request, session, redirect, url_for, flash
from .utils import requiere_login
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from .decorators import requiere_rol


@bp.route("/ventas")
@requiere_rol('operador', 'supervisor', 'administrador')
def ventas():
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'ventas':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó a Ventas")
        session['last_page'] = 'ventas'
    ventas = supabase.table("ventas").select("*").order("fecha_venta", desc=True).execute().data
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
        
        # Registrar evento de venta en auditoría
        from app.utils.eventohumano import registrar_evento_humano
        usuario_nombre = session.get("usuario_nombre", "Usuario")
        registrar_evento_humano("venta", f"{usuario_nombre} realizó Venta #{id_venta} por ${total_venta:,.0f}")
        
        # 2. Crear detalles de venta y actualizar inventario
        detalles_venta = []
        movimientos_inventario = []
        
        for producto in datos["productos"]:
            idproducto = producto["idproducto"]
            cantidad = producto["cantidad"]
            precio_unitario = producto["precio_unitario"]
            
            # Obtener información del producto (incluyendo peso en GRAMOS)
            producto_info = supabase.table("productos").select("id_estante, stock, peso").eq("idproducto", idproducto).execute()
            
            if not producto_info.data:
                continue
            
            stock_actual = producto_info.data[0].get("stock", 0)
            id_estante = producto_info.data[0].get("id_estante")
            peso_gramos = producto_info.data[0].get("peso", 0)  # Peso en GRAMOS desde BD
            peso_kg = peso_gramos / 1000  # Convertir a kilogramos
            
            # Validar stock disponible
            if stock_actual < cantidad:
                return jsonify({
                    "success": False, 
                    "error": f"Stock insuficiente para el producto ID {idproducto}. Disponible: {stock_actual}, Solicitado: {cantidad}"
                }), 400
            
            # Detalle de venta (sin subtotal, es columna generada automáticamente)
            detalle = {
                "idventa": id_venta,
                "idproducto": idproducto,
                "cantidad": cantidad,
                "precio_unitario": precio_unitario
            }
            detalles_venta.append(detalle)
            

            # Intentar emparejar con retiro ya registrado (asíncrono)
            from datetime import timedelta
            now = datetime.now()
            ventana_ini = (now - timedelta(minutes=5)).isoformat()
            ventana_fin = (now + timedelta(minutes=5)).isoformat()
            # Buscar retiro pendiente (no validado por venta) en la ventana
            retiro_match = supabase.table("movimientos_inventario").select("id_movimiento, cantidad, peso_total, timestamp, es_venta_validada").eq("idproducto", idproducto).eq("tipo_evento", "Retirar").eq("es_venta_validada", False).gte("timestamp", ventana_ini).lte("timestamp", ventana_fin).execute().data
            if retiro_match:
                # Emparejar: actualizar retiro como validado
                for retiro in retiro_match:
                    supabase.table("movimientos_inventario").update({
                        "es_venta_validada": True,
                        "motivo_sospecha": None,
                        "observacion": f"Emparejado con venta #{id_venta}"
                    }).eq("id_movimiento", retiro["id_movimiento"]).execute()
            else:
                # No hay retiro, registrar venta pendiente
                movimiento = {
                    "tipo_evento": "VentaPendiente",
                    "idproducto": idproducto,
                    "id_estante": id_estante,
                    "cantidad": cantidad,
                    "peso_por_unidad": peso_kg,
                    "peso_total": cantidad * peso_kg,
                    "rut_usuario": rut_usuario,
                    "timestamp": now.isoformat(),
                    "observacion": f"Venta #{id_venta} pendiente de retiro"
                }
                movimientos_inventario.append(movimiento)
            
            # Actualizar stock del producto
            nuevo_stock = stock_actual - cantidad
            supabase.table("productos").update({
                "stock": nuevo_stock,
                "fecha_modificacion": datetime.now().isoformat(),
                "modificado_por": rut_usuario
            }).eq("idproducto", idproducto).execute()
        
        # 3. Insertar detalles de venta
        if detalles_venta:
            try:
                detalle_response = supabase.table("detalle_ventas").insert(detalles_venta).execute()
                if not detalle_response.data:
                    return jsonify({"success": False, "error": "Error al registrar detalles de venta"}), 500
            except Exception as e:
                return jsonify({"success": False, "error": f"Error al insertar detalles: {str(e)}"}), 500
        
        # 4. Insertar movimientos de inventario
        if movimientos_inventario:
            try:
                movimiento_response = supabase.table("movimientos_inventario").insert(movimientos_inventario).execute()
            except Exception as e:
                pass  # No crítico
        
        return jsonify({
            "success": True,
            "mensaje": "Venta registrada exitosamente",
            "id_venta": id_venta,
            "total": total_venta
        })
        
    except Exception as e:
        import traceback
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/api/productos/disponibles")
@requiere_login
def productos_disponibles():
    try:
        productos = supabase.table("productos").select("idproducto, nombre, stock, precio_unitario").gt("stock", 0).execute()
        return jsonify(productos.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/promedio_consumo")
@requiere_login
def api_promedio_consumo():
    """Devuelve promedio de cantidad vendida por producto y promedio total.
    Útil como fallback cuando no hay series temporales de consumo.
    """
    try:
        detalle = supabase.table("detalle_ventas").select("idproducto, cantidad").execute().data
        productos = supabase.table("productos").select("idproducto, nombre").execute().data

        if not detalle:
            return jsonify({"promedio_total": 0, "promedio_por_producto": []})

        # map id->nombre
        prod_map = {p['idproducto']: p.get('nombre', f'Producto {p["idproducto"]}') for p in (productos or [])}

        sums = {}
        counts = {}
        for d in detalle:
            pid = d.get('idproducto')
            qty = d.get('cantidad') or 0
            sums[pid] = sums.get(pid, 0) + qty
            counts[pid] = counts.get(pid, 0) + 1

        promedio_por_producto = []
        total_sum = 0
        total_count = 0
        for pid, s in sums.items():
            c = counts.get(pid, 1)
            avg = s / c if c else 0
            nombre = prod_map.get(pid, f'Producto {pid}')
            promedio_por_producto.append({"idproducto": pid, "nombre": nombre, "promedio": round(avg, 2)})
            total_sum += s
            total_count += c

        promedio_total = (total_sum / total_count) if total_count else 0

        return jsonify({"promedio_total": round(promedio_total, 2), "promedio_por_producto": promedio_por_producto})
    except Exception as e:
        return jsonify({"promedio_total": 0, "promedio_por_producto": []})


# =============================================
# Exportación de Ventas a Excel
# =============================================

# Endpoint registrado en __init__.py con exención CSRF
@requiere_rol('operador', 'supervisor', 'administrador')
def exportar_ventas_excel():
    """Exporta ventas a Excel con formato profesional"""
    from flask import send_file
    from app.utils.excel_exporter import ExcelExporter
    import logging
    import traceback
    
    logger = logging.getLogger(__name__)
    
    try:
        # Obtener filtros del request
        data = request.get_json() or {}
        filtros = data.get('filtros', {})
        
        # Obtener ventas desde la base de datos
        query = supabase.table("ventas").select("*").order("fecha_venta", desc=True)
        
        # Aplicar filtros de fecha si existen
        if filtros.get('fechaDesde'):
            query = query.gte('fecha_venta', filtros['fechaDesde'])
        if filtros.get('fechaHasta'):
            query = query.lte('fecha_venta', filtros['fechaHasta'])
        
        # Ejecutar query
        response = query.execute()
        ventas = response.data or []
        
        if len(ventas) == 0:
            return jsonify({
                'success': False,
                'message': 'No hay ventas registradas para exportar'
            }), 404
        
        # Obtener usuarios (vendedores)
        usuarios = supabase.table("usuarios").select("rut_usuario, nombre").execute().data or []
        usuarios_dict = {u["rut_usuario"]: u["nombre"] for u in usuarios}
        
        # Enriquecer datos de ventas
        ventas_enriquecidas = []
        
        for idx, venta in enumerate(ventas, 1):
            # Obtener ID de venta (puede ser 'id_venta' o 'idventa')
            id_venta = venta.get('id_venta') or venta.get('idventa')
            
            # IMPORTANTE: Las ventas se guardan con 'rut_usuario', no 'rut_vendedor'
            rut_vendedor = (venta.get('rut_usuario') or      # Este es el campo correcto
                           venta.get('rut_vendedor') or 
                           venta.get('rutvendedor') or 
                           venta.get('rutusuario') or 
                           venta.get('rut') or 
                           venta.get('vendedor_rut'))
            
            # Obtener detalles de esta venta específica
            total_productos = 0
            total_unidades = 0
            productos_nombres = []
            
            try:
                detalle_response = supabase.table("detalle_ventas").select("*, productos(nombre)").eq('idventa', id_venta).execute()
                detalles = detalle_response.data or []
                
                if detalles:
                    productos_unicos = {}
                    for d in detalles:
                        id_producto = d.get('idproducto')
                        if id_producto:
                            productos_unicos[id_producto] = d.get('productos', {}).get('nombre', f'Producto {id_producto}')
                        total_unidades += d.get('cantidad', 0)
                    total_productos = len(productos_unicos)
                    productos_nombres = list(productos_unicos.values())
            except Exception as e:
                pass
            
            # Buscar el nombre del vendedor
            vendedor_nombre = usuarios_dict.get(rut_vendedor, None)
            
            # Si no se encuentra por RUT exacto, intentar buscar sin guión
            if not vendedor_nombre and rut_vendedor:
                rut_sin_guion = str(rut_vendedor).replace('-', '')
                for rut_key, nombre in usuarios_dict.items():
                    if str(rut_key).replace('-', '') == rut_sin_guion:
                        vendedor_nombre = nombre
                        rut_vendedor = rut_key  # Actualizar con el formato correcto
                        break
            
            if not vendedor_nombre:
                vendedor_nombre = 'Desconocido'
            
            # Si aún no hay RUT, marcar como N/A
            if not rut_vendedor:
                rut_vendedor = 'N/A'
            
            ventas_enriquecidas.append({
                'id_venta': id_venta or '',
                'fecha': venta.get('fecha_venta', ''),
                'vendedor_rut': rut_vendedor,
                'vendedor_nombre': vendedor_nombre,
                'total': venta.get('total', 0),
                'total_productos': total_productos,
                'total_unidades': total_unidades,
                'productos': ', '.join(productos_nombres[:3]) + ('...' if len(productos_nombres) > 3 else '')
            })
        
        # Generar Excel
        exporter = ExcelExporter()
        excel_file = exporter.exportar_ventas(ventas_enriquecidas, filtros)
        
        # Generar nombre de archivo
        fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'Weigence_Ventas_{fecha_actual}.xlsx'
        
        logger.info(f"Exportación Excel generada: {filename} ({len(ventas)} ventas)")
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error al exportar ventas a Excel: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error al generar el archivo Excel: {str(e)}'
        }), 500
