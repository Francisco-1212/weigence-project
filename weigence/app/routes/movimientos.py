from flask import render_template
from .utils import requiere_login
from . import bp
from api.conexion_supabase import supabase
from flask import request, jsonify, session
from datetime import datetime
from .decorators import requiere_rol

@bp.route("/api/movimientos/<int:id_movimiento>")
@requiere_login
def obtener_movimiento(id_movimiento):
    """Obtiene un movimiento específico por ID"""
    try:
        q = (
            supabase.table("movimientos_inventario")
            .select("""
                *,
                productos:idproducto (
                    nombre,
                    peso
                ),
                estantes:id_estante (
                    nombre
                ),
                usuarios:rut_usuario (
                    nombre
                )
            """)
            .eq("id_movimiento", id_movimiento)
            .single()
            .execute()
        )
        
        if not q.data:
            return jsonify({"success": False, "error": "Movimiento no encontrado"}), 404
        
        m = q.data
        productos_data = m.get("productos") or {}
        estantes_data = m.get("estantes") or {}
        usuarios_data = m.get("usuarios") or {}
        
        movimiento = {
            "id_movimiento": m.get("id_movimiento"),
            "idproducto": m.get("idproducto"),
            "producto": productos_data.get("nombre", "Producto no encontrado"),
            "tipo_evento": m.get("tipo_evento"),
            "cantidad": m.get("cantidad"),
            "peso_por_unidad": m.get("peso_por_unidad", 0),
            "peso_total": m.get("peso_total", 0),
            "ubicacion": estantes_data.get("nombre", "Desconocida"),
            "usuario_nombre": usuarios_data.get("nombre", "Usuario desconocido"),
            "rut_usuario": m.get("rut_usuario", ""),
            "timestamp": m.get("timestamp", "")[:16].replace("T", " "),
            "observacion": m.get("observacion", "")
        }
        
        return jsonify({"success": True, "movimiento": movimiento})
        
    except Exception as e:
        print(f"Error al obtener movimiento {id_movimiento}:", e)
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/movimientos")
@requiere_rol('bodeguera', 'supervisor', 'jefe', 'administrador')
def movimientos():
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'movimientos':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó a Movimientos")
        session['last_page'] = 'movimientos'
    try:
        #print("Realizando consulta a Supabase...")
        q = (
            supabase.table("movimientos_inventario")
            .select("""
                *,
                productos:idproducto (
                    nombre,
                    peso
                ),
                estantes:id_estante (
                    nombre
                ),
                usuarios:rut_usuario (
                    nombre
                )
            """)
            .order("timestamp", desc=True)
            .limit(50)
            .execute()
        )
        
 #       print("Respuesta de Supabase:", q.data)

        movimientos = []
        for m in q.data:
            try:
                # Manejar casos donde las relaciones pueden ser None
                productos_data = m.get("productos") or {}
                estantes_data = m.get("estantes") or {}
                usuarios_data = m.get("usuarios") or {}
                
                mov = {
                    "id_movimiento": m.get("id_movimiento"),
                    "producto": productos_data.get("nombre", "Producto no encontrado"),
                    "tipo_evento": m.get("tipo_evento"),
                    "cantidad": m.get("cantidad", 0),
                    "peso_por_unidad": m.get("peso_por_unidad", 0),
                    "peso_total": m.get("peso_total", 0),
                    "ubicacion": estantes_data.get("nombre") or f"E{m.get('id_estante')}",
                    "usuario_nombre": usuarios_data.get("nombre", "Usuario no registrado"),
                    "rut_usuario": m.get("rut_usuario", "No registrado"),
                    "observacion": m.get("observacion", ""),
                    "timestamp": m.get("timestamp", "").replace("T", " "),
                    "idproducto": m.get("idproducto"),
                    "id_estante": m.get("id_estante")
                }
                movimientos.append(mov)
                #print("Movimiento procesado:", mov)
            except Exception as e:
                print(f"Error procesando movimiento: {e}")
                continue

        print("Total movimientos a enviar:", len(movimientos))
        
        return render_template(
            "pagina/movimientos.html", 
            movimientos=movimientos
        )

    except Exception as e:
        print("Error al cargar movimientos:", str(e))
        import traceback
        print(traceback.format_exc())
        return render_template("pagina/movimientos.html", movimientos=[])


@bp.route("/api/productos")
@requiere_login
def get_productos():
    try:
        # Modificamos la consulta para usar los nombres correctos de las columnas
        response = supabase.table("productos").select(
            "idproducto, nombre, stock, peso"
        ).execute()
        
        return jsonify(response.data)
    except Exception as e:
        print("Error al obtener productos:", str(e))
        return jsonify({"error": str(e)}), 500

@bp.route("/api/estantes")
@requiere_login
def get_estantes():
    try:
        response = supabase.table("estantes").select("id_estante,nombre").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route("/api/movimientos/estadisticas/<int:idproducto>")
@requiere_login
def estadisticas_producto(idproducto):
    """Obtiene estadísticas de movimientos para un producto específico"""
    try:
        # Obtener todos los movimientos del producto
        movimientos = supabase.table("movimientos_inventario").select(
            "cantidad, tipo_evento, timestamp"
        ).eq("idproducto", idproducto).order("timestamp", desc=True).execute()
        
        # Calcular estadísticas
        total_entradas = sum(m['cantidad'] for m in movimientos.data if m['tipo_evento'] == 'Añadir')
        total_retiros = sum(m['cantidad'] for m in movimientos.data if m['tipo_evento'] == 'Retirar')
        
        # Obtener stock actual del producto
        producto = supabase.table("productos").select("stock").eq("idproducto", idproducto).execute()
        stock_actual = producto.data[0]['stock'] if producto.data else 0
        
        # Último movimiento
        ultimo_movimiento = movimientos.data[0]['timestamp'] if movimientos.data else None
        tiempo_desde_ultimo = None
        
        if ultimo_movimiento:
            desde = datetime.fromisoformat(ultimo_movimiento.replace('Z', '+00:00'))
            ahora = datetime.now(desde.tzinfo)
            diferencia = ahora - desde
            
            if diferencia.days > 0:
                tiempo_desde_ultimo = f"Hace {diferencia.days} día{'s' if diferencia.days != 1 else ''}"
            elif diferencia.seconds >= 3600:
                horas = diferencia.seconds // 3600
                tiempo_desde_ultimo = f"Hace {horas} hora{'s' if horas != 1 else ''}"
            elif diferencia.seconds >= 60:
                minutos = diferencia.seconds // 60
                tiempo_desde_ultimo = f"Hace {minutos} min"
            else:
                tiempo_desde_ultimo = "Hace unos segundos"
        
        return jsonify({
            "success": True,
            "entradas": total_entradas,
            "retiros": total_retiros,
            "stock_actual": stock_actual,
            "ultimo_movimiento": tiempo_desde_ultimo or "Sin movimientos"
        })
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@bp.route("/api/movimientos/nuevo", methods=["POST"])
@requiere_login
def nuevo_movimiento():
    try:
        datos = request.json
        print("Datos recibidos:", datos)
        
        # Validar datos requeridos
        required_fields = ['tipo_evento', 'idproducto', 'cantidad', 'peso_por_unidad']
        for field in required_fields:
            if field not in datos:
                return jsonify({
                    "success": False, 
                    "error": f"Campo requerido: {field}"
                }), 400

        # Validar que los valores numéricos sean positivos
        if datos['cantidad'] <= 0:
            return jsonify({
                "success": False,
                "error": "La cantidad debe ser mayor a 0"
            }), 400

        if datos['peso_por_unidad'] <= 0:
            return jsonify({
                "success": False,
                "error": "El peso por unidad debe ser mayor a 0"
            }), 400

        # Calcular peso_total si no viene calculado
        if 'peso_total' not in datos or datos['peso_total'] is None:
            datos['peso_total'] = datos['cantidad'] * datos['peso_por_unidad']

        # Obtener información del producto
        producto_info = supabase.table("productos").select("nombre, stock, id_estante, peso").eq("idproducto", datos["idproducto"]).execute()
        if not producto_info.data:
            return jsonify({"success": False, "error": "Producto no encontrado"}), 404
        
        producto = producto_info.data[0]
        
        # CÁLCULO AUTOMÁTICO DE ESTANTE (usando lógica existente: A, B, C...)
        if 'id_estante' not in datos or not datos['id_estante']:
            # Si no se proporciona, usar el estante actual del producto
            datos['id_estante'] = producto.get('id_estante')
            if not datos['id_estante']:
                # Si el producto no tiene estante, asignar el primer estante disponible
                estantes = supabase.table("estantes").select("id_estante").order("id_estante").limit(1).execute()
                if estantes.data:
                    datos['id_estante'] = estantes.data[0]['id_estante']
                else:
                    return jsonify({"success": False, "error": "No hay estantes disponibles"}), 400

        # Obtener el usuario de la sesión
        datos["rut_usuario"] = session.get("usuario_id")
        usuario_nombre = session.get("usuario_nombre", "Usuario")
        if not datos["rut_usuario"]:
            return jsonify({"success": False, "error": "Usuario no identificado"}), 401

        # Agregar timestamp
        datos["timestamp"] = datetime.now().isoformat()

        # Validar stock suficiente para retiros
        if datos["tipo_evento"] == "Retirar":
            if producto['stock'] < datos['cantidad']:
                return jsonify({
                    "success": False,
                    "error": f"Stock insuficiente. Disponible: {producto['stock']} unidades"
                }), 400

        # Realizar la inserción del movimiento
        response = supabase.table("movimientos_inventario").insert(datos).execute()

        # Actualizar stock del producto
        if datos["tipo_evento"] in ["Añadir", "Retirar"]:
            factor = 1 if datos["tipo_evento"] == "Añadir" else -1
            nuevo_stock = producto['stock'] + (factor * datos['cantidad'])
            
            supabase.table("productos").update({
                "stock": nuevo_stock
            }).eq("idproducto", datos["idproducto"]).execute()

        # Registrar evento en auditoría
        from app.utils.eventohumano import registrar_evento_humano
        tipo_accion = "entrada" if datos["tipo_evento"] == "Añadir" else "retiro" if datos["tipo_evento"] == "Retirar" else "movimiento"
        registrar_evento_humano(
            "movimiento_inventario",
            f"{usuario_nombre} registró {tipo_accion} de {datos['cantidad']} unidades de {producto['nombre']}"
        )

        return jsonify({
            "success": True,
            "data": response.data,
            "mensaje": "Movimiento registrado correctamente"
        })

    except Exception as e:
        print("Error en nuevo_movimiento:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
