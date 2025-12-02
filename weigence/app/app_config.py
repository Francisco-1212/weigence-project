"""
Configuración centralizada de la aplicación Flask
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """Configuración base"""
    
    # ========== SEGURIDAD ==========
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError(
            "ERROR CRÍTICO: SECRET_KEY no configurada. "
            "Genera una con: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    
    # ========== SESIONES ==========
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)
    SESSION_COOKIE_NAME = "weigence_session"  # Nombre único para evitar conflictos
    SESSION_REFRESH_EACH_REQUEST = False  # No regenerar cookie en cada request
    
    # ========== SUPABASE ==========
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configuradas en .env")
    
    # ========== EMAIL ==========
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM", MAIL_USERNAME)
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    
    # ========== RATE LIMITING ==========
    RATELIMIT_STORAGE_URL = os.getenv("RATELIMIT_STORAGE_URL", "memory://")
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # ========== LOGGING ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    
    # ========== APLICACIÓN ==========
    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requiere HTTPS
    TEMPLATES_AUTO_RELOAD = False
    SEND_FILE_MAX_AGE_DEFAULT = 300
    
    # Validar que esté en HTTPS
    if not Config.BASE_URL.startswith("https://"):
        import warnings
        warnings.warn(
            "⚠️  ADVERTENCIA: En producción se recomienda usar HTTPS. "
            "Configura BASE_URL con https:// en .env"
        )


class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False  # Desactivar CSRF en tests


# Mapeo de configuraciones
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_map.get(env, DevelopmentConfig)
