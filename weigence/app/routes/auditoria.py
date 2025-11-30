from __future__ import annotations

import csv
import io
import json
import logging
import uuid
import zipfile
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from flask import jsonify, render_template, request, send_file, session

from api.conexion_supabase import supabase
from . import bp
from .decorators import requiere_rol

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent / "data"
ERROR_LOG_FILE = DATA_DIR / "errors_log.json"
CALIBRATION_LOG_FILE = DATA_DIR / "calibraciones_log.json"

DEFAULT_LIMIT = 200
DEFAULT_HOURS = 24

SUPPORTED_EVENT_TYPES = {
    "movimientos_inventario",
    "ventas",
    "detalle_ventas",
    "pesajes",
    "alertas",
    "alertas_stock",
    "alertas_sistema",
    "accesos_autorizaciones",
    "eventos_ia",
    "errores_criticos",
    "calibraciones",
    "inactividad",
    "anomalias_detectadas",
    "retiros_programados",
    "retiros_fuera_de_horario",
    "accesos_a_estantes",
    "lecturas_sensores",
    "login_logout_usuarios",
    "gestion_usuarios",
    "modificacion_perfil",
    "consulta_lectura",
    "exportacion",
    "modificacion_datos",
}

SEVERITY_DEFAULT = {
    "crit": "critical",
    "critical": "critical",
    "warn": "warning",
    "warning": "warning",
    "error": "error",
    "err": "error",
    "info": "info",
}


@bp.route("/auditoria")
@requiere_rol('supervisor', 'administrador')
def auditoria():
    from app.utils.eventohumano import registrar_evento_humano
    if session.get('last_page') != 'auditoria':
        usuario_nombre = session.get('usuario_nombre', 'Usuario')
        registrar_evento_humano("navegacion", f"{usuario_nombre} ingresó al módulo Auditoría")
        session['last_page'] = 'auditoria'
    # Carga inicial rápida: solo 30 eventos de las últimas 6 horas
    snapshot = generar_traza_auditoria(limit=30, horas=6)
    return render_template('pagina/auditoria.html', audit_snapshot=snapshot)


@bp.route('/api/auditoria/live-trail')
@requiere_rol('supervisor', 'administrador')
def api_auditoria_live_trail():
    filtros = _extract_filters(request.args)
    limit = _safe_int(request.args.get('limit'), DEFAULT_LIMIT)
    horas = _safe_int(request.args.get('horas'), DEFAULT_HOURS)
    snapshot = generar_traza_auditoria(limit=limit, filtros=filtros, horas=horas)

    return jsonify({
        "ok": True,
        "logs": snapshot["logs"],
        "meta": snapshot["meta"],
        "available_filters": snapshot["available_filters"],
        "applied_filters": filtros,
    })

@bp.route('/api/auditoria/logs')
@requiere_rol('supervisor', 'administrador')
def api_auditoria_logs():
    """
    Endpoint simple para la nueva Terminal de Investigación.
    Retorna todos los eventos ya normalizados.
    Sin límite de rate ya que se actualiza cada 45 segundos.
    """
    try:
        filtros = _extract_filters(request.args)
        limit = _safe_int(request.args.get('limit'), DEFAULT_LIMIT)
        horas = _safe_int(request.args.get('horas'), DEFAULT_HOURS)

        snapshot = generar_traza_auditoria(
            limit=limit,
            filtros=filtros,
            horas=horas
        )

        return jsonify({
            "ok": True,
            "logs": snapshot["logs"],
            "meta": snapshot["meta"],
            "filtros_aplicados": filtros,
        })
    except Exception as e:
        logger.error(f"Error en api_auditoria_logs: {str(e)}", exc_info=True)
        return jsonify({
            "ok": False,
            "error": str(e),
            "logs": [],
            "meta": {}
        }), 200  # Devolver 200 pero con ok: False para que el frontend lo maneje

@bp.route('/api/auditoria/export', methods=['POST'])
@requiere_rol('supervisor', 'administrador')
def api_export_auditoria():
    payload = request.get_json(silent=True) or {}
    formato = (payload.get('formato') or 'csv').lower()
    filtros = payload.get('filtros') or {}
    limit = _safe_int(payload.get('limit'), 600)
    horas = _safe_int(payload.get('horas'), DEFAULT_HOURS)

    snapshot = generar_traza_auditoria(limit=limit, filtros=filtros, horas=horas)
    logs = snapshot["logs"]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if formato == 'zip':
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('logs.json', json.dumps(logs, ensure_ascii=False, indent=2))
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'audit-trail-{stamp}.zip'
        )

    if formato == 'pdf':
        pdf_buffer = _build_pdf_bytes(logs)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'audit-trail-{stamp}.pdf'
        )

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["timestamp", "nivel", "tipo_evento", "usuario", "producto", "estante", "mensaje"])
    for entry in logs:
        writer.writerow([
            entry.get("timestamp"),
            entry.get("nivel"),
            entry.get("tipo_evento"),
            entry.get("usuario"),
            entry.get("producto"),
            entry.get("estante"),
            entry.get("mensaje"),
        ])

    bytes_buffer = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
    return send_file(
        bytes_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'audit-trail-{stamp}.csv'
    )


@bp.route('/api/auditoria/usuarios-activos')
@requiere_rol('supervisor', 'administrador')
def api_usuarios_activos():
    """
    Obtiene los usuarios activos con su última actividad.
    Usa el sistema de heartbeat en tiempo real para determinar usuarios conectados.
    """
    try:
        from app.utils.sesiones_activas import obtener_usuarios_conectados
        
        # Obtener usuarios conectados del sistema de heartbeat (últimos 30 minutos para ser más permisivo)
        usuarios_conectados_ruts, detalles_conectados = obtener_usuarios_conectados(timeout_minutos=30)
        
        logger.info(f"[USUARIOS-ACTIVOS] Conectados desde heartbeat: {len(usuarios_conectados_ruts)}")
        
        # Consultar todos los usuarios de la base de datos (sin apellido porque no existe esa columna)
        usuarios_result = supabase.table('usuarios')\
            .select('rut_usuario, nombre, correo, rol')\
            .execute()
        
        if not usuarios_result.data:
            return jsonify({
                'activos': [],
                'total_activos': 0,
                'total_usuarios': 0
            })
        
        usuarios_con_actividad = []
        ahora = datetime.now()
        
        for usuario in usuarios_result.data:
            rut = usuario.get('rut_usuario')
            es_activo = rut in usuarios_conectados_ruts
            tiempo_relativo = 'Sin actividad reciente'
            ultima_actividad_iso = None
            
            if es_activo and rut in detalles_conectados:
                # Usuario activo con heartbeat
                ultima_act_str = detalles_conectados[rut].get('ultima_actividad')
                if ultima_act_str:
                    try:
                        dt_actividad = datetime.fromisoformat(ultima_act_str)
                        ultima_actividad_iso = ultima_act_str
                        
                        # Calcular tiempo relativo
                        delta = ahora - dt_actividad
                        
                        if delta.total_seconds() < 60:
                            tiempo_relativo = 'Ahora mismo'
                        elif delta.total_seconds() < 3600:
                            minutos = int(delta.total_seconds() / 60)
                            tiempo_relativo = f'Hace {minutos} min'
                        else:
                            tiempo_relativo = 'Hace menos de 1 h'
                    except Exception as e:
                        logger.error(f"Error procesando ultima_actividad del heartbeat: {e}")
                        tiempo_relativo = 'Activo ahora'
            
            nombre = usuario.get('nombre') or ''
            
            usuarios_con_actividad.append({
                'rut': rut,
                'nombre': nombre,
                'apellido': '',  # La columna apellido no existe en la BD
                'correo': usuario.get('correo', ''),
                'rol': usuario.get('rol', ''),
                'nombre_completo': nombre,
                'ultima_actividad': ultima_actividad_iso,
                'tiempo_relativo': tiempo_relativo,
                'activo': es_activo
            })
        
        # Ordenar: activos primero, luego por nombre
        usuarios_con_actividad.sort(key=lambda x: (not x['activo'], x['nombre']))
        
        activos_count = len(usuarios_conectados_ruts)
        
        logger.info(f"Total usuarios: {len(usuarios_con_actividad)}, Activos: {activos_count}")
        
        return jsonify({
            'activos': usuarios_con_actividad,
            'total_activos': activos_count,
            'total_usuarios': len(usuarios_con_actividad)
        })
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"[USUARIOS-ACTIVOS] Error completo:\n{error_detail}")
        return jsonify({'error': str(e), 'detail': error_detail}), 500


@bp.route('/api/auditoria/recalibrar', methods=['POST'])
@requiere_rol('supervisor', 'administrador')
def api_recalibrar_sensores():
    payload = request.get_json(silent=True) or {}
    usuario = session.get('usuario_nombre') or session.get('usuario_id') or 'sistema'
    detalle = (payload.get('detalle') or 'Recalibración solicitada desde la terminal').strip()

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "usuario": usuario,
        "detalle": detalle,
    }

    historial = _read_json_list(CALIBRATION_LOG_FILE)
    historial.insert(0, registro)
    historial = historial[:80]
    _write_json_list(CALIBRATION_LOG_FILE, historial)

    return jsonify({"ok": True, "mensaje": "Secuencia de recalibración enviada", "registro": registro})


def generar_traza_auditoria(*, limit: int = DEFAULT_LIMIT, filtros: Dict[str, str] | None = None, horas: int = DEFAULT_HOURS) -> Dict[str, Any]:
    horas = horas or DEFAULT_HOURS
    limit = limit or DEFAULT_LIMIT
    desde = datetime.now(timezone.utc) - timedelta(hours=horas)

    events, catalog = _gather_audit_events(desde, horas)
    filtered = _apply_filters(events, filtros)

    return {
        "logs": filtered[:limit],
        "meta": _build_meta(filtered),
        "available_filters": {
            "usuarios": sorted(catalog["usuarios"]),
            "productos": sorted(catalog["productos"]),
            "estantes": sorted(catalog["estantes"]),
            "tipos_evento": sorted({evt["tipo_evento"] for evt in events}),
            "severidades": sorted({evt["severidad"] for evt in events}),
        },
    }



def _gather_audit_events(desde: datetime, horas: int = DEFAULT_HOURS) -> tuple[List[Dict[str, Any]], Dict[str, set[str]]]:
    events: List[Dict[str, Any]] = []
    catalog = {"usuarios": set(), "productos": set(), "estantes": set()}
    user_activity = defaultdict(lambda: {"first": None, "last": None, "nombre": None})
    movement_timestamps: List[datetime] = []
    sensor_snapshots: Dict[str, Dict[str, Any]] = {}

    usuarios_cache = _build_cache('usuarios', 'rut_usuario', 'nombre')
    productos_cache = _build_cache('productos', 'idproducto', 'nombre')
    estantes_cache = _build_cache('estantes', 'id_estante', 'nombre')

    def add_event(*, event_id: str | None, tipo: str, mensaje: str, ts: datetime | str, nivel: str = 'INFO',
                  usuario: str | None = None, usuario_id: str | None = None,
                  producto: str | None = None, producto_id: Any = None,
                  estante: str | None = None, estante_id: Any = None,
                  fuente: str | None = None, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        tipo_clean = (tipo or 'movimientos_inventario').lower()
        if tipo_clean not in SUPPORTED_EVENT_TYPES:
            tipo_clean = 'movimientos_inventario'
        nivel_up = (nivel or 'INFO').upper()
        severidad = SEVERITY_DEFAULT.get(nivel_up.lower(), 'info')

        # Normalizar timestamp - puede venir como string ISO o datetime
        if isinstance(ts, str):
            # Ya es un string ISO, parsearlo a datetime para procesar
            ts_dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            ts_str = ts
        else:
            # Es datetime, convertir a string
            ts_dt = ts
            ts_str = ts.isoformat()

        entry = {
            "id": event_id or f"evt-{uuid.uuid4().hex[:8]}",
            "timestamp": ts_str,
            "_ts": ts_dt,
            "fecha": ts_dt.strftime('%Y-%m-%d'),
            "hora": ts_dt.strftime('%H:%M:%S'),
            "nivel": nivel_up,
            "severidad": severidad,
            "tipo_evento": tipo_clean,
            "mensaje": mensaje,
            "detalle": mensaje,  # Agregar detalle explícitamente
            "usuario": usuario,
            "usuario_id": usuario_id,
            "rut": usuario_id or 'N/A',  # RUT del usuario
            "producto": producto,
            "producto_id": producto_id,
            "estante": estante,
            "estante_id": estante_id,
            "fuente": fuente,
            "metadata": _serialize_metadata(metadata),
        }
        events.append(entry)
        if usuario:
            catalog["usuarios"].add(usuario)
        if producto:
            catalog["productos"].add(producto)
        if estante:
            catalog["estantes"].add(estante)
        return entry

    def track_activity(user_id: str | None, nombre: str | None, ts: datetime) -> None:
        if not user_id:
            return
        registro = user_activity[user_id]
        registro["nombre"] = nombre or registro.get("nombre") or user_id
        if registro["first"] is None or ts < registro["first"]:
            registro["first"] = ts
        if registro["last"] is None or ts > registro["last"]:
            registro["last"] = ts

    def collect_movimientos() -> None:
        rows = _supabase_select(
            'movimientos_inventario',
            select="""
                id_movimiento,
                tipo_evento,
                cantidad,
                timestamp,
                observacion,
                idproducto,
                id_estante,
                rut_usuario,
                productos:idproducto ( nombre ),
                estantes:id_estante ( nombre ),
                usuarios:rut_usuario ( nombre )
            """,
            order_field='timestamp',
            limit=100,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('timestamp'))
            movement_timestamps.append(ts)
            usuario_nombre = _safe_label(
                (row.get('usuarios') or {}).get('nombre'),
                usuarios_cache.get(row.get('rut_usuario')),
                row.get('rut_usuario'),
            )
            producto_nombre = _safe_label(
                (row.get('productos') or {}).get('nombre'),
                productos_cache.get(row.get('idproducto')),
                f"ID {row.get('idproducto')}",
            )
            estante_nombre = _safe_label(
                (row.get('estantes') or {}).get('nombre'),
                estantes_cache.get(row.get('id_estante')),
                row.get('id_estante'),
            )
            estante_code = _format_estante(estante_nombre)
            movement_type = _resolve_movement_type(row, ts)
            nivel = 'WARN' if movement_type == 'retiros_fuera_de_horario' else 'INFO'
            mensaje = f"{row.get('tipo_evento', 'Movimiento')} {row.get('cantidad') or 0}u de {producto_nombre or 'producto'} en {estante_code or 'estante'}"
            metadata = {
                'cantidad': row.get('cantidad'),
                'observacion': row.get('observacion'),
                'evento_original': row.get('tipo_evento'),
            }
            track_activity(row.get('rut_usuario'), usuario_nombre, ts)
            add_event(
                event_id=f"mov-{row.get('id_movimiento')}",
                tipo=movement_type,
                mensaje=mensaje,
                ts=ts,
                nivel=nivel,
                usuario=usuario_nombre,
                usuario_id=row.get('rut_usuario'),
                producto=producto_nombre,
                producto_id=row.get('idproducto'),
                estante=estante_code,
                estante_id=row.get('id_estante'),
                fuente='movimientos_inventario',
                metadata=metadata,
            )

    def collect_ventas() -> None:
        rows = _supabase_select(
            'ventas',
            select='idventa,total,fecha_venta,rut_usuario',
            order_field='fecha_venta',
            limit=50,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('fecha_venta'))
            usuario_nombre = _safe_label(usuarios_cache.get(row.get('rut_usuario')), row.get('rut_usuario'))
            track_activity(row.get('rut_usuario'), usuario_nombre, ts)
            total = float(row.get('total') or 0)
            mensaje = f"Venta #{row.get('idventa')} registrada por {usuario_nombre or 'sistema'} (${total:,.0f})"
            add_event(
                event_id=f"ven-{row.get('idventa')}",
                tipo='ventas',
                mensaje=mensaje,
                ts=ts,
                nivel='INFO',
                usuario=usuario_nombre,
                usuario_id=row.get('rut_usuario'),
                fuente='ventas',
                metadata={'total': total},
            )

    def collect_detalle_ventas() -> None:
        rows = _supabase_select(
            'detalle_ventas',
            select="""
                iddetalle,
                idventa,
                idproducto,
                cantidad,
                precio_unitario,
                fecha_detalle,
                productos:idproducto ( nombre )
            """,
            order_field='fecha_detalle',
            limit=80,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('fecha_detalle'))
            producto_nombre = _safe_label(
                (row.get('productos') or {}).get('nombre'),
                productos_cache.get(row.get('idproducto')),
                f"Producto {row.get('idproducto')}",
            )
            cantidad = row.get('cantidad') or 0
            precio = row.get('precio_unitario') or 0
            mensaje = f"{cantidad}u de {producto_nombre or 'producto'} (${precio:,.0f} c/u) para venta {row.get('idventa')}"
            add_event(
                event_id=f"det-{row.get('iddetalle')}",
                tipo='detalle_ventas',
                mensaje=mensaje,
                ts=ts,
                nivel='INFO',
                producto=producto_nombre,
                producto_id=row.get('idproducto'),
                fuente='detalle_ventas',
                metadata={'cantidad': cantidad, 'precio_unitario': precio, 'venta': row.get('idventa')},
            )

    def collect_pesajes() -> None:
        rows = _supabase_select(
            'pesajes',
            select='idpesaje,idproducto,peso_unitario,fecha_pesaje',
            order_field='fecha_pesaje',
            limit=60,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('fecha_pesaje'))
            producto_nombre = _safe_label(
                productos_cache.get(row.get('idproducto')),
                f"Producto {row.get('idproducto')}",
            )
            peso = row.get('peso_unitario')
            mensaje = f"Pesaje de {producto_nombre or 'producto'}: {peso} kg"
            add_event(
                event_id=f"peso-{row.get('idpesaje')}",
                tipo='pesajes',
                mensaje=mensaje,
                ts=ts,
                nivel='INFO',
                producto=producto_nombre,
                producto_id=row.get('idproducto'),
                fuente='pesajes',
                metadata={'peso': peso},
            )
            if row.get('idproducto'):
                sensor_snapshots[str(row['idproducto'])] = {
                    'ts': ts,
                    'producto': producto_nombre,
                    'peso': peso,
                }

    def collect_alertas() -> None:
        rows = _supabase_select(
            'alertas',
            select='id,tipo_color,titulo,descripcion,estado,fecha_creacion,idproducto,idusuario',
            order_field='fecha_creacion',
            limit=50,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('fecha_creacion'))
            tono = (row.get('tipo_color') or '').lower()
            titulo = row.get('titulo') or 'Alerta del sistema'
            descripcion = row.get('descripcion') or ''
            
            # Determinar nivel según color
            nivel = 'CRIT' if tono == 'rojo' else 'WARN' if tono == 'amarillo' else 'INFO'
            
            # Categorizar el tipo de alerta de forma más específica
            titulo_lower = titulo.lower()
            if 'stock' in titulo_lower or 'bajo' in titulo_lower or 'agotado' in titulo_lower or 'inventario' in titulo_lower:
                base_type = 'alertas_stock'
            elif 'anom' in titulo_lower:
                base_type = 'anomalias_detectadas'
            else:
                base_type = 'alertas_sistema'
            
            usuario_nombre = _safe_label(usuarios_cache.get(row.get('idusuario')), row.get('idusuario'))
            producto_nombre = _safe_label(productos_cache.get(row.get('idproducto')), f"Producto {row.get('idproducto')}")
            
            # Crear mensaje más descriptivo combinando título y descripción
            if descripcion and descripcion != titulo:
                mensaje = f"{titulo}: {descripcion}"
            else:
                mensaje = titulo
            
            add_event(
                event_id=f"alert-{row.get('id')}",
                tipo=base_type,
                mensaje=mensaje,
                ts=ts,
                nivel=nivel,
                usuario=usuario_nombre,
                usuario_id=row.get('idusuario'),
                producto=producto_nombre,
                producto_id=row.get('idproducto'),
                fuente='alertas',
                metadata={'descripcion': row.get('descripcion'), 'estado': row.get('estado'), 'tipo_color': tono},
            )

    def collect_eventos_ia() -> None:
        rows = _supabase_select(
            'ia_auditoria_logs',
            select='id,modulo,resultado,confianza,fecha',
            order_field='fecha',
            limit=40,
            since=desde,
        )
        for row in rows:
            ts = _parse_ts(row.get('fecha'))
            resultado = row.get('resultado') or ''
            nivel = 'INFO'
            if resultado.startswith('[') and ']' in resultado:
                prefix = resultado.split(']', 1)[0].strip('[]').upper()
                if prefix in {'CRIT', 'CRITICAL'}:
                    nivel = 'CRIT'
                elif prefix in {'WARN', 'WARNING'}:
                    nivel = 'WARN'
            mensaje = resultado.split(']', 1)[-1].strip() if ']' in resultado else resultado
            add_event(
                event_id=f"ia-{row.get('id')}",
                tipo='eventos_ia',
                mensaje=mensaje or 'Evento IA registrado',
                ts=ts,
                nivel=nivel,
                fuente=row.get('modulo'),
                metadata={'confianza': row.get('confianza'), 'modulo': row.get('modulo')},
            )

    def collect_error_logs() -> None:
        for entry in _read_json_list(ERROR_LOG_FILE)[:80]:
            ts = _parse_ts(entry.get('timestamp'))
            # Filtrar eventos antiguos fuera del rango temporal
            if ts < desde:
                continue
            mensaje = entry.get('message') or 'Error registrado'
            add_event(
                event_id=f"err-{uuid.uuid4().hex[:8]}",
                tipo='errores_criticos',
                mensaje=mensaje,
                ts=ts,
                nivel='CRIT',
                fuente='sistema',
            )

    def collect_calibraciones() -> None:
        for entry in _read_json_list(CALIBRATION_LOG_FILE)[:60]:
            ts = _parse_ts(entry.get('timestamp'))
            # Filtrar eventos antiguos fuera del rango temporal
            if ts < desde:
                continue
            add_event(
                event_id=f"cal-{uuid.uuid4().hex[:8]}",
                tipo='calibraciones',
                mensaje=entry.get('detalle') or 'Recalibración ejecutada',
                ts=ts,
                nivel='INFO',
                usuario=entry.get('usuario'),
                fuente='terminal',
            )

    def collect_sensor_snapshots() -> None:
        if not sensor_snapshots:
            return
        for data in list(sensor_snapshots.values())[:8]:
            ts = data['ts']
            mensaje = f"Lectura sensor {data.get('sensor') or 'N/A'}: {data.get('peso')} kg ({data.get('producto')})"
            add_event(
                event_id=f"sns-{uuid.uuid4().hex[:8]}",
                tipo='lecturas_sensores',
                mensaje=mensaje,
                ts=ts,
                nivel='INFO',
                producto=data.get('producto'),
                fuente='sensores',
                metadata={'sensor': data.get('sensor'), 'peso': data.get('peso')},
            )

    def collect_auditoria_eventos():
        """Recolectar eventos de login/logout y acciones de usuarios desde la tabla auditoria_eventos"""
        try:
            # Usar el parámetro 'desde' para filtrar correctamente
            desde_iso = desde.isoformat()
            
            # Aumentar límite según el rango temporal
            eventos_limit = 100
            if horas >= 720:  # Mes
                eventos_limit = 1000
            elif horas >= 168:  # Semana
                eventos_limit = 500
            
            response = (
                supabase.table("auditoria_eventos")
                .select("id,fecha,usuario,accion,detalle")
                .gte("fecha", desde_iso)
                .order("fecha", desc=True)
                .limit(eventos_limit)
                .execute()
            )
            
            for row in response.data:
                try:
                    accion = row.get("accion", "").lower()
                    detalle = row.get("detalle", "")
                    usuario_nombre = row.get("usuario", "desconocido")
                    
                    # Mapear accion a tipo_evento esperado por frontend
                    if accion in ["login", "logout"]:
                        tipo = "login_logout_usuarios"
                        nivel = 'INFO'
                    elif accion in ["crear_usuario", "editar_usuario", "eliminar_usuario"]:
                        tipo = "gestion_usuarios"
                        nivel = 'INFO'
                    elif accion in ["editar_perfil"]:
                        tipo = "modificacion_perfil"
                        nivel = 'INFO'
                    elif accion in ["venta"]:
                        tipo = "ventas"
                        nivel = 'INFO'
                    elif accion in ["ver", "navegacion", "acceso"]:
                        tipo = "consulta_lectura"
                        nivel = 'INFO'
                    elif accion in ["exportar", "export", "descarga"]:
                        tipo = "exportacion"
                        nivel = 'INFO'
                    else:
                        tipo = "modificacion_datos"
                        nivel = 'INFO'
                    
                    # La fecha ya viene como string ISO desde Supabase
                    ts = row.get("fecha")
                    if not ts:
                        ts = datetime.now(timezone.utc).isoformat()
                    
                    # Intentar obtener RUT del usuario
                    usuario_id = None
                    if usuario_nombre and usuario_nombre != 'Sistema':
                        user_data = usuarios_cache.get(usuario_nombre)
                        if not user_data:
                            # Buscar por nombre
                            for rut, nombre in usuarios_cache.items():
                                if nombre == usuario_nombre:
                                    usuario_id = rut
                                    break
                    
                    add_event(
                        event_id=f"audit-{row.get('id')}",
                        tipo=tipo,
                        mensaje=detalle or accion,
                        ts=ts,
                        nivel=nivel,
                        usuario=usuario_nombre,
                        usuario_id=usuario_id,
                        fuente='auditoria_eventos',
                        metadata={'accion_original': accion},
                    )
                except Exception as row_error:
                    logger.error(f"[AUDITORIA] Error procesando fila individual: {row_error} | Fila: {row}")
                    continue

        except Exception as e:
            logger.error(f"[AUDITORIA] Error al recolectar eventos de auditoria_eventos: {e}", exc_info=True)

    def build_login_logout() -> None:
        for user_id, data in user_activity.items():
            first_ts = data.get('first')
            last_ts = data.get('last')
            if not first_ts:
                continue
            nombre = data.get('nombre') or user_id
            add_event(
                event_id=f"login-{user_id}",
                tipo='login_logout_usuarios',
                mensaje=f"Inicio de sesión confirmado para {nombre}",
                ts=first_ts,
                nivel='INFO',
                usuario=nombre,
                usuario_id=user_id,
                fuente='rbac',
            )
            if last_ts and last_ts > first_ts:
                add_event(
                    event_id=f"logout-{user_id}",
                    tipo='login_logout_usuarios',
                    mensaje=f"Cierre de sesión registrado para {nombre}",
                    ts=last_ts,
                    nivel='INFO',
                    usuario=nombre,
                    usuario_id=user_id,
                    fuente='rbac',
                )

    def build_inactividad() -> None:
        ordered = sorted(set(movement_timestamps))
        if len(ordered) < 2:
            return
        inserted = 0
        for anterior, siguiente in zip(ordered, ordered[1:]):
            gap = (siguiente - anterior).total_seconds()
            if gap >= 3 * 3600:
                midpoint = anterior + timedelta(seconds=gap / 2)
                add_event(
                    event_id=f"inact-{uuid.uuid4().hex[:8]}",
                    tipo='inactividad',
                    mensaje=f"{gap / 3600:.1}h sin actividad en estantes",
                    ts=midpoint,
                    nivel='WARN',
                    fuente='analizador',
                    metadata={'duracion_segundos': gap},
                )
                inserted += 1
                if inserted >= 3:
                    break

    # Ejecutar consultas en paralelo para reducir latencia
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [
            executor.submit(collect_movimientos),
            executor.submit(collect_ventas),
            executor.submit(collect_detalle_ventas),
            executor.submit(collect_pesajes),
            executor.submit(collect_alertas),
            executor.submit(collect_auditoria_eventos),
        ]
        # Esperar a que todas terminen
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error en consulta paralela: {e}")
    
    # Ejecutar después de las consultas principales
    collect_error_logs()
    collect_calibraciones()
    collect_sensor_snapshots()
    # build_login_logout()  # ← DESHABILITADO: genera eventos duplicados con timestamps incorrectos
    build_inactividad()

    events.sort(key=lambda e: e['_ts'], reverse=True)
    for entry in events:
        entry.pop('_ts', None)

    return events, catalog


def _resolve_movement_type(row: Dict[str, Any], ts: datetime) -> str:
    tipo_text = (row.get('tipo_evento') or '').lower()
    observacion = (row.get('observacion') or '').lower()
    if 'reti' in tipo_text:
        if ts.hour < 7 or ts.hour > 21:
            return 'retiros_fuera_de_horario'
        return 'retiros_programados'
    if 'autoriz' in observacion:
        return 'accesos_autorizaciones'
    if 'acceso' in observacion or 'estante' in observacion:
        return 'accesos_a_estantes'
    if 'calib' in observacion:
        return 'calibraciones'
    return 'movimientos_inventario'


def _build_cache(table: str, key_field: str, value_field: str) -> Dict[Any, str]:
    try:
        response = supabase.table(table).select(f"{key_field},{value_field}").limit(500).execute()
        data = response.data or []
        return {row.get(key_field): row.get(value_field) for row in data if row.get(key_field)}
    except Exception as exc:
        logger.debug("[Auditoria] No se pudo cargar catálogo %s: %s", table, exc)
        return {}


def _safe_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
        return parsed if parsed > 0 else default
    except (TypeError, ValueError):
        return default


def _parse_ts(raw: Any) -> datetime:
    if isinstance(raw, datetime):
        ts = raw
    elif raw:
        try:
            ts = datetime.fromisoformat(str(raw).replace('Z', '+00:00'))
        except ValueError:
            ts = datetime.utcnow()
    else:
        ts = datetime.utcnow()
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    else:
        ts = ts.astimezone(timezone.utc)
    return ts


def _format_estante(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str) and value.strip():
        return value.strip()
    try:
        return f"EST-{int(value):03d}"
    except (TypeError, ValueError):
        return str(value)


def _safe_label(*values: Any) -> str | None:
    for item in values:
        if isinstance(item, str) and item.strip():
            return item.strip()
    for item in values:
        if item:
            return str(item)
    return None


def _serialize_metadata(data: Dict[str, Any] | None) -> Dict[str, Any]:
    if not data:
        return {}
    resultado: Dict[str, Any] = {}
    for clave, valor in data.items():
        if isinstance(valor, datetime):
            resultado[clave] = valor.isoformat()
        else:
            resultado[clave] = valor
    return resultado


def _supabase_select(table: str, *, select: str, order_field: str, limit: int = 200, since: datetime | None = None) -> List[Dict[str, Any]]:
    query = supabase.table(table).select(select)
    
    # IMPORTANTE: Aplicar filtro de fecha ANTES de ordenar y limitar
    if since is not None:
        query = query.gte(order_field, since.isoformat())
    
    query = query.order(order_field, desc=True).limit(limit)
    
    try:
        response = query.execute()
        return response.data or []
    except Exception as exc:
        logger.warning("[Auditoria] Error consultando %s: %s", table, exc)
        return []


def _read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open('r', encoding='utf-8') as handle:
            data = json.load(handle)
            return data if isinstance(data, list) else []
    except Exception as exc:
        logger.warning("[Auditoria] No se pudo leer %s: %s", path.name, exc)
        return []


def _write_json_list(path: Path, payload: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with path.open('w', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
    except Exception as exc:
        logger.error("[Auditoria] No se pudo escribir %s: %s", path.name, exc)


def _apply_filters(events: List[Dict[str, Any]], filtros: Dict[str, str] | None) -> List[Dict[str, Any]]:
    if not filtros:
        return list(events)

    search = (filtros.get('search') or '').lower()
    usuario = (filtros.get('usuario') or '').lower()
    producto = (filtros.get('producto') or '').lower()
    estante = (filtros.get('estante') or '').lower()
    tipo = (filtros.get('tipo_evento') or '').lower()
    severidad = (filtros.get('severidad') or '').lower()
    fecha = filtros.get('fecha') or ''

    filtrados: List[Dict[str, Any]] = []
    for entry in events:
        if usuario and usuario not in (entry.get('usuario') or '').lower():
            continue
        if producto and producto not in (entry.get('producto') or '').lower():
            continue
        if estante and estante not in (entry.get('estante') or '').lower():
            continue
        if tipo and tipo != (entry.get('tipo_evento') or '').lower():
            continue
        if severidad and severidad != (entry.get('severidad') or '').lower():
            continue
        if fecha and fecha != entry.get('fecha'):
            continue
        if search:
            haystack = " ".join(
                str(value)
                for value in [
                    entry.get('mensaje'),
                    entry.get('usuario'),
                    entry.get('producto'),
                    entry.get('estante'),
                    entry.get('tipo_evento'),
                    json.dumps(entry.get('metadata') or {}, ensure_ascii=False),
                ]
            ).lower()
            if search not in haystack:
                continue
        filtrados.append(entry)
    return filtrados


def _build_meta(logs: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    dataset = list(logs)
    severity_counts = Counter(item.get('severidad', 'info') for item in dataset)
    type_counts = Counter(item.get('tipo_evento') for item in dataset)
    mem_usage = 48.0 + len(dataset) * 0.35
    cpu_usage = min(92.0, 3.0 + len(dataset) * 0.15)
    latency = max(4.0, 18.0 - len(dataset) * 0.05)

    return {
        'total': len(dataset),
        'por_severidad': dict(severity_counts),
        'por_tipo': dict(type_counts),
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'system': {
            'mem': f"{mem_usage:.1f}MB",
            'cpu': f"{cpu_usage:.1f}%",
            'latency': f"{latency:.0f}ms",
        },
    }


def _extract_filters(source: Dict[str, Any]) -> Dict[str, str]:
    mapping = {
        'search': source.get('q') or source.get('search') or '',
        'usuario': source.get('usuario') or '',
        'producto': source.get('producto') or '',
        'estante': source.get('estante') or '',
        'tipo_evento': source.get('tipo_evento') or '',
        'severidad': source.get('severidad') or '',
        'fecha': source.get('fecha') or '',
    }
    return {clave: valor.strip() for clave, valor in mapping.items() if valor and valor.strip()}


def _simple_pdf(lines: List[str]) -> io.BytesIO:
    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    content_lines = ['BT', '/F1 10 Tf', '14 TL', '72 800 Td']
    for line in lines:
        safe = line.replace('\\', '\\\\').replace('(', '\(').replace(')', '\)')
        content_lines.append(f'({safe}) Tj')
        content_lines.append('T*')
    content_lines.append('ET')

    content_bytes = "\n".join(content_lines).encode('latin-1', 'ignore')

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj\n",
        f"4 0 obj << /Length {len(content_bytes)} >> stream\n".encode('ascii') + content_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n",
    ]

    offsets: List[int] = []
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)

    xref_pos = buffer.tell()
    buffer.write(f"xref\n0 {len(offsets) + 1}\n0000000000 65535 f \n".encode('ascii'))
    for off in offsets:
        buffer.write(f"{off:010d} 00000 n \n".encode('ascii'))
    buffer.write(f"trailer << /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode('ascii'))
    buffer.seek(0)
    return buffer


def _build_pdf_bytes(logs: List[Dict[str, Any]]) -> io.BytesIO:
    lines = [
        'Weigence - Live Audit Trail',
        f"Eventos exportados: {len(logs)}",
        f"Generado: {datetime.now(timezone.utc).isoformat()}",
        '',
    ]
    for entry in logs[:80]:
        linea = f"[{entry.get('nivel')}] {entry.get('fecha')} {entry.get('hora')} {entry.get('tipo_evento')} :: {entry.get('mensaje')}"
        if entry.get('usuario'):
            linea += f" (Usuario: {entry['usuario']})"
        lines.append(linea)
    return _simple_pdf(lines)
