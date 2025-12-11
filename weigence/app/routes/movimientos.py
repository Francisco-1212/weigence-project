from app.data.movimiento_service import procesar_movimiento
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
            
            # Obtener lecturas recientes del estante (últimos 30 segundos)
            from datetime import datetime, timedelta
            tiempo_limite = (datetime.now() - timedelta(seconds=30)).isoformat()
            
            response = supabase.table("lecturas_peso").select("*").eq(
                "id_estante", id_estante
            ).gte("timestamp", tiempo_limite).execute()
            
            # Ordenar por timestamp descendente en Python
            if response.data:
                response.data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
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

@bp.route("/api/lecturas_peso_pendientes", methods=["POST"])
@requiere_login
def lecturas_peso_pendientes():
    """Obtiene lecturas pendientes de procesamiento (para recuperar movimientos perdidos)"""
    try:
        datos = request.json
        estantes = datos.get('estantes', [])
        minutos = datos.get('minutos', 5)
        
        if not estantes:
            return jsonify({
                "success": False,
                "error": "estantes requerido"
            }), 400
        
        from datetime import datetime, timedelta
        tiempo_limite = (datetime.now() - timedelta(minutes=minutos)).isoformat()
        
        print(f"🔍 [Pendientes] Buscando lecturas desde {tiempo_limite} en estantes: {estantes}")
        
        # Obtener lecturas relevantes de los últimos N minutos (máximo 50)
        response = supabase.table("lecturas_peso").select("*").in_(
            "id_estante", estantes
        ).gte("timestamp", tiempo_limite).order("timestamp", desc=True).limit(50).execute()
        
        if not response.data:
            return jsonify({
                "success": True,
                "lecturas": []
            })
        
        # Obtener IDs de movimientos grises ya registrados (buscar en últimos 30 días, no solo período actual)
        tiempo_busqueda = (datetime.now() - timedelta(days=30)).isoformat()
        movimientos_existentes = supabase.table("movimientos_inventario").select(
            "observacion"
        ).in_(
            "id_estante", estantes
        ).eq("tipo_evento", "gris").gte("timestamp", tiempo_busqueda).execute()
        
        print(f"🔍 [Pendientes] Verificando contra {len(movimientos_existentes.data)} movimientos grises existentes")
        
        # Extraer IDs de lecturas ya procesadas (si están en la observación)
        lecturas_procesadas = set()
        for mov in movimientos_existentes.data:
            obs = mov.get('observacion', '')
            # Intentar extraer ID de lectura de la observación si tiene formato específico
            if 'Lectura:' in obs:
                try:
                    id_lectura = int(obs.split('Lectura:')[1].split()[0].strip())
                    lecturas_procesadas.add(id_lectura)
                except:
                    pass
        
        # Agrupar por estante y obtener solo la ÚLTIMA lectura relevante de cada uno
        lecturas_por_estante = {}
        for lectura in response.data:
            id_estante = lectura.get('id_estante')
            id_lectura = lectura.get('id_lectura')
            diferencia_original = float(lectura.get('diferencia_anterior', 0))
            diferencia_abs = abs(diferencia_original)
            timestamp = lectura.get('timestamp', '')
            
            # Si tiene diferencia >= 15g (absoluto) y no está procesada
            if diferencia_abs >= 15 and id_lectura not in lecturas_procesadas:
                # Solo guardar si es la primera del estante (más reciente por el order desc)
                if id_estante not in lecturas_por_estante:
                    lecturas_por_estante[id_estante] = lectura
                    print(f"   📌 Estante {id_estante}: Lectura {id_lectura} ({diferencia_original:+.1f}g)")
        
        lecturas_pendientes = list(lecturas_por_estante.values())
        
        print(f"📋 [Pendientes] {len(lecturas_pendientes)} lecturas pendientes (1 por estante) de {len(response.data)} totales")
        
        return jsonify({
            "success": True,
            "lecturas": lecturas_pendientes
        })
        
    except Exception as e:
        print(f"❌ [Pendientes] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

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
        from datetime import datetime, timedelta
        
        datos = request.json
        print("📝 [Movimiento Gris] Datos recibidos:", datos)
        
        # Validar campos requeridos
        if not datos.get('id_estante'):
            return jsonify({"success": False, "error": "id_estante requerido"}), 400
        
        id_estante = datos['id_estante']
        peso_nuevo = datos.get('peso_total', 0)
        timestamp_actual = datetime.now()
        
        # Intentar identificar producto por peso PRIMERO (necesario para buscar VentaPendiente)
        from app.data.movimiento_service import procesar_movimiento
        resultado_deteccion = procesar_movimiento(
            id_estante,
            peso_nuevo,
            'gris',
            timestamp_actual,
            None
        )
        
        # Enriquecer datos con detección de producto
        datos_enriquecidos = datos.copy()
        if resultado_deteccion.get('idproducto'):
            datos_enriquecidos['idproducto'] = resultado_deteccion.get('idproducto')
            datos_enriquecidos['idproducto_detectado'] = resultado_deteccion.get('idproducto_detectado')
            print(f"🔍 [Movimiento Gris] Producto detectado: {resultado_deteccion.get('idproducto')}")
        
        # PRIMERO: Intentar actualizar un movimiento VentaPendiente existente
        # Si se detecta un retiro de peso, puede corresponder a una venta pendiente
        print(f"🔍 [Movimiento Gris] Buscando VentaPendiente antes de crear gris...")
        movimiento_actualizado = actualizar_movimiento_pendiente_o_gris(
            id_estante,
            peso_nuevo,
            timestamp_actual,
            datos_enriquecidos,  # Usar datos enriquecidos con detección
            es_desde_sensor=True  # Indica que viene del sensor
        )
        
        if movimiento_actualizado:
            print(f"✅ [Movimiento Gris] VentaPendiente encontrado y actualizado: {movimiento_actualizado.get('id_movimiento')}")
            return jsonify({
                "success": True,
                "data": movimiento_actualizado,
                "mensaje": "Venta pendiente confirmada con sensor"
            })
        
        print(f"ℹ️ [Movimiento Gris] No hay VentaPendiente, creando movimiento gris...")
        
        # Extraer ID de lectura de la observación (si existe)
        observacion = datos.get('observacion', '')
        id_lectura_actual = None
        if '[Lectura:' in observacion:
            try:
                id_lectura_actual = int(observacion.split('[Lectura:')[1].split(']')[0].strip())
                print(f"🔍 [Movimiento Gris] ID Lectura extraído: {id_lectura_actual}")
            except Exception as e:
                print(f"⚠️ [Movimiento Gris] Error extrayendo ID lectura: {e}")
                pass
        else:
            print(f"⚠️ [Movimiento Gris] Observación sin ID lectura: '{observacion}'")
        
        # Verificar si ya existe un movimiento con esta lectura
        if id_lectura_actual:
            # Buscar en los últimos 5 minutos de movimientos grises
            tiempo_limite = (datetime.now() - timedelta(minutes=5)).isoformat()
            
            movimientos_existentes = supabase.table("movimientos_inventario").select(
                "id_movimiento, observacion, timestamp"
            ).eq("id_estante", id_estante).eq("tipo_evento", "gris").gte(
                "timestamp", tiempo_limite
            ).execute()
            
            print(f"🔍 [Movimiento Gris] Verificando {len(movimientos_existentes.data)} movimientos recientes")
            
            for mov in movimientos_existentes.data:
                obs = mov.get('observacion', '')
                if f'[Lectura: {id_lectura_actual}]' in obs:
                    print(f"❌ [Movimiento Gris] DUPLICADO detectado - Lectura {id_lectura_actual} ya en movimiento {mov.get('id_movimiento')}")
                    return jsonify({
                        "success": True,
                        "data": None,
                        "mensaje": f"Movimiento ya registrado (lectura {id_lectura_actual} duplicada)"
                    })
            
            print(f"✅ [Movimiento Gris] Lectura {id_lectura_actual} no encontrada en duplicados, procediendo...")
        
        # PRIORIZAR datos del frontend sobre detección automática
        # La cantidad del frontend indica correctamente si es adición (+1) o retiro (-1)
        cantidad = datos.get('cantidad', 1)
        if cantidad is None:
            cantidad = resultado_deteccion.get('cantidad', 1)
            print(f"⚠️ [Movimiento Gris] Usando cantidad de detección: {cantidad}")
        
        # La observación del frontend incluye [Lectura: ID] para evitar duplicados
        observacion_final = datos.get('observacion', '')
        if not observacion_final or observacion_final == '':
            observacion_final = resultado_deteccion.get('observacion', 'Detección automática: Peso estable sin identificación')
        
        movimiento_gris = {
            "id_estante": id_estante,
            "idproducto": resultado_deteccion.get("idproducto"),
            "idproducto_detectado": resultado_deteccion.get("idproducto_detectado"),
            "rut_usuario": None,  # NULL = Sistema automático
            "cantidad": cantidad,  # Del frontend: +1 (adición) o -1 (retiro)
            "tipo_evento": 'gris',
            "peso_total": peso_nuevo,
            "peso_por_unidad": datos.get('peso_por_unidad') or resultado_deteccion.get('peso_por_unidad') or peso_nuevo,
            "timestamp": timestamp_actual.isoformat(),
            "match_por_peso": resultado_deteccion.get("match_por_peso"),
            "es_venta_validada": resultado_deteccion.get("es_venta_validada"),
            "es_retiro_sospechoso": resultado_deteccion.get("es_retiro_sospechoso"),
            "motivo_sospecha": resultado_deteccion.get("motivo_sospecha"),
            "observacion": observacion_final  # Del frontend con [Lectura: ID]
        }

        print(f"💾 [Movimiento Gris] Valores finales:")
        print(f"   - cantidad: {cantidad} (frontend: {datos.get('cantidad')}, detección: {resultado_deteccion.get('cantidad')})")
        print(f"   - observacion: '{observacion_final}'")
        print(f"   - peso_total: {peso_nuevo} kg")

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

def actualizar_movimiento_pendiente_o_gris(id_estante, peso_total, timestamp_retiro, datos_retiro, es_desde_sensor=False):
    """
    Busca movimientos pendientes o grises que coincidan con un retiro y los actualiza.
    
    Escenarios:
    1. Si es desde sensor (gris): Busca VentaPendiente y la completa
    2. Si es venta manual: Busca movimiento gris y lo actualiza
    
    Args:
        id_estante: ID del estante
        peso_total: Peso del retiro
        timestamp_retiro: Timestamp del retiro
        datos_retiro: Diccionario con los datos del retiro
        es_desde_sensor: True si el retiro viene del sensor de peso
        
    Returns:
        bool: True si se actualizó un movimiento, False si no
    """
    try:
        from datetime import timedelta
        
        # Buscar VentaPendiente en los últimos 30 minutos, movimientos grises en 5 minutos
        minutos_busqueda = 30 if es_desde_sensor else 5
        tiempo_limite = (timestamp_retiro - timedelta(minutes=minutos_busqueda)).isoformat()
        tiempo_futuro = (timestamp_retiro + timedelta(seconds=30)).isoformat()
        
        if es_desde_sensor:
            # CASO 1: Sensor detectó retiro → Buscar VentaPendiente
            cantidad_retiro = abs(datos_retiro.get('cantidad', 0))
            idproducto_retiro = datos_retiro.get('idproducto')
            print(f"🔍 [Actualizar Pendiente] Buscando VentaPendiente en estante {id_estante}")
            print(f"   Rango: últimos 30 minutos")
            print(f"   Retiro detectado: {cantidad_retiro} unidad(es), Producto: {idproducto_retiro}, Peso: {abs(peso_total)*1000:.0f}g")
            
            tipo_busqueda = "VentaPendiente"
        else:
            # CASO 2: Venta manual → Buscar movimiento gris del sensor
            print(f"🔍 [Actualizar Gris] Buscando movimientos grises en estante {id_estante}")
            print(f"   Rango: {tiempo_limite} a {tiempo_futuro}")
            print(f"   Peso venta: {peso_total} kg")
            
            tipo_busqueda = "gris"
        
        # Buscar movimientos según el tipo
        movimientos_encontrados = supabase.table("movimientos_inventario").select(
            "id_movimiento, peso_total, timestamp, observacion, cantidad, idproducto, tipo_evento"
        ).eq("id_estante", id_estante).eq("tipo_evento", tipo_busqueda).gte(
            "timestamp", tiempo_limite
        ).lte("timestamp", tiempo_futuro).execute()
        
        if not movimientos_encontrados.data:
            print(f"⚠️ [Actualizar] No se encontraron movimientos {tipo_busqueda} recientes")
            return False
        
        print(f"📋 [Actualizar] Encontrados {len(movimientos_encontrados.data)} movimientos {tipo_busqueda}")
        
        # Buscar el que mejor coincida con el peso y producto
        TOLERANCIA_PESO = 0.01  # 10 gramos de tolerancia
        mejor_coincidencia = None
        min_diferencia = float('inf')
        
        for mov in movimientos_encontrados.data:
            peso_mov = float(mov.get('peso_total', 0))
            cantidad_mov = mov.get('cantidad', 0)
            idproducto_mov = mov.get('idproducto')
            diferencia_peso = abs(peso_mov - abs(peso_total))
            
            # Si es VentaPendiente, verificar compatibilidad
            if tipo_busqueda == "VentaPendiente":
                idproducto_retiro = datos_retiro.get('idproducto')
                cantidad_retiro = abs(datos_retiro.get('cantidad', 0))
                cantidad_venta = abs(cantidad_mov)
                
                # 1. Verificar que el producto coincida
                if idproducto_mov and idproducto_retiro and idproducto_mov != idproducto_retiro:
                    print(f"   ⏭️ Mov {mov['id_movimiento']}: Producto no coincide ({idproducto_mov} vs {idproducto_retiro})")
                    continue
                
                # 2. Verificar que las cantidades coincidan (unidades vendidas = unidades retiradas)
                if cantidad_venta != cantidad_retiro:
                    print(f"   ⏭️ Mov {mov['id_movimiento']}: Cantidad no coincide (Venta: {cantidad_venta} vs Retiro: {cantidad_retiro})")
                    continue
                
                print(f"   ✓ Mov {mov['id_movimiento']}: Producto y cantidad coinciden (ID:{idproducto_retiro}, Unidades:{cantidad_venta})")
            
            # Verificar tipo (retiro)
            es_retiro_mov = cantidad_mov < 0
            es_retiro_dato = datos_retiro.get('cantidad', 0) < 0
            
            if es_retiro_mov == es_retiro_dato and diferencia_peso < min_diferencia:
                min_diferencia = diferencia_peso
                mejor_coincidencia = mov
                print(f"   🎯 Candidato: Mov {mov['id_movimiento']} - Diff peso: {diferencia_peso*1000:.1f}g, Unidades: {abs(cantidad_mov)}")
        
        if mejor_coincidencia and min_diferencia <= TOLERANCIA_PESO:
            id_mov = mejor_coincidencia['id_movimiento']
            tipo_original = mejor_coincidencia['tipo_evento']
            
            if tipo_busqueda == "VentaPendiente":
                # CASO 1: Completar VentaPendiente con datos del sensor
                print(f"✅ [Completar Venta] Actualizando VentaPendiente {id_mov} con datos del sensor")
                
                observacion_original = mejor_coincidencia.get('observacion', '')
                idproducto_detectado = datos_retiro.get('idproducto_detectado')
                
                # Preparar datos de actualización preservando información de venta
                cantidad_unidades = abs(mejor_coincidencia.get('cantidad', 0))
                update_data = {
                    "tipo_evento": "Retirar",  # Cambiar de VentaPendiente a Retirar
                    "es_venta_validada": True,
                    "match_por_peso": True,
                    "peso_total": peso_total,  # Actualizar con peso real del sensor
                    "timestamp": timestamp_retiro.isoformat(),  # Timestamp del retiro sensor
                    "observacion": observacion_original + f" [Retiro confirmado: {cantidad_unidades} unidad(es) - {abs(peso_total)*1000:.0f}g a {timestamp_retiro.strftime('%H:%M:%S')}]"
                }
                
                # Si el sensor detectó el producto, actualizar
                if idproducto_detectado:
                    update_data["idproducto_detectado"] = idproducto_detectado
                    update_data["observacion"] += f" [Producto confirmado: {idproducto_detectado}]"
                
                mensaje_auditoria = f"VentaPendiente {id_mov} completada con retiro del sensor en estante {id_estante} a {timestamp_retiro.strftime('%H:%M:%S')}"
                
            else:
                # CASO 2: Actualizar movimiento gris con venta manual
                print(f"✅ [Actualizar Gris] Actualizando movimiento gris {id_mov} con venta validada")
                
                update_data = {
                    "tipo_evento": datos_retiro.get("tipo_evento", "Retirar"),
                    "idproducto": datos_retiro.get("idproducto"),
                    "idproducto_detectado": datos_retiro.get("idproducto_detectado"),
                    "rut_usuario": datos_retiro.get("rut_usuario"),
                    "cantidad": datos_retiro.get("cantidad"),
                    "peso_por_unidad": datos_retiro.get("peso_por_unidad"),
                    "match_por_peso": datos_retiro.get("match_por_peso"),
                    "es_venta_validada": True,
                    "es_retiro_sospechoso": False,
                    "motivo_sospecha": None,
                    "observacion": datos_retiro.get("observacion", "") + " [Actualizado desde movimiento gris]"
                }
                
                mensaje_auditoria = f"Movimiento gris {id_mov} actualizado a venta validada en estante {id_estante}"
            
            # Actualizar en la base de datos
            supabase.table("movimientos_inventario").update(update_data).eq(
                "id_movimiento", id_mov
            ).execute()
            
            print(f"✅ [Actualizar] Movimiento {id_mov} actualizado correctamente")
            
            # Registrar en auditoría
            from app.utils.eventohumano import registrar_evento_humano
            registrar_evento_humano("movimiento_actualizado", mensaje_auditoria)
            
            return True
        else:
            print(f"⚠️ [Actualizar] No se encontró coincidencia (mejor diff: {min_diferencia*1000:.1f}g)")
            return False
            
    except Exception as e:
        print(f"❌ [Actualizar Gris] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

@bp.route("/api/movimientos/nuevo", methods=["POST"])
@requiere_login
def nuevo_movimiento():
    try:
        datos_req = request.json
        print("Datos recibidos:", datos_req)

        # Obtener datos requeridos del sensor
        id_estante = datos_req.get('id_estante')
        peso_total = datos_req.get('peso_total')
        tipo_evento = datos_req.get('tipo_evento')
        timestamp = datos_req.get('timestamp')
        rut_usuario = datos_req.get('rut_usuario') or session.get("usuario_id")
        usuario_nombre = session.get("usuario_nombre", "Usuario")

        # Validar campos mínimos
        if id_estante is None or peso_total is None or tipo_evento is None or timestamp is None:
            return jsonify({
                "success": False,
                "error": "Faltan campos requeridos: id_estante, peso_total, tipo_evento, timestamp"
            }), 400

        # Convertir timestamp a datetime si es string
        if isinstance(timestamp, str):
            try:
                timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except Exception:
                timestamp_dt = datetime.now()
        else:
            timestamp_dt = timestamp

        # Llamar a la lógica central
        datos = procesar_movimiento(id_estante, peso_total, tipo_evento, timestamp_dt, rut_usuario)

        # Preparar datos para inserción
        movimiento_db = {
            "id_estante": id_estante,
            "idproducto": datos.get("idproducto"),
            "idproducto_detectado": datos.get("idproducto_detectado"),
            "cantidad": datos.get("cantidad"),
            "peso_por_unidad": datos.get("peso_por_unidad"),
            "peso_total": peso_total,
            "tipo_evento": tipo_evento,
            "timestamp": timestamp_dt.isoformat(),
            "rut_usuario": rut_usuario,
            "match_por_peso": datos.get("match_por_peso"),
            "es_venta_validada": datos.get("es_venta_validada"),
            "es_retiro_sospechoso": datos.get("es_retiro_sospechoso"),
            "motivo_sospecha": datos.get("motivo_sospecha"),
            "observacion": datos.get("observacion")
        }

        # ANTES de insertar, verificar si hay movimientos pendientes o grises que coincidan
        movimiento_actualizado = False
        if tipo_evento == "Retirar" and datos.get("es_venta_validada"):
            # Venta manual → Buscar movimiento gris del sensor
            movimiento_actualizado = actualizar_movimiento_pendiente_o_gris(
                id_estante, 
                peso_total, 
                timestamp_dt, 
                movimiento_db,
                es_desde_sensor=False
            )
        
        # Si NO se actualizó un movimiento, insertar uno nuevo
        if not movimiento_actualizado:
            response = supabase.table("movimientos_inventario").insert(movimiento_db).execute()
            mensaje_respuesta = "Movimiento registrado correctamente"
        else:
            # Si se actualizó, retornar mensaje
            response = type('obj', (object,), {'data': [{'actualizado': True}]})()
            mensaje_respuesta = "Movimiento pendiente/gris actualizado con datos de venta"
            print(f"🔄 [Venta] Movimiento actualizado en lugar de crear duplicado")

        # Si es retiro sospechoso, insertar alerta automáticamente
        if datos.get("es_retiro_sospechoso"):
            descripcion = f"Retiro sospechoso detectado en estante {id_estante}. Observación: {datos.get('observacion', '')}"
            supabase.table("alertas").insert({
                "titulo": "Retiro sospechoso",
                "descripcion": descripcion,
                "icono": "alert-triangle",
                "tipo_color": "warning",
                "idproducto": datos.get("idproducto"),
                "idusuario": rut_usuario
            }).execute()

        # Mantener respuesta compatible
        return jsonify({
            "success": True,
            "data": response.data,
            "mensaje": mensaje_respuesta
        })

    except Exception as e:
        print("Error en nuevo_movimiento:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
