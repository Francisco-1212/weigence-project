

import logging
from math import floor
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from api.conexion_supabase import supabase

# Tolerancia estándar para el match de peso (en kg)
TOLERANCIA_PESO = 0.005  # 5 gramos - más estricto para evitar falsos positivos

def procesar_movimiento(
	id_estante: int,
	peso_total: float,
	tipo_evento: str,
	timestamp: datetime,
	rut_usuario: Optional[str] = None
) -> Dict[str, Any]:
	"""
	Procesa un movimiento de inventario, identificando producto por peso, validando venta y marcando sospechas.
	"""
	try:
		# 1. Cálculo inicial
		peso_retirado = abs(peso_total)
		logging.info(f"[MOVIMIENTO] Peso recibido: {peso_total} kg | Peso retirado abs: {peso_retirado} kg | Estante: {id_estante}")
		# 2. Traer todos los productos del estante
		productos_resp = supabase.table("productos").select("*").eq("id_estante", id_estante).execute()
		productos = productos_resp.data if hasattr(productos_resp, 'data') else productos_resp.get('data', [])
		if not productos:
			logging.warning(f"No hay productos para el estante {id_estante}")
			return {
				"idproducto": None,
				"idproducto_detectado": None,
				"cantidad": None,
				"peso_por_unidad": None,
				"match_por_peso": False,
				"es_venta_validada": False,
				"es_retiro_sospechoso": False,
				"motivo_sospecha": "No hay productos en estante",
				"observacion": "No se detectó producto por peso"
			}
		# 3. Determinar peso_ref para cada producto
		mejor_match = None
		min_diff = float('inf')
		peso_ref_elegido = None
		idproducto_detectado = None
		for prod in productos:
			idprod = prod["idproducto"]
			# Buscar último pesaje
			pesaje_resp = supabase.table("pesajes").select("peso_unitario").eq("idproducto", idprod).order("fecha_pesaje", desc=True).limit(1).execute()
			pesaje = pesaje_resp.data[0]["peso_unitario"] if pesaje_resp.data else prod.get("peso")
			# Conversión automática de gramos a kilogramos si el valor es mayor a 10
			peso_ref = pesaje / 1000 if pesaje and pesaje > 10 else pesaje
			diff = abs(peso_retirado - peso_ref)
			logging.info(f"[PRODUCTO] id: {idprod} | peso_ref: {peso_ref} kg | diff: {diff} kg | nombre: {prod.get('descripcion','')} | tolerancia: {TOLERANCIA_PESO}")
			if diff < min_diff:
				min_diff = diff
				mejor_match = prod
				peso_ref_elegido = peso_ref
				idproducto_detectado = idprod
		# 4. Identificar producto usando mínima diferencia
		if mejor_match is not None and min_diff <= TOLERANCIA_PESO:
			logging.info(f"[MATCH] Producto detectado: {mejor_match.get('descripcion','')} | id: {idproducto_detectado} | peso_ref: {peso_ref_elegido} | diff: {min_diff}")
		else:
			# Si la diferencia es mayor a la tolerancia, registramos como movimiento no identificado
			if mejor_match is not None:
				logging.warning(f"[NO MATCH] Peso detectado ({peso_retirado} kg) no coincide con ningún producto. Producto más cercano: {mejor_match.get('descripcion','')} | peso_ref: {peso_ref_elegido} | diff: {min_diff} kg (tolerancia: {TOLERANCIA_PESO} kg)")
			else:
				logging.warning(f"[NO MATCH] No hay productos en el estante para comparar")
			
			# No hay match por peso - devolver sin producto asociado
			# Crear motivo conciso con información del producto más cercano
			if mejor_match:
				nombre_prod = mejor_match.get('nombre') or mejor_match.get('descripcion', 'N/A')
				motivo = f"Peso detectado ({peso_retirado:.3f} kg) no coincide con ningún producto registrado. Producto más cercano: {nombre_prod} ({peso_ref_elegido:.3f} kg, diff: {min_diff:.3f} kg)"
			else:
				motivo = "No se encontró producto con peso coincidente"
			
			return {
				"idproducto": None,
				"idproducto_detectado": None,
				"cantidad": None,
				"peso_por_unidad": None,
				"match_por_peso": False,
				"es_venta_validada": False,
				"es_retiro_sospechoso": False,
				"motivo_sospecha": motivo,
				"observacion": "Producto no identificado - peso fuera de tolerancia"
			}
		# 5. Calcular cantidad con redondeo hacia abajo
		cantidad_abs = floor(peso_retirado / peso_ref_elegido) if peso_ref_elegido else 1
		if cantidad_abs < 1:
			cantidad_abs = 1
		signo = -1 if peso_total < 0 else 1
		cantidad = signo * cantidad_abs
		# 6. Validar venta si es retiro
		es_venta_validada = False
		es_retiro_sospechoso = False
		motivo_sospecha = None
		if peso_total < 0:
			# Buscar ventas en ventana ±30 minutos
			ventana_ini = (timestamp - timedelta(minutes=30)).isoformat()
			ventana_fin = (timestamp + timedelta(minutes=30)).isoformat()
			# Buscar venta pendiente en movimientos_inventario
			venta_pendiente = supabase.table("movimientos_inventario").select("id_movimiento, cantidad, timestamp, tipo_evento").eq("idproducto", idproducto_detectado).eq("tipo_evento", "VentaPendiente").gte("timestamp", ventana_ini).lte("timestamp", ventana_fin).execute().data
			if venta_pendiente:
				# Emparejar: actualizar venta pendiente como validada
				for venta in venta_pendiente:
					supabase.table("movimientos_inventario").update({
						"tipo_evento": "Retirar",
						"es_venta_validada": True,
						"motivo_sospecha": None,
						"observacion": "Emparejado con retiro"
					}).eq("id_movimiento", venta["id_movimiento"]).execute()
				es_venta_validada = True
				es_retiro_sospechoso = False
				motivo_sospecha = None
			else:
				# Si no hay venta pendiente, buscar en detalle_ventas (flujo original)
				ventas_resp = supabase.table("detalle_ventas").select("cantidad,fecha_detalle,idventa").eq("idproducto", idproducto_detectado)
				ventas_resp = ventas_resp.gte("fecha_detalle", ventana_ini).lte("fecha_detalle", ventana_fin).execute()
				detalles = ventas_resp.data if hasattr(ventas_resp, 'data') else ventas_resp.get('data', [])
				sum_cant_venta = sum([d["cantidad"] for d in detalles]) if detalles else 0
				if sum_cant_venta >= abs(cantidad):
					es_venta_validada = True
					es_retiro_sospechoso = False
				else:
					es_venta_validada = False
					es_retiro_sospechoso = True
					motivo_sospecha = "Retiro sin venta registrada en ventana ±30min"
		# 7. Preparar observacion
		if peso_total < 0:
			obs = "RETIRO automático: detectado por peso"
		else:
			obs = "ADICIÓN automática: detectado por peso"
		return {
			"idproducto": idproducto_detectado,
			"idproducto_detectado": idproducto_detectado,
			"cantidad": cantidad,
			"peso_por_unidad": peso_ref_elegido,
			"match_por_peso": True,
			"es_venta_validada": es_venta_validada,
			"es_retiro_sospechoso": es_retiro_sospechoso,
			"motivo_sospecha": motivo_sospecha,
			"observacion": obs
		}
	except Exception as e:
		logging.exception(f"Error en procesar_movimiento: {e}")
		return {
			"idproducto": None,
			"idproducto_detectado": None,
			"cantidad": None,
			"peso_por_unidad": None,
			"match_por_peso": False,
			"es_venta_validada": False,
			"es_retiro_sospechoso": False,
			"motivo_sospecha": f"Error: {str(e)}",
			"observacion": "Error al procesar movimiento"
		}
		# 5. Calcular cantidad con redondeo hacia abajo
		cantidad_abs = floor(peso_retirado / peso_ref_elegido) if peso_ref_elegido else 1
		if cantidad_abs < 1:
			cantidad_abs = 1
		signo = -1 if peso_total < 0 else 1
		cantidad = signo * cantidad_abs
		# 6. Validar venta si es retiro
		es_venta_validada = False
		es_retiro_sospechoso = False
		motivo_sospecha = None
		if peso_total < 0:
			# Buscar ventas en ventana ±30 minutos
			ventana_ini = (timestamp - timedelta(minutes=30)).isoformat()
			ventana_fin = (timestamp + timedelta(minutes=30)).isoformat()
			ventas_query = (
				supabase.rpc(
					"detalle_ventas_en_ventana",
					{
						"idproducto": idproducto_detectado,
						"ventana_ini": ventana_ini,
						"ventana_fin": ventana_fin
					}
				)
			)
			# Si no existe la función RPC, usar consulta directa:
			ventas_resp = supabase.table("detalle_ventas").select("cantidad,fecha_detalle,idventa").eq("idproducto", idproducto_detectado)
			ventas_resp = ventas_resp.gte("fecha_detalle", ventana_ini).lte("fecha_detalle", ventana_fin).execute()
			detalles = ventas_resp.data if hasattr(ventas_resp, 'data') else ventas_resp.get('data', [])
			sum_cant_venta = sum([d["cantidad"] for d in detalles]) if detalles else 0
			if sum_cant_venta >= abs(cantidad):
				es_venta_validada = True
				es_retiro_sospechoso = False
			else:
				es_venta_validada = False
				es_retiro_sospechoso = True
				motivo_sospecha = "Retiro sin venta registrada en ventana ±30min"
		# 7. Preparar observacion
		if peso_total < 0:
			obs = "RETIRO automático: detectado por peso"
		else:
			obs = "ADICIÓN automática: detectado por peso"
		return {
			"idproducto": idproducto_detectado,
			"idproducto_detectado": idproducto_detectado,
			"cantidad": cantidad,
			"peso_por_unidad": peso_ref_elegido,
			"match_por_peso": True,
			"es_venta_validada": es_venta_validada,
			"es_retiro_sospechoso": es_retiro_sospechoso,
			"motivo_sospecha": motivo_sospecha,
			"observacion": obs
		}
	except Exception as e:
		logging.exception(f"Error en procesar_movimiento: {e}")
		return {
			"idproducto": None,
			"idproducto_detectado": None,
			"cantidad": None,
			"peso_por_unidad": None,
			"match_por_peso": False,
			"es_venta_validada": False,
			"es_retiro_sospechoso": False,
			"motivo_sospecha": f"Error: {str(e)}",
			"observacion": "Error al procesar movimiento"
		}


# NUEVA FUNCIÓN: registrar movimiento de inventario justificado por venta
def registrar_movimiento_por_venta(id_estante: int, idproducto: int, cantidad: int, peso_por_unidad: float, rut_usuario: str, timestamp: datetime = None):
    """
    Registra un movimiento de inventario por venta, usando la lógica de procesar_movimiento para validación cruzada.
    """
    if timestamp is None:
        timestamp = datetime.now()
    peso_total = -abs(cantidad * peso_por_unidad)
    datos = procesar_movimiento(id_estante, peso_total, 'Retirar', timestamp, rut_usuario)
    movimiento_db = {
        "id_estante": id_estante,
        "idproducto": idproducto,
        "idproducto_detectado": datos.get("idproducto_detectado"),
        "cantidad": cantidad,
        "peso_por_unidad": peso_por_unidad,
        "peso_total": peso_total,
        "tipo_evento": 'Retirar',
        "timestamp": timestamp.isoformat(),
        "rut_usuario": rut_usuario,
        "match_por_peso": datos.get("match_por_peso"),
        "es_venta_validada": datos.get("es_venta_validada"),
        "es_retiro_sospechoso": datos.get("es_retiro_sospechoso"),
        "motivo_sospecha": datos.get("motivo_sospecha"),
        "observacion": datos.get("observacion")
    }

    supabase.table("movimientos_inventario").insert(movimiento_db).execute()
    return movimiento_db


