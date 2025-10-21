import os
from flask import Flask, session
from .routes import bp as routes_bp
from .routes.utils import obtener_notificaciones

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "weigence_secret_key_2024")

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
