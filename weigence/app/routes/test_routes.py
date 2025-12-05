"""
Rutas de prueba para el sistema de registro de errores
Solo para desarrollo y testing
"""
from flask import Blueprint, render_template, jsonify
from app.utils.error_logger import registrar_error, registrar_error_critico
from .utils import requiere_login

bp = Blueprint('test', __name__, url_prefix='/test')


@bp.route('/errores')
@requiere_login
def test_errores():
    """Página de prueba para generar errores intencionalmente"""
    return render_template('pagina/test_errores.html')


@bp.route('/audit-logs')
@requiere_login
def test_audit_logs():
    """Página de prueba para verificar API de logs de auditoría"""
    return render_template('test_audit_logs.html')


@bp.route('/error-backend')
@requiere_login
def test_error_backend():
    """Genera un error normal de backend para pruebas"""
    try:
        registrar_error(
            mensaje="Error de prueba desde backend",
            modulo="test",
            exception=None
        )
        return jsonify({
            'success': True,
            'message': 'Error registrado correctamente en auditoría'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al registrar: {str(e)}'
        }), 500


@bp.route('/error-critico-backend')
@requiere_login
def test_error_critico_backend():
    """Genera un error crítico de backend para pruebas"""
    try:
        # Simular una excepción real
        try:
            result = 10 / 0  # Esto genera ZeroDivisionError
        except Exception as exc:
            registrar_error_critico(
                mensaje="Error crítico de prueba (división por cero)",
                modulo="test",
                exception=exc
            )
        
        return jsonify({
            'success': True,
            'message': 'Error crítico registrado correctamente en auditoría'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al registrar: {str(e)}'
        }), 500
