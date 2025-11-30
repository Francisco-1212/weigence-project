import os
from flask import Flask, session, jsonify, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

from .routes import bp as routes_bp
from .routes.utils import obtener_notificaciones
from .app_config import get_config
from .utils.logger import setup_logging

load_dotenv()

# Extensiones inicializadas a nivel de m�dulo
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["500 per hour", "100 per minute"],  # limites mas generosos
)

socketio_instance = None


def create_app(config_name=None):
    """Factory para crear la aplicacion Flask."""
    global socketio_instance

    app = Flask(__name__)

    # ========== CONFIGURACION ==========
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    config_class = get_config()
    app.config.from_object(config_class)

    # ========== LOGGING ==========
    logger = setup_logging(
        app=app,
        log_file=app.config.get("LOG_FILE", "app.log"),
        log_level=app.config.get("LOG_LEVEL", "INFO"),
    )

    logger.info("=" * 60)
    logger.info(f"Weigence Inventory - Modo: {config_name.upper()}")
    logger.info("=" * 60)

    from app.chat.chat_api import bp_chat

    app.register_blueprint(bp_chat)

    # ========== EXTENSIONES DE SEGURIDAD ==========
    
    # Configurar custom exempt decision
    def is_api_route():
        """Verifica si es una ruta API que debe estar exenta de CSRF"""
        path = request.path
        exempt_prefixes = ["/api/chat/", "/api/usuarios", "/api/auditoria", "/password-reset", "/api/validate-reset-token", "/api/reset-password"]
        
        for prefix in exempt_prefixes:
            if prefix.endswith("/"):
                if path.startswith(prefix):
                    return True
            else:
                if path == prefix or path.startswith(prefix + "/"):
                    return True
        return False
    
    # Inicializar CSRF con verificación custom
    app.config['WTF_CSRF_CHECK_DEFAULT'] = True
    csrf._exempt_views = set()
    csrf._exempt_blueprints = set()
    
    # Override el método protect de CSRF
    original_protect = csrf.protect
    def custom_protect():
        if is_api_route():
            logger.info(f"[CSRF-EXEMPT] Ruta {request.path} exenta de CSRF")
            return None
        logger.debug(f"[CSRF-PROTECTED] Verificando CSRF para {request.path}")
        return original_protect()
    
    csrf.protect = custom_protect
    csrf.init_app(app)
    logger.info("CSRF Protection activado con excepciones para API")

    limiter.init_app(app)
    logger.info("Rate Limiting configurado")

    # Registrar endpoint de debug (solo en desarrollo)
    if app.config.get("DEBUG"):
        try:
            from .routes.debug import debug_bp

            app.register_blueprint(debug_bp)
            csrf.exempt(debug_bp)
            logger.info("Endpoints de debug registrados")
        except ImportError:
            logger.warning("No se pudo cargar modulo debug")

    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor inicia sesion para acceder"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        from api.conexion_supabase import supabase

        usuarios = supabase.table("usuarios").select("*").eq("rut_usuario", user_id).execute().data
        return User(usuarios[0]) if usuarios else None

    app.register_blueprint(routes_bp)

    # Exentar rutas especificas de CSRF
    @csrf.exempt
    @app.route("/password-reset", methods=["POST"])
    def csrf_exempt_password_reset():
        from app.routes.login import password_reset

        return password_reset()

    @csrf.exempt
    @app.route("/api/validate-reset-token", methods=["POST"])
    def csrf_exempt_validate_token():
        from app.routes.login import validate_reset_token

        return validate_reset_token()

    @csrf.exempt
    @app.route("/api/reset-password", methods=["POST"])
    def csrf_exempt_reset_password():
        from app.routes.login import reset_password_submit

        return reset_password_submit()

    logger.info("Rutas de recuperacion de contrasena exentas de CSRF (metodo wrapper)")

    # ========== SOCKETIO (CHAT TIEMPO REAL) ==========
    try:
        from .chat.sockets.chat_ws import init_socketio

        socketio_instance = init_socketio(app)
        logger.info("WebSocket (SocketIO) configurado para chat")
    except ImportError as e:
        logger.warning(f"SocketIO no disponible: {e}")
        logger.warning("Chat funcionara sin tiempo real (solo polling)")
    except Exception as e:
        logger.error(f"Error al inicializar SocketIO: {e}")

    @app.errorhandler(Exception)
    def handle_error(e):
        """Maneja todos los errores y devuelve JSON para peticiones AJAX."""
        logger.error(f"Excepcion no capturada: {str(e)}", exc_info=True)

        if request.path.startswith("/api/"):
            error_msg = "Error del servidor" if not app.config.get("DEBUG") else f"Error: {str(e)}"
            return jsonify({"success": False, "error": error_msg}), 500

        raise

    @app.before_request
    def check_session_permanent():
        """Control de persistencia de sesion segun "Recordarme"."""
        if session.get("usuario_logueado"):
            session.permanent = bool(session.get("recordarme_activado", False))
        session.modified = True

    @app.context_processor
    def utility_processor():
        return dict(
            usuario_nombre=session.get("usuario_nombre", ""),
            usuario_rol=session.get("usuario_rol", ""),
            usuario_correo=session.get("usuario_correo", ""),
        )

    @app.context_processor
    def inject_notificaciones():
        try:
            notificaciones, agrupadas = obtener_notificaciones(session.get("usuario_id"))
            return dict(notificaciones=notificaciones, notificaciones_agrupadas=agrupadas)
        except Exception as e:
            logger.error(f"Error al inyectar notificaciones globales: {e}")
            return dict(notificaciones=[], notificaciones_agrupadas={})

    logger.info("Aplicacion Weigence iniciada correctamente")
    logger.info("=" * 60)
    return app


csrf = csrf
