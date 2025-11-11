from flask import render_template, jsonify, request, session, redirect, url_for, flash
from . import bp
from api.conexion_supabase import supabase
from datetime import datetime
from pathlib import Path
import json
from app.ia import generar_recomendacion_v2

from .utils import requiere_login

last_manual_update = datetime.now()


def check_sistema_integral():
    estados = []
    try:
        supabase.table("productos").select("idproducto").limit(1).execute()
        estados.append("db_ok")
    except Exception:
        estados.append("db_fail")

    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    errors_file = data_dir / 'errors_log.json'
    errores = []

    if errors_file.exists():
        with open(errors_file, 'r', encoding='utf-8') as f:
            errores = json.load(f)

    if "db_fail" in estados:
        estado_general = "offline"
    elif errores:
        estado_general = "warning"
    else:
        estado_general = "online"

    detalles = []
    if "db_fail" in estados:
        detalles.append("No se pudo conectar a la base de datos")
    for e in errores[:10]:
        ts = e.get('timestamp', '')
        msg = e.get('message', '')
        detalles.append(f"{ts} - {msg}")

    return estado_general, detalles


@bp.route('/api/status')
@requiere_login
def api_status():
    estado, detalles = check_sistema_integral()
    global last_manual_update
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
