from flask import render_template
from .utils import requiere_login
from . import bp
from api.conexion_supabase import supabase
from flask import request, jsonify, session
from datetime import datetime

@bp.route("/movimientos")
@requiere_login
def movimientos():
    try:
        #print("Realizando consulta a Supabase...")
        q = (
            supabase.table("movimientos_inventario")
            .select("""
                *,
                productos:idproducto (
                    nombre
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
            "idproducto, nombre, stock"
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

@bp.route("/api/movimientos/nuevo", methods=["POST"])
@requiere_login
def nuevo_movimiento():
    try:
        datos = request.json
        print("Datos recibidos:", datos)  # Para debugging
        
        # Validar datos requeridos
        required_fields = ['tipo_evento', 'idproducto', 'id_estante', 'cantidad']
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

        # Obtener el usuario correctamente de la sesión
        datos["rut_usuario"] = session.get("usuario_id")  # Asegúrate que coincida con el nombre usado en login.py
        if not datos["rut_usuario"]:
            return jsonify({"success": False, "error": "Usuario no identificado"}), 401

        # Agregar timestamp
        datos["timestamp"] = datetime.now().isoformat()

        # Realizar la inserción
        response = supabase.table("movimientos_inventario").insert(datos).execute()

        # Si es añadir o retirar, actualizar stock
        if datos["tipo_evento"] in ["Añadir", "Retirar"]:
            factor = 1 if datos["tipo_evento"] == "Añadir" else -1
            stock_update = supabase.table("productos").update({
                "stock": supabase.raw(f"stock + {factor * datos['cantidad']}")
            }).eq("idproducto", datos["idproducto"]).execute()

        return jsonify({
            "success": True,
            "data": response.data,
            "mensaje": "Movimiento registrado correctamente"
        })

    except Exception as e:
        print("Error en nuevo_movimiento:", str(e))
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
