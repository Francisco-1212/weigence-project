from flask import render_template, jsonify, request, session, redirect, url_for, flash, make_response
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime, timedelta
from functools import wraps
from collections import defaultdict
import requests


def requiere_login(f):
    """
    Decorador que requiere sesión activa y previene caché del navegador.
    Agrega headers de seguridad para evitar navegación con botones atrás/adelante.
    """
    @wraps(f)
    def decorador(*args, **kwargs):
        # Validar que existe sesión activa
        if 'usuario_logueado' not in session:
            session.clear()  # Limpiar cualquier residuo de sesión
            flash("Debes iniciar sesión para acceder a esta página", "warning")
            return redirect(url_for('main.login'))
        
        # Validar que la sesión tenga los datos mínimos requeridos
        if not session.get('usuario_id') or not session.get('usuario_nombre'):
            session.clear()
            flash("Sesión inválida. Por favor inicia sesión nuevamente", "error")
            return redirect(url_for('main.login'))
        
        # Ejecutar la función protegida
        response = make_response(f(*args, **kwargs))
        
        # Agregar headers de seguridad para prevenir caché
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        
        return response
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
        # === 1) Generar alertas nuevas antes de leer (sin llamada HTTP) ===
        try:
            from .alertas import generar_alertas_basicas
            generar_alertas_basicas()
        except Exception as err:
            print(f"Advertencia: no se pudieron regenerar alertas automáticamente ({err})")

        # === 2) Obtener productos activos primero ===
        try:
            productos_activos = supabase.table("productos").select("idproducto, nombre").eq("activo", True).execute().data or []
        except:
            productos_activos = supabase.table("productos").select("idproducto, nombre").execute().data or []
        
        ids_activos = {p["idproducto"] for p in productos_activos}
        nombres_activos = {p["nombre"].lower() for p in productos_activos}
        
        print(f"[DEBUG] Productos activos: {len(ids_activos)}")
        
        # === 3) Leer alertas desde Supabase ===
        query = (
            supabase.table("alertas")
            .select("*")
            .in_("estado", ["pendiente", "activo"])
            .order("fecha_creacion", desc=True)
        )
        data = query.limit(50).execute()
        alertas_raw = data.data or []
        
        print(f"[DEBUG] Alertas obtenidas: {len(alertas_raw)}")
        
        # === 4) Filtrar y resolver alertas de productos inexistentes ===
        alertas = []
        alertas_a_resolver = []
        
        for a in alertas_raw:
            id_prod = a.get("idproducto")
            id_estante = a.get("id_estante")
            titulo = a.get("titulo", "")
            
            # Alertas de estantes (sin idproducto) siempre pasan
            if id_estante and not id_prod:
                alertas.append(a)
                continue
            
            # Si la alerta tiene idproducto, verificar que el producto existe
            if id_prod:
                if id_prod not in ids_activos:
                    # Marcar para resolver
                    alertas_a_resolver.append(a["id"])
                    print(f"[FILTRO] Alerta descartada (producto inexistente): {titulo}")
                    continue
            
            # Si el título menciona un producto específico, verificar que existe
            titulo_lower = titulo.lower()
            if any(palabra in titulo_lower for palabra in ["vencer", "vencido", "stock", "agotado"]):
                # Solo filtrar si tiene idproducto
                if id_prod:
                    # Extraer nombre del producto del título
                    encontrado = False
                    for nombre in nombres_activos:
                        if nombre in titulo_lower:
                            encontrado = True
                            break
                    
                    if not encontrado:
                        # El producto mencionado no existe
                        alertas_a_resolver.append(a["id"])
                        print(f"[FILTRO] Alerta descartada (nombre no encontrado): {titulo}")
                        continue
            
            # Alerta válida
            alertas.append(a)
        
        # Resolver alertas inválidas en batch
        if alertas_a_resolver:
            try:
                for alert_id in alertas_a_resolver:
                    supabase.table("alertas").update({"estado": "resuelto"}).eq("id", alert_id).execute()
                print(f"[LIMPIEZA] {len(alertas_a_resolver)} alertas resueltas automáticamente")
            except Exception as resolve_err:
                print(f"[ERROR] Error al resolver alertas: {resolve_err}")
        
        print(f"[DEBUG] Alertas válidas: {len(alertas)}")

        # === 5) Alerta dinámica: productos sin pesaje en 7 días ===
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
            # Fecha antigua para que aparezca al final (hace 30 días)
            fecha_antigua = (hoy - timedelta(days=30)).isoformat()
            alerta_sint = {
                "id": "__no_pesaje_7d__",
                "tipo_color": "amarillo",
                "icono": "warning",
                "titulo": "Productos sin pesaje reciente",
                "descripcion": f"No se han pesado {len(sin_pesaje)} producto(s) en los últimos 7 días.",
                "detalle": "Sugerencia: planificar control de estantes y calibración si aplica.",
                "enlace": "/movimientos",
                "fecha_creacion": fecha_antigua,  # Fecha antigua para que aparezca al final
            }
            if not any(a.get("id") == alerta_sint["id"] for a in alertas):
                # Agregar al final - el ordenamiento por fecha la colocará al final automáticamente
                alertas.append(alerta_sint)

        # === 6) Ordenar alertas por fecha (más recientes primero) ===
        def obtener_timestamp(alerta):
            try:
                # Obtener fecha_creacion o timestamp
                fecha = alerta.get("fecha_creacion") or alerta.get("timestamp") or hoy.isoformat()
                # Limpiar microsegundos y zona horaria si existen
                fecha_str = str(fecha).split(".")[0].replace("Z", "").replace("+00:00", "")
                # Convertir a timestamp
                dt = datetime.fromisoformat(fecha_str)
                return dt.timestamp()
            except Exception as e:
                print(f"[WARN] Error parseando fecha {alerta.get('titulo')}: {e}")
                return 0
        
        # Ordenar por fecha descendente (más recientes primero)
        alertas = sorted(alertas, key=lambda a: obtener_timestamp(a), reverse=True)

        # === 7) Agrupar por fecha para el header y formatear fechas ===
        hoy_d = datetime.now().date()
        ayer_d = hoy_d - timedelta(days=1)
        grupos = defaultdict(list)

        for a in alertas:
            f_raw = a.get("fecha_creacion") or a.get("timestamp")
            try:
                f_dt = (
                    datetime.fromisoformat(str(f_raw).split(".")[0])
                    if f_raw
                    else datetime.now()
                )
                f = f_dt.date()
                # Formatear fecha como "HH:MM:SS - DD/MM/YYYY"
                a["fecha_formateada"] = f_dt.strftime("%H:%M:%S - %d/%m/%Y")
            except Exception:
                f = hoy_d
                a["fecha_formateada"] = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")

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


# === UTILIDADES PARA INVENTARIO ===

def asignar_estante(categoria):
    """
    Asigna un estante según la categoría.
    Si la categoría contiene ciertos patrones, se le da un número fijo.
    Si no coincide con ninguno, se distribuye por orden.
    """
    categoria = (categoria or "").lower()

    if "analgésico" in categoria:
        return 1
    if "antibiótico" in categoria:
        return 2
    if "vitamina" in categoria:
        return 3
    if "suplemento" in categoria:
        return 4
    if "higiene" in categoria:
        return 5
    return 6  # categoría genérica


def formatear_estante_codigo(id_estante):
    """
    Convierte un id numérico en formato 'E-01', 'E-02', etc.
    """
    try:
        return f"E-{int(id_estante):02d}"
    except (TypeError, ValueError):
        return "E-??"


# === ENDPOINT DE SEGURIDAD: VERIFICAR SESIÓN ===
@bp.route('/api/verify-session', methods=['GET'])
def verify_session():
    """
    Endpoint para verificar si existe una sesión activa válida.
    Usado por JavaScript para prevenir navegación con caché después de logout.
    """
    is_authenticated = (
        'usuario_logueado' in session and 
        session.get('usuario_id') and 
        session.get('usuario_nombre')
    )
    
    response = jsonify({
        'authenticated': is_authenticated,
        'user_id': session.get('usuario_id') if is_authenticated else None
    })
    
    # Headers anti-caché para que el navegador no cachee esta respuesta
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response
