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
@requiere_rol('operador', 'supervisor', 'administrador')
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
            .limit(100)  # Aumentado para historial completo
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
                
                # Si rut_usuario es NULL, es un movimiento automático del sistema
                rut_usuario = m.get("rut_usuario")
                if rut_usuario is None:
                    usuario_nombre = "Sistema"
                    rut_display = "Automático"
                else:
                    usuario_nombre = usuarios_data.get("nombre", "Usuario no registrado")
                    rut_display = rut_usuario or "No registrado"
                
                mov = {
                    "id_movimiento": m.get("id_movimiento"),
                    "producto": productos_data.get("nombre", "Producto no encontrado"),
                    "tipo_evento": m.get("tipo_evento"),
                    "cantidad": m.get("cantidad", 0),
                    "peso_por_unidad": m.get("peso_por_unidad", 0),
                    "peso_total": m.get("peso_total", 0),
                    "ubicacion": estantes_data.get("nombre") or f"E{m.get('id_estante')}",
                    "usuario_nombre": usuario_nombre,
                    "rut_usuario": rut_display,
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
        # Modificamos la consulta para incluir id_estante
        response = supabase.table("productos").select(
            "idproducto, nombre, stock, peso, id_estante"
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

@bp.route("/api/lecturas_peso_recientes", methods=["POST"])
@requiere_login
def lecturas_peso_recientes():
    """Obtiene lecturas de peso recientes para un estante con retry automático"""
    import time
    from httpx import ReadError
    from httpcore import ReadError as HttpcoreReadError
    
    datos = request.json
    id_estante = datos.get('id_estante')
    
    if not id_estante:
        return jsonify({
            "success": False,
            "error": "id_estante requerido"
        }), 400
    
    # Configuración de reintentos
    max_intentos = 3
    retraso_base = 0.5  # segundos
    
    for intento in range(max_intentos):
        try:
            if intento > 0:
                retraso = retraso_base * (2 ** intento)  # Exponential backoff
                print(f"🔄 [RETRY] Intento {intento + 1}/{max_intentos} tras {retraso}s...")
                time.sleep(retraso)
            
            # Obtener lecturas del estante
            response = supabase.table("lecturas_peso").select("*").eq("id_estante", id_estante).execute()
            
            # Ordenar por id_lectura descendente en Python
            if response.data:
                response.data.sort(key=lambda x: x.get('id_lectura', 0), reverse=True)
                response.data = response.data[:10]  # Solo las últimas 10
            
            # Éxito - retornar inmediatamente
            return jsonify({
                "success": True,
                "data": response.data
            })
        
        except (ReadError, HttpcoreReadError) as e:
            # Error de socket - reintentar
            if intento < max_intentos - 1:
                print(f"⚠️ [SOCKET] Error WinError 10035 en intento {intento + 1}, reintentando...")
                continue
            else:
                # Último intento fallido - retornar lista vacía en lugar de error
                print(f"❌ [SOCKET] Todos los intentos fallaron para estante {id_estante}")
                return jsonify({
                    "success": True,
                    "data": [],
                    "warning": "Timeout de conexión, reintentando en próxima consulta"
                })
        
        except Exception as e:
            print(f"❌ [LECTURAS] Error inesperado: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    # Fallback (no debería llegar aquí)
    return jsonify({
        "success": True,
        "data": []
    })

@bp.route("/api/movimientos/ultimo/<int:id_estante>")
@requiere_login
def ultimo_movimiento_estante(id_estante):
    """Obtiene el último movimiento registrado para un estante"""
    try:
        response = supabase.table("movimientos_inventario").select(
            "id_movimiento, tipo_evento, peso_total, timestamp"
        ).eq("id_estante", id_estante).order("timestamp", desc=True).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            return jsonify({
                "success": True,
                "data": response.data[0]
            })
        else:
            return jsonify({
                "success": True,
                "data": None
            })
        
    except Exception as e:
        print(f"Error obteniendo último movimiento: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/movimientos/gris", methods=["POST"])
@requiere_login
def crear_movimiento_gris():
    """Crea un movimiento 'gris' automático del sistema"""
    try:
        datos = request.json
        print("📝 [Movimiento Gris] Datos recibidos:", datos)
        
        # Validar campos requeridos
        if not datos.get('id_estante'):
            return jsonify({"success": False, "error": "id_estante requerido"}), 400
        
        id_estante = datos['id_estante']
        peso_nuevo = datos.get('peso_total', 0)
        
        # Verificar el último movimiento gris en este estante
        ultimo_mov = supabase.table("movimientos_inventario").select(
            "peso_total, timestamp"
        ).eq("id_estante", id_estante).eq("tipo_evento", "gris").order(
            "timestamp", desc=True
        ).limit(1).execute()
        
        # Si existe un movimiento reciente con peso similar, no crear duplicado
        if ultimo_mov.data:
            ultimo_peso = ultimo_mov.data[0].get('peso_total', 0)
            diferencia_peso = abs(peso_nuevo - ultimo_peso)
            
            # Si la diferencia es menor a 0.02 kg (20g), es considerado duplicado
            UMBRAL_DUPLICADO = 0.02  # kg
            if diferencia_peso < UMBRAL_DUPLICADO:
                print(f"⚠️ [Movimiento Gris] Duplicado detectado - Estante {id_estante}: {peso_nuevo}kg vs {ultimo_peso}kg (Δ={diferencia_peso*1000:.1f}g)")
                return jsonify({
                    "success": True,
                    "data": None,
                    "mensaje": "Movimiento similar ya registrado, omitiendo duplicado"
                })
        
        # Preparar datos del movimiento gris (rut_usuario NULL = Sistema automático)
        movimiento_gris = {
            "id_estante": id_estante,
            "idproducto": None,  # No identificado
            "rut_usuario": None,  # NULL = Sistema automático
            "cantidad": datos.get('cantidad', 0),
            "tipo_evento": 'gris',
            "peso_total": peso_nuevo,
            "peso_por_unidad": datos.get('peso_por_unidad', peso_nuevo),
            "timestamp": datetime.now().isoformat(),
            "observacion": datos.get('observacion', 'Detección automática: Peso estable sin identificación')
        }
        
        print(f"💾 [Movimiento Gris] Insertando:", movimiento_gris)
        
        # Insertar en la base de datos
        response = supabase.table("movimientos_inventario").insert(movimiento_gris).execute()
        
        if response.data:
            print(f"✅ [Movimiento Gris] Registrado: {response.data[0].get('id_movimiento')}")
            
            # Registrar evento en auditoría
            from app.utils.eventohumano import registrar_evento_humano
            registrar_evento_humano(
                "movimiento_gris",
                f"Sistema detectó peso estable no identificado en estante {datos['id_estante']}: {datos.get('peso_total', 0):.2f}kg"
            )
            
            return jsonify({
                "success": True,
                "data": response.data[0],
                "mensaje": "Movimiento gris registrado correctamente"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo registrar el movimiento"
            }), 500
        
    except Exception as e:
        print(f"❌ [Movimiento Gris] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route("/api/movimientos/nuevo", methods=["POST"])
@requiere_login
def nuevo_movimiento():
    try:
        datos = request.json
        print("Datos recibidos:", datos)
        
        # Validar datos requeridos
        required_fields = ['tipo_evento', 'idproducto', 'cantidad', 'peso_por_unidad', 'id_estante']
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
        
        # Validar que el estante seleccionado existe
        if not datos.get('id_estante'):
            return jsonify({
                "success": False,
                "error": "Debe seleccionar un estante"
            }), 400
        
        # Verificar que el estante existe en la base de datos
        estante_info = supabase.table("estantes").select("id_estante, nombre").eq("id_estante", datos['id_estante']).execute()
        if not estante_info.data:
            return jsonify({
                "success": False,
                "error": "El estante seleccionado no existe"
            }), 404

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
