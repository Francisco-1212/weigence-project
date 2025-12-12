import os
from flask import Flask, session, jsonify, request, redirect, url_for
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

# Extensiones inicializadas a nivel de módulo
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    default_limits=["10000 per hour", "500 per minute"],  # Límites muy altos para desarrollo
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
        exempt_prefixes = [
            "/",  # Login - exento de CSRF
            "/login",  # Login alternativo
            "/api/chat/", 
            "/api/usuarios", 
            "/api/auditoria", 
            "/password-reset", 
            "/api/validate-reset-token", 
            "/api/reset-password",
            "/api/lecturas_peso_recientes",  # Sistema automático de detección de peso
            "/api/lecturas_peso_pendientes",  # Recuperación de movimientos perdidos
            "/api/movimientos/gris"  # Movimientos grises automáticos
        ]
        
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

    # ========== SEGURIDAD: Headers anti-caché para páginas protegidas ==========
    @app.after_request
    def add_security_headers(response):
        """
        Agrega headers de seguridad para prevenir caché en páginas protegidas.
        Esto evita que usuarios puedan usar botones atrás/adelante después de logout.
        """
        # Solo aplicar a páginas HTML (no APIs, static files, etc)
        if response.content_type and 'text/html' in response.content_type:
            # Verificar si es una página protegida (que requiere login)
            if 'usuario_logueado' in session:
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0, post-check=0, pre-check=0'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '-1'
                # Header adicional para prevenir bfcache en navegadores modernos
                response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
    
    @app.before_request
    def validate_session_on_protected_routes():
        """
        Valida la sesión antes de cada request a rutas protegidas.
        Fuerza logout si la sesión está corrupta o inválida.
        """
        # Excluir rutas públicas y archivos estáticos
        public_routes = [
            '/login', 
            '/logout', 
            '/password-reset', 
            '/static', 
            '/api/reset-password', 
            '/api/validate-reset-token',
            '/api/validate-session'  # Agregar validación de sesión
        ]
        
        if any(request.path.startswith(route) for route in public_routes):
            return None
        
        # Si hay "intento" de sesión pero está incompleta, forzar limpieza
        # SOLO si no es una petición AJAX o API
        if session.get('usuario_logueado') and not request.path.startswith('/api/'):
            if not session.get('usuario_id') or not session.get('usuario_nombre'):
                logger.warning(f"[SECURITY] Sesión corrupta detectada en {request.path} - forzando logout")
                session.clear()
                return redirect(url_for('main.login'))
        
        return None
    
    logger.info("Headers de seguridad anti-caché configurados")

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
    
    # Registrar blueprint de pruebas (solo desarrollo)
    from app.routes.test_routes import bp as test_bp
    app.register_blueprint(test_bp)

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

    @csrf.exempt
    @app.route("/api/inventario/exportar-excel", methods=["POST"])
    def csrf_exempt_exportar_inventario():
        from app.routes.inventario import exportar_inventario_excel
        return exportar_inventario_excel()

    @csrf.exempt
    @app.route("/api/ventas/exportar-excel", methods=["POST"])
    def csrf_exempt_exportar_ventas():
        from app.routes.ventas import exportar_ventas_excel
        return exportar_ventas_excel()

    logger.info("Rutas de recuperacion de contrasena exentas de CSRF (metodo wrapper)")

    # ========== SOCKETIO (CHAT TIEMPO REAL) ==========
    try:
        from .chat.sockets.chat_ws import init_socketio

        socketio_instance = init_socketio(app)
        logger.info("WebSocket (SocketIO) configurado para chat")
        
        # Configurar logging de engineio/socketio para ser menos verboso
        import logging
        
        # Suprimir logs de sesiones inválidas (nivel ERROR)
        logging.getLogger('socketio').setLevel(logging.CRITICAL)
        logging.getLogger('engineio').setLevel(logging.CRITICAL)
        logging.getLogger('engineio.server').setLevel(logging.CRITICAL)
        
    except ImportError as e:
        logger.warning(f"SocketIO no disponible: {e}")
        logger.warning("Chat funcionara sin tiempo real (solo polling)")
    except Exception as e:
        logger.error(f"Error al inicializar SocketIO: {e}")

    @app.errorhandler(404)
    def handle_404(e):
        """Log para 404 mostrando la URL solicitada solo para rutas no comunes"""
        # Ignorar 404s comunes de archivos estáticos, favicon y SocketIO polling
        ignore_paths = [
            '/favicon.ico', 
            '/robots.txt', 
            '/sitemap.xml', 
            '.map',
            '/socket.io/',  # Rutas de SocketIO (polling fallback)
            '/static/uploads/profile_pictures/',  # Fotos de perfil faltantes (común)
        ]
        
        # Loguear con más detalle para diagnosticar problemas
        should_log = not any(path in request.path for path in ignore_paths)
        
        if should_log:
            # Capturar información adicional para diagnóstico
            headers_info = f"Referer: {request.referrer}" if request.referrer else "Sin referer"
            logger.warning(f"⚠️ 404: {request.method} {request.path} | {headers_info} | Query: {dict(request.args)}")
        
        # Manejar imágenes de perfil faltantes - redirigir a generador de avatar
        if '/static/uploads/profile_pictures/' in request.path:
            # Extraer el RUT del nombre del archivo si es posible
            import re
            rut_match = re.search(r'/(\d+-\d+)_', request.path)
            if rut_match:
                rut = rut_match.group(1)
                # Usar UI Avatars con el RUT como inicial
                initials = rut[:2].upper()
                avatar_url = f"https://ui-avatars.com/api/?name={initials}&background=4F46E5&color=fff&size=200&bold=true"
                return redirect(avatar_url)
            # Si no hay RUT, usar avatar genérico
            return redirect("https://ui-avatars.com/api/?name=U&background=4F46E5&color=fff&size=200&bold=true")
        
        # Siempre devolver una respuesta limpia sin stack trace
        if request.path.startswith("/api/") or request.is_json or request.accept_mimetypes.best == 'application/json':
            return jsonify({"success": False, "error": "Endpoint no encontrado"}), 404
        
        # Para navegación normal, redirigir a página de error o home
        from flask import render_template
        try:
            return render_template('errors/404.html'), 404
        except:
            # Si no hay template de error, redirigir al dashboard
            return redirect(url_for('main.dashboard'))

    @app.errorhandler(Exception)
    def handle_error(e):
        """Maneja todos los errores y devuelve JSON para peticiones AJAX."""
        # No loguear errores 404 como excepciones críticas
        from werkzeug.exceptions import NotFound, HTTPException
        from flask_wtf.csrf import CSRFError
        
        if isinstance(e, NotFound):
            return handle_404(e)
        
        # Manejar errores CSRF de forma especial
        if isinstance(e, CSRFError):
            logger.warning(f"[CSRF] Error de validación CSRF en {request.path}: {str(e)}")
            # Si es el login, redirigir para refrescar el token
            if request.path == "/" or request.path == "/login":
                flash("Tu sesión ha expirado. Por favor, inicia sesión nuevamente.", "warning")
                return redirect(url_for('main.login'))
            # Para otras rutas, si es API devolver JSON, si no mostrar error
            if request.path.startswith("/api/") or request.is_json:
                return jsonify({"success": False, "error": "Token de seguridad inválido. Recarga la página."}), 400
            flash("Token de seguridad inválido. Por favor, recarga la página.", "error")
            return redirect(url_for('main.dashboard'))
        
        # Suprimir logs de otros errores HTTP esperados (400, 403, etc.)
        if isinstance(e, HTTPException):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": e.description}), e.code
            raise
        
        # Solo loguear excepciones reales, no errores HTTP esperados
        logger.error(f"Excepcion no capturada: {str(e)}", exc_info=False)

        if request.path.startswith("/api/"):
            error_msg = "Error del servidor" if not app.config.get("DEBUG") else f"Error: {str(e)}"
            return jsonify({"success": False, "error": error_msg}), 500

        raise

    @app.before_request
    def check_session_permanent():
        """Control de persistencia de sesion segun "Recordarme"."""
        if session.get("usuario_logueado"):
            # Solo configurar permanencia si no está ya configurada
            should_be_permanent = bool(session.get("recordarme_activado", False))
            if session.permanent != should_be_permanent:
                session.permanent = should_be_permanent
                session.modified = True  # Solo marcar como modificada cuando cambia

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
