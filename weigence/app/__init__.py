import os
from flask import Flask, session, jsonify, request
from flask_login import LoginManager
from .routes import bp as routes_bp
from .routes.utils import obtener_notificaciones
from flask import Blueprint
from datetime import timedelta
from dotenv import load_dotenv
import traceback

# Cargar variables de entorno
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # desactiva cache estático
    
    # Configuración de sesiones
    app.config["SESSION_COOKIE_SECURE"] = False  # False para desarrollo HTTP, True para HTTPS
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)  # Máximo 30 días si es permanente

    app.secret_key = os.getenv("SECRET_KEY", "weigence_secret_key_2024")

    # Registrar endpoint de debug
    from .routes.debug import debug_bp
    app.register_blueprint(debug_bp)

    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor inicia sesión para acceder"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        from api.conexion_supabase import supabase
        usuarios = supabase.table("usuarios").select("*").eq("rut_usuario", user_id).execute().data
        return User(usuarios[0]) if usuarios else None

    app.register_blueprint(routes_bp)
    
    # Manejador de errores global para peticiones AJAX
    @app.errorhandler(Exception)
    def handle_error(e):
        """Maneja todos los errores y devuelve JSON para peticiones AJAX"""
        print(f"[ERROR] Excepción no capturada: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        
        # Si es una petición AJAX, devolver JSON
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': f'Error del servidor: {str(e)}'
            }), 500
        
        # Si no, dejar que Flask maneje el error normalmente
        raise

    # Middleware para manejar sesiones no permanentes
    @app.before_request
    def check_session_permanent():
        """
        Control de persistencia de sesión según "Recordarme"
        
        Con "Recordarme" (recordarme_activado=True):
        - session.permanent = True → Duración: PERMANENT_SESSION_LIFETIME (30 días)
        - Cookie persiste incluso después de cerrar navegador
        
        Sin "Recordarme" (recordarme_activado=False):
        - session.permanent = False → Duración: hasta cerrar navegador
        - Cookie se elimina al cerrar navegador
        """
        if session.get("usuario_logueado"):
            # Aplicar regla de persistencia según "Recordarme"
            session.permanent = bool(session.get("recordarme_activado", False))
        
        # Marcar sesión como modificada para que se guarde
        session.modified = True

    # --- Variables globales para templates ---
    @app.context_processor
    def utility_processor():
        return dict(
            usuario_nombre=session.get("usuario_nombre", ""),
            usuario_rol=session.get("usuario_rol", ""),
            usuario_correo=session.get("usuario_correo", "")
        )
    
    # --- Notificaciones globales ---
    @app.context_processor
    def inject_notificaciones():
        try:
            notificaciones, agrupadas = obtener_notificaciones(session.get("usuario_id"))
            return dict(notificaciones=notificaciones, notificaciones_agrupadas=agrupadas)
        except Exception as e:
            print("Error al inyectar notificaciones globales:", e)
            return dict(notificaciones=[], notificaciones_agrupadas={})

    print("Aplicación Weigence iniciada correctamente.")
    return app
