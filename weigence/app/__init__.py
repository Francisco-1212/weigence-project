import os
from flask import Flask, session, jsonify, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .routes import bp as routes_bp
from .routes.utils import obtener_notificaciones
from flask import Blueprint
from datetime import timedelta
from dotenv import load_dotenv
import traceback

# Cargar configuración y logging
from .app_config import get_config
from .utils.logger import setup_logging, get_logger

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones (a nivel de módulo para que puedan importarse)
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["500 per hour", "100 per minute"]  # Límites más generosos
)

# SocketIO se importa e inicializa más abajo
socketio_instance = None

def create_app(config_name=None):
    """
    Factory para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración ('development', 'production', 'testing')
    """
    global socketio_instance
    
    app = Flask(__name__)
    
    # ========== CARGAR CONFIGURACIÓN ==========
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    config_class = get_config()
    app.config.from_object(config_class)
    
    # ========== CONFIGURAR LOGGING ==========
    logger = setup_logging(
        app=app,
        log_file=app.config.get('LOG_FILE', 'app.log'),
        log_level=app.config.get('LOG_LEVEL', 'INFO')
    )
    
    logger.info("="*60)
    logger.info(f"🚀 Weigence Inventory - Modo: {config_name.upper()}")
    logger.info("="*60)
    
    # ========== INICIALIZAR EXTENSIONES DE SEGURIDAD ==========
    # CSRF Protection
    csrf.init_app(app)
    logger.info("✓ CSRF Protection activado")
    
    # Exentar rutas de API de chat y password-reset del CSRF
    @app.before_request
    def bypass_csrf_for_chat_api():
        exempt_paths = [
            '/api/chat/',
            '/password-reset',
            '/api/validate-reset-token',
            '/api/reset-password'
        ]
        
        # Log de debug para ver todas las rutas que llegan
        logger.debug(f"[CSRF-CHECK] Ruta: {request.path} | Método: {request.method}")
        
        # Verificar si la ruta debe estar exenta
        is_exempt = any(
            request.path.startswith(path) if path.endswith('/') else request.path == path 
            for path in exempt_paths
        )
        
        if is_exempt:
            from flask import g
            g._csrf_exempt = True
            logger.info(f"[CSRF-EXEMPT] ✓ Ruta {request.path} exenta de CSRF")
        else:
            logger.debug(f"[CSRF-PROTECTED] Ruta {request.path} requiere CSRF")
    
    logger.info("✓ Rutas /api/chat/*, /password-reset y /api/validate-reset-token exentas de CSRF")
    
    # Rate Limiting
    limiter.init_app(app)
    logger.info("✓ Rate Limiting configurado")
    
    # Registrar endpoint de debug (solo en desarrollo)
    if app.config.get("DEBUG"):
        try:
            from .routes.debug import debug_bp
            app.register_blueprint(debug_bp)
            csrf.exempt(debug_bp)
            logger.info("✓ Endpoints de debug registrados")
        except ImportError:
            logger.warning("⚠️  No se pudo cargar módulo debug")

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
    
    # Exentar rutas específicas de CSRF después de registrar el blueprint
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
    
    logger.info("✓ Rutas de recuperación de contraseña exentas de CSRF (método wrapper)")
    
    # ========== INICIALIZAR SOCKETIO (CHAT TIEMPO REAL) ==========
    try:
        from .sockets.chat_ws import init_socketio, registrar_eventos_socket
        socketio_instance = init_socketio(app)
        registrar_eventos_socket()
        logger.info("✓ WebSocket (SocketIO) configurado para chat")
    except ImportError as e:
        logger.warning(f"⚠️  SocketIO no disponible: {e}")
        logger.warning("⚠️  Chat funcionará sin tiempo real (solo polling)")
    except Exception as e:
        logger.error(f"❌ Error al inicializar SocketIO: {e}")
    
    @app.errorhandler(Exception)
    def handle_error(e):
        """Maneja todos los errores y devuelve JSON para peticiones AJAX"""
        logger.error(f"Excepción no capturada: {str(e)}", exc_info=True)
        
        # Si es una petición AJAX, devolver JSON
        if request.path.startswith('/api/'):
            # No exponer detalles en producción
            error_msg = 'Error del servidor' if not app.config.get("DEBUG") else f'Error: {str(e)}'
            return jsonify({
                'success': False,
                'error': error_msg
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
            logger.error(f"Error al inyectar notificaciones globales: {e}")
            return dict(notificaciones=[], notificaciones_agrupadas={})

    logger.info("✅ Aplicación Weigence iniciada correctamente")
    logger.info("="*60)
    return app
