import json
from datetime import datetime
from pathlib import Path

from flask import jsonify, request

from api.conexion_supabase import supabase

from . import bp
from .utils import requiere_login

last_manual_update = datetime.now()


def check_sistema_integral():
    """Verifica el estado del sistema basado únicamente en la conexión a la base de datos"""
    try:
        supabase.table("productos").select("idproducto").limit(1).execute()
        return "online", []
    except Exception as e:
        return "offline", [f"No se pudo conectar a la base de datos: {str(e)}"]



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
    """Registra errores en la tabla de auditoría en lugar de archivo JSON"""
    payload = request.get_json() or {}
    message = payload.get('message', 'Error sin mensaje')
    detail = payload.get('detail', '')
    level = payload.get('level', 'error')
    
    try:
        from flask import session
        usuario = session.get('usuario', {}).get('email', 'Sistema')
        
        # Registrar en auditoría usando los campos correctos
        supabase.table('auditoria_eventos').insert({
            'fecha': datetime.now().isoformat(),
            'usuario': usuario,
            'accion': f'error_sistema_{level}',
            'detalle': f"{message}. {detail}" if detail else message
        }).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error registrando en auditoría: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/history')
@requiere_login
def api_history():
    """Retorna historial de eventos del sistema (movimientos, ventas, etc.)"""
    try:
        # Obtener eventos de auditoría recientes
        eventos = supabase.table("auditoria_eventos").select(
            "fecha, accion, detalle, usuario"
        ).order("fecha", desc=True).limit(50).execute()
        
        # Formatear eventos
        historial = []
        for evt in eventos.data:
            historial.append({
                'timestamp': evt.get('fecha'),
                'message': f"[{evt.get('accion', 'evento')}] {evt.get('detalle', '')} - {evt.get('usuario', 'Sistema')}"
            })
        
        return jsonify(historial)
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return jsonify([])


@bp.route('/api/history_errors')
@requiere_login
def api_history_errors():
    """Retorna historial de errores del sistema desde auditoría"""
    try:
        # Filtrar eventos que sean errores del sistema
        errores = supabase.table("auditoria_eventos").select(
            "fecha, detalle, usuario, accion"
        ).like("accion", "error_sistema%").order(
            "fecha", desc=True
        ).limit(50).execute()
        
        resultado = []
        for e in errores.data:
            resultado.append({
                'timestamp': e.get('fecha'),
                'message': e.get('detalle', ''),
                'usuario': e.get('usuario', 'Sistema'),
                'nivel': e.get('accion', 'error_sistema_error').replace('error_sistema_', '')
            })
        
        return jsonify(resultado)
    except Exception as e:
        print(f"Error leyendo errores desde auditoría: {e}")
        return jsonify([])


@bp.route('/api/refresh', methods=['POST'])
@requiere_login
def api_refresh():
    """Actualiza manualmente el timestamp de última actualización"""
    global last_manual_update
    last_manual_update = datetime.now()
    return jsonify({'success': True, 'timestamp': last_manual_update.isoformat()})
