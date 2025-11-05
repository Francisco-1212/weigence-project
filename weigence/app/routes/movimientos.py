from flask import render_template
from .utils import requiere_login
from . import bp
from api.conexion_supabase import supabase

@bp.route("/movimientos")
@requiere_login
def movimientos():
    try:
        # Consultar con relaciones completas para evitar múltiples queries
        q = (
            supabase.table("movimientos_inventario")
            .select("""
                id_movimiento,
                idproducto,
                productos(nombre),
                id_estante,
                estantes(id_estante),
                rut_usuario,
                usuarios(nombre),
                cantidad,
                tipo_evento,
                timestamp,
                observacion
            """)
            .order("timestamp", desc=True)
            .limit(50)
            .execute()
        )

        movimientos = []
        for m in q.data or []:
            producto = m.get("productos", {}).get("nombre") if isinstance(m.get("productos"), dict) else None
            estante = m.get("estantes", {}).get("id_estante") if isinstance(m.get("estantes"), dict) else None
            usuario = m.get("usuarios", {}).get("nombre") if isinstance(m.get("usuarios"), dict) else None

            movimientos.append({
                "producto": producto or f"Producto {m.get('idproducto', '-')}",
                "tipo_evento": m.get("tipo_evento", "—"),
                "cantidad": m.get("cantidad", 0),
                "ubicacion": f"Estante {estante}" if estante else "—",
                "usuario_nombre": usuario or "Desconocido",
                "rut_usuario": m.get("rut_usuario", "—"),
                "observacion": m.get("observacion", ""),
                "timestamp": (m.get("timestamp") or "")[:16].replace("T", " "),
            })

    except Exception as e:
        print("Error al cargar movimientos:", e)
        movimientos = []

    # render_template con MOVIMIENTOS disponibles en JS
    return render_template("pagina/movimientos.html", movimientos=movimientos)
