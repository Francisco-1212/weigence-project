from flask import render_template
from . import bp
from api.conexion_supabase import supabase

@bp.route("/historial")
def historial():
    try:
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
            .limit(30)
            .execute()
        )

        movimientos = []
        for m in q.data or []:
            producto = m.get("productos", {}).get("nombre") if isinstance(m.get("productos"), dict) else None
            estante = m.get("estantes", {}).get("id_estante") if isinstance(m.get("estantes"), dict) else None
            usuario = m.get("usuarios", {}).get("nombre") if isinstance(m.get("usuarios"), dict) else None

            movimientos.append({
                "producto": producto or f"Producto {m.get('idproducto','-')}",
                "tipo_evento": m.get("tipo_evento", "—"),
                "cantidad": m.get("cantidad", 0),
                "ubicacion": f"Estante {estante}" if estante else "—",
                "usuario_nombre": usuario or "Desconocido",
                "timestamp": (m.get("timestamp") or "")[:16].replace("T", " "),
                "observacion": m.get("observacion", ""),
            })

        movimientos = movimientos[:5]

        eq = (
            supabase.table("alertas")
            .select("titulo, descripcion, tipo_color, fecha_creacion, estado")
            .order("fecha_creacion", desc=True)
            .limit(30)
            .execute()
        )
        errores = [
            {
                "tipo": (e.get("titulo") or e.get("tipo_color") or "Info"),
                "descripcion": e.get("descripcion", "Sin descripción"),
                "fecha_creacion": (e.get("fecha_creacion") or "")[:16].replace("T", " "),
                "estado": e.get("estado", "pendiente"),
            }
            for e in (eq.data or [])
        ]

    except Exception as e:
        print("Error al cargar historial:", e)
        movimientos, errores = [], []

    return render_template("pagina/historial.html", movimientos=movimientos, errores=errores)
