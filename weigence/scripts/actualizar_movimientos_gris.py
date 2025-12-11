import logging
from datetime import datetime
from app.data.movimiento_service import procesar_movimiento
from api.conexion_supabase import supabase

logging.basicConfig(level=logging.INFO)

def actualizar_movimientos_gris():
    # Obtener todos los movimientos tipo 'gris' sin producto asociado
    movimientos = supabase.table("movimientos_inventario") \
        .select("id_movimiento, id_estante, peso_total, timestamp") \
        .eq("tipo_evento", "gris") \
        .is_("idproducto", None) \
        .execute().data

    logging.info(f"Total movimientos gris sin producto: {len(movimientos)}")

    for mov in movimientos:
        id_mov = mov["id_movimiento"]
        id_estante = mov["id_estante"]
        peso_total = mov["peso_total"]
        timestamp = mov["timestamp"]
        try:
            # Convertir timestamp si es necesario
            if isinstance(timestamp, str):
                timestamp_dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                timestamp_dt = timestamp
            resultado = procesar_movimiento(id_estante, peso_total, 'gris', timestamp_dt, None)
            if resultado.get("idproducto"):
                # Actualizar el movimiento con el producto detectado y flags
                update_data = {
                    "idproducto": resultado["idproducto"],
                    "idproducto_detectado": resultado["idproducto_detectado"],
                    "match_por_peso": resultado["match_por_peso"],
                    "peso_por_unidad": resultado["peso_por_unidad"],
                    "es_venta_validada": resultado["es_venta_validada"],
                    "es_retiro_sospechoso": resultado["es_retiro_sospechoso"],
                    "motivo_sospecha": resultado["motivo_sospecha"],
                    "observacion": resultado["observacion"]
                }
                supabase.table("movimientos_inventario").update(update_data).eq("id_movimiento", id_mov).execute()
                logging.info(f"Movimiento {id_mov} actualizado con producto {resultado['idproducto']}")
            else:
                logging.info(f"Movimiento {id_mov} sigue sin producto detectado")
        except Exception as e:
            logging.error(f"Error actualizando movimiento {id_mov}: {e}")

if __name__ == "__main__":
    actualizar_movimientos_gris()
