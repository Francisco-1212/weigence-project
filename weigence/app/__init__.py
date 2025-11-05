import os
from flask import Flask, session
from flask_login import LoginManager
from .routes import bp as routes_bp
from .routes.utils import obtener_notificaciones

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # desactiva cache estático
    app.config["REMEMBER_COOKIE_DURATION"] = 2592000  # 30 días en segundos
    app.config["REMEMBER_COOKIE_SECURE"] = True
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True

    app.secret_key = os.getenv("SECRET_KEY", "weigence_secret_key_2024")

    # Inicializar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Por favor inicia sesión para acceder"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        from api.conexion_supabase import supabase
        usuarios = supabase.table("usuarios").select("*").eq("rut_usuario", user_id).execute().data
        return User(usuarios[0]) if usuarios else None

    app.register_blueprint(routes_bp)

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
