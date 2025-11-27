import json
from datetime import datetime
from pathlib import Path

from flask import jsonify, request

from api.conexion_supabase import supabase

from . import bp
from .utils import requiere_login

last_manual_update = datetime.now()


def check_sistema_integral():
    estados = []
    try:
        supabase.table("productos").select("idproducto").limit(1).execute()
        estados.append("db_ok")
    except Exception:
        estados.append("db_fail")

    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    errors_file = data_dir / "errors_log.json"
    errores = []

    if errors_file.exists():
        with open(errors_file, "r", encoding="utf-8") as f:
            errores = json.load(f)

    estado_general = "offline" if "db_fail" in estados else ("warning" if errores else "online")

    detalles = []
    if "db_fail" in estados:
        detalles.append("No se pudo conectar a la base de datos")
    detalles.extend(
        f"{e.get('timestamp', '')} - {e.get('message', '')}"
        for e in errores[:10]
    )

    return estado_general, detalles


@bp.route('/api/status')
@requiere_login
def api_status():
    estado, detalles = check_sistema_integral()
    return jsonify({
        'connection_state': estado,
        'status_details': detalles,
        'last_update': last_manual_update.isoformat(),
        'important_events': 0
    })


@bp.route('/api/log_error', methods=['POST'])
@requiere_login
def api_log_error():
    payload = request.get_json() or {}
    message = payload.get('message', 'Error sin mensaje')
    timestamp = datetime.now().isoformat()
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    errors_file = data_dir / 'errors_log.json'
    try:
        existing = []
        if errors_file.exists():
            with open(errors_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        existing.insert(0, {'timestamp': timestamp, 'message': message})
        existing = existing[:200]
        with open(errors_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/history')
@requiere_login
def api_history():
    """Retorna historial de eventos del sistema (movimientos, ventas, etc.)"""
    try:
        # Obtener eventos de auditoría recientes
        eventos = supabase.table("auditoria_eventos").select(
            "timestamp, tipo_evento, detalle, usuario"
        ).order("timestamp", desc=True).limit(50).execute()
        
        # Formatear eventos
        historial = []
        for evt in eventos.data:
            historial.append({
                'timestamp': evt.get('timestamp'),
                'message': f"[{evt.get('tipo_evento', 'evento')}] {evt.get('detalle', '')} - {evt.get('usuario', 'Sistema')}"
            })
        
        return jsonify(historial)
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return jsonify([])


@bp.route('/api/history_errors')
@requiere_login
def api_history_errors():
    """Retorna historial de errores del sistema"""
    data_dir = Path(__file__).parent / 'data'
    errors_file = data_dir / 'errors_log.json'
    
    try:
        if errors_file.exists():
            with open(errors_file, 'r', encoding='utf-8') as f:
                errores = json.load(f)
            return jsonify(errores[:50])  # Solo los últimos 50
        else:
            return jsonify([])
    except Exception as e:
        print(f"Error leyendo errores: {e}")
        return jsonify([])


@bp.route('/api/refresh', methods=['POST'])
@requiere_login
def api_refresh():
    """Actualiza manualmente el timestamp de última actualización"""
    global last_manual_update
    last_manual_update = datetime.now()
    return jsonify({'success': True, 'timestamp': last_manual_update.isoformat()})
