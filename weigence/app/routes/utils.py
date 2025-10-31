from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import requests





def requiere_login(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'usuario_logueado' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorador


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def agrupar_notificaciones_por_fecha(notificaciones):
    hoy = datetime.now().date()
    ayer = hoy - timedelta(days=1)
    grupos = defaultdict(list)

    for notif in notificaciones:
        fecha_raw = notif.get("fecha_creacion") or notif.get("timestamp")
        if fecha_raw:
            try:
                fecha = datetime.fromisoformat(str(fecha_raw).split('.')[0])
                fecha_notif = fecha.date()
            except Exception:
                fecha_notif = hoy
            if fecha_notif == hoy:
                grupos["Hoy"].append(notif)
            elif fecha_notif == ayer:
                grupos["Ayer"].append(notif)
            else:
                grupos[fecha_notif.strftime("%d/%m/%Y")].append(notif)
        else:
            grupos["Sin fecha"].append(notif)
    return grupos


def obtener_notificaciones(usuario_id=None):
    try:
        # Generar alertas nuevas antes de leer (sin llamada HTTP)
        try:
            from .alertas import generar_alertas_basicas
            generar_alertas_basicas()
        except Exception as err:
            print(f"Advertencia: no se pudieron regenerar alertas automáticamente ({err})")

        # === 2) Leer alertas desde Supabase ===
        query = supabase.table("alertas").select("*").neq("estado","descartada").order("fecha_creacion", desc=True)
        data = query.limit(30).execute()
        alertas = data.data or []

        # === 3) Alerta dinámica: productos sin pesaje en 7 días ===
        hoy = datetime.now()
        hace_7d = (hoy - timedelta(days=7)).isoformat()

        pesajes_7d = (
            supabase.table("pesajes")
            .select("idproducto,fecha_pesaje")
            .gte("fecha_pesaje", hace_7d)
            .execute()
            .data or []
        )
        ids_con_pesaje = {p["idproducto"] for p in pesajes_7d if p.get("idproducto")}

        prods = supabase.table("productos").select("idproducto,nombre").execute().data or []
        sin_pesaje = [p for p in prods if p["idproducto"] not in ids_con_pesaje]

        if sin_pesaje:
            alerta_sint = {
                "id": "__no_pesaje_7d__",
                "tipo_color": "amarillo",
                "icono": "warning",
                "titulo": "Productos sin pesaje reciente",
                "descripcion": f"No se han pesado {len(sin_pesaje)} producto(s) en los últimos 7 días.",
                "detalle": "Sugerencia: planificar control de estantes y calibración si aplica.",
                "enlace": "/movimientos",
                "fecha_creacion": hoy.isoformat(),
            }
            # Evita duplicar si ya existe
            if not any(a.get("id") == alerta_sint["id"] for a in alertas):
                alertas.insert(0, alerta_sint)

        # === 4) Agrupar por fecha para el header ===
        hoy_d = datetime.now().date()
        ayer_d = hoy_d - timedelta(days=1)
        grupos = defaultdict(list)

        for a in alertas:
            f_raw = a.get("fecha_creacion") or a.get("timestamp")
            try:
                f = (
                    datetime.fromisoformat(str(f_raw).split(".")[0]).date()
                    if f_raw
                    else hoy_d
                )
            except Exception:
                f = hoy_d

            if f == hoy_d:
                grupos["Hoy"].append(a)
            elif f == ayer_d:
                grupos["Ayer"].append(a)
            else:
                grupos[f.strftime("%d/%m/%Y")].append(a)

        return alertas, grupos

    except Exception as e:
        print(f"Error al obtener notificaciones: {e}")
        return [], {}
