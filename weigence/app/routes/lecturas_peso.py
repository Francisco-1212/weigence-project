"""
Rutas para procesar lecturas de peso del sensor y generar movimientos automáticos
"""
from flask import Blueprint, jsonify, request
from api.conexion_supabase import supabase
from datetime import datetime
from .decorators import requiere_autenticacion

# Crear blueprint independiente para lecturas de peso
bp = Blueprint('lecturas_peso', __name__)

@bp.route("/api/lecturas_peso/procesar", methods=["POST"])
@requiere_autenticacion
def procesar_lectura_peso():
    """
    Procesa una nueva lectura de peso y crea un movimiento automático si hay cambios significativos
    """
    try:
        datos = request.json
        id_estante = datos.get('id_estante')
        peso_leido = float(datos.get('peso_leido', 0))
        diferencia = float(datos.get('diferencia_anterior', 0))
        
        # Umbral mínimo para registrar movimiento (ignorar variaciones menores a 5g)
        UMBRAL_MINIMO = 5.0
        
        if abs(diferencia) < UMBRAL_MINIMO:
            return jsonify({
                "success": True,
                "mensaje": "Diferencia menor al umbral, no se registra movimiento",
                "diferencia": diferencia
            })
        
        # Determinar tipo de evento basado en la diferencia
        tipo_evento = "Automático"
        
        # Buscar productos en ese estante para determinar cual pudo haber cambiado
        # Por ahora, usaremos NULL en idproducto para movimientos automáticos
        # En el futuro, se podría implementar lógica para detectar qué producto cambió
        
        # Crear el movimiento automático
        movimiento_data = {
            "id_estante": id_estante,
            "tipo_evento": tipo_evento,
            "peso_total": abs(diferencia),  # Peso en kg
            "timestamp": datetime.now().isoformat(),
            "observacion": f"Movimiento automático detectado: {'+' if diferencia > 0 else ''}{diferencia:.2f}kg",
            "rut_usuario": None,  # Movimiento automático, sin usuario
            "idproducto": None,   # Por ahora, sin producto específico
            "cantidad": None,
            "peso_por_unidad": None
        }
        
        # Insertar en la base de datos
        resultado = supabase.table("movimientos_inventario").insert(movimiento_data).execute()
        
        if resultado.data:
            return jsonify({
                "success": True,
                "mensaje": "Movimiento automático registrado",
                "movimiento": resultado.data[0],
                "diferencia": diferencia
            })
        else:
            return jsonify({
                "success": False,
                "error": "No se pudo registrar el movimiento"
            }), 500
            
    except Exception as e:
        print(f"Error procesando lectura de peso: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/api/lecturas_peso/ultimas/<int:id_estante>")
@requiere_autenticacion
def obtener_ultimas_lecturas(id_estante):
    """
    Obtiene las últimas lecturas de peso de un estante
    """
    try:
        lecturas = supabase.table("lecturas_peso").select(
            "*"
        ).eq("id_estante", id_estante).order("timestamp", desc=True).limit(50).execute()
        
        return jsonify({
            "success": True,
            "lecturas": lecturas.data
        })
        
    except Exception as e:
        print(f"Error obteniendo lecturas: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/api/lecturas_peso/generar_movimientos_historicos", methods=["POST"])
@requiere_autenticacion
def generar_movimientos_historicos():
    """
    Procesa lecturas históricas y genera movimientos automáticos retroactivos
    Solo para uso administrativo
    """
    try:
        # Obtener todas las lecturas con diferencia significativa
        UMBRAL_MINIMO = 5.0
        
        lecturas = supabase.table("lecturas_peso").select(
            "*"
        ).order("timestamp", desc=False).execute()
        
        movimientos_creados = 0
        
        for lectura in lecturas.data:
            diferencia = float(lectura.get('diferencia_anterior', 0))
            
            if abs(diferencia) >= UMBRAL_MINIMO:
                # Verificar si ya existe un movimiento para esta lectura
                movimiento_existente = supabase.table("movimientos_inventario").select(
                    "id_movimiento"
                ).eq("timestamp", lectura['timestamp']).eq("tipo_evento", "Automático").execute()
                
                if not movimiento_existente.data:
                    movimiento_data = {
                        "id_estante": lectura['id_estante'],
                        "tipo_evento": "Automático",
                        "peso_total": abs(diferencia),
                        "timestamp": lectura['timestamp'],
                        "observacion": f"Movimiento automático detectado: {'+' if diferencia > 0 else ''}{diferencia:.2f}kg",
                        "rut_usuario": None,
                        "idproducto": None,
                        "cantidad": None,
                        "peso_por_unidad": None
                    }
                    
                    supabase.table("movimientos_inventario").insert(movimiento_data).execute()
                    movimientos_creados += 1
        
        return jsonify({
            "success": True,
            "mensaje": f"Se generaron {movimientos_creados} movimientos históricos",
            "total": movimientos_creados
        })
        
    except Exception as e:
        print(f"Error generando movimientos históricos: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@bp.route("/api/lecturas_peso/test", methods=["POST"])
def test_procesar_lectura():
    """
    Endpoint de testing sin autenticación para probar el procesamiento de lecturas
    SOLO PARA DESARROLLO - Remover en producción
    """
    # Llamar directamente a la función sin el decorador de autenticación
    try:
        datos = request.json
        id_estante = datos.get('id_estante')
        peso_leido = float(datos.get('peso_leido', 0))
        diferencia = float(datos.get('diferencia_anterior', 0))
        timestamp = datos.get('timestamp', datetime.now().isoformat())
        es_anomalia = datos.get('es_anomalia', False)
        
        if not id_estante or peso_leido is None:
            return jsonify({
                "success": False,
                "error": "Faltan datos requeridos: id_estante y peso_leido"
            }), 400
        
        # Umbral mínimo para considerar cambio significativo (1kg)
        UMBRAL_MINIMO = 1.0
        
        if abs(diferencia) < UMBRAL_MINIMO:
            return jsonify({
                "success": True,
                "message": "Sin cambios significativos de peso",
                "diferencia": diferencia
            })
        
        # Buscar productos en el estante
        productos_query = supabase.table("productos")\
            .select("*")\
            .eq("id_estante", id_estante)\
            .eq("estado", "activo")\
            .execute()
        
        if not productos_query.data:
            return jsonify({
                "success": False,
                "error": f"No se encontraron productos activos en estante {id_estante}"
            }), 404
        
        # Usar el primer producto encontrado
        producto = productos_query.data[0]
        peso_por_unidad = float(producto.get("peso_por_unidad", 0))
        
        if peso_por_unidad <= 0:
            return jsonify({
                "success": False,
                "error": "El producto no tiene peso_por_unidad configurado"
            }), 400
        
        # Calcular cantidad de unidades
        cantidad_unidades = int(abs(diferencia) / peso_por_unidad)
        
        if cantidad_unidades == 0:
            return jsonify({
                "success": True,
                "message": "Cambio de peso insuficiente para registrar movimiento",
                "diferencia": diferencia,
                "peso_por_unidad": peso_por_unidad
            })
        
        # Crear movimiento automático
        movimiento_data = {
            "tipo_evento": "Automático",
            "idproducto": producto["idproducto"],
            "id_estante": id_estante,
            "cantidad": cantidad_unidades,
            "peso_total": abs(diferencia),
            "peso_por_unidad": peso_por_unidad,
            "rut_usuario": "sistema",
            "observacion": f"Movimiento detectado automáticamente por sensor de peso. "
                          f"Lectura: {peso_leido}kg, Diferencia: {diferencia:+.2f}kg. "
                          f"{'[ANOMALÍA]' if es_anomalia else ''}",
            "timestamp": timestamp
        }
        
        resultado = supabase.table("movimientos_inventario").insert(movimiento_data).execute()
        
        return jsonify({
            "success": True,
            "message": "Movimiento automático registrado (TEST)",
            "movimiento_id": resultado.data[0]["id_movimiento"] if resultado.data else None,
            "tipo_movimiento": "Automático",
            "cantidad_unidades": cantidad_unidades,
            "peso_total": abs(diferencia),
            "producto": producto["nombre"],
            "estante": f"E{id_estante}"
        })
        
    except Exception as e:
        print(f"Error en test de lectura: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
