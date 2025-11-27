import os

import app as app_package
from livereload import Server

app = app_package.create_app()
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")  # Usa 0.0.0.0 para compartir por red/Live Share
APP_PORT = int(os.getenv("APP_PORT", "5000"))
APP_MAX_TRIES = int(os.getenv("APP_PORT_RETRIES", "10"))


def serve_with_retry(server: Server, host: str = "127.0.0.1", start_port: int = 5000, max_tries: int = 10):
    """Intenta iniciar el servidor en start_port y avanza si el puerto esta en uso."""
    port = start_port
    for _ in range(max_tries):
        try:
            print(f"Iniciando servidor en http://{host}:{port}")
            sio = app_package.socketio_instance
            if sio:
                print("Modo: Flask + SocketIO (WebSocket habilitado)")
                sio.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
            else:
                print("Modo: Flask sin WebSocket")
                server.serve(port=port, host=host, debug=True)
            return
        except OSError as e:
            if getattr(e, "winerror", None) == 10048 or "Address already in use" in str(e):
                print(f"Puerto {port} en uso, intentando puerto {port + 1}...")
                port += 1
                continue
            raise


def serve_socketio_with_retry(sio, flask_app, host: str, start_port: int, max_tries: int):
    """Lanza SocketIO con reintentos si el puerto esta en uso."""
    port = start_port
    for _ in range(max_tries):
        try:
            print(f"Iniciando servidor (SocketIO) en http://{host}:{port}")
            sio.run(flask_app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
            return
        except OSError as e:
            if getattr(e, "winerror", None) == 10048 or "Address already in use" in str(e):
                print(f"Puerto {port} en uso, intentando puerto {port + 1}...")
                port += 1
                continue
            raise


if __name__ == "__main__":
    sio = app_package.socketio_instance
    if not sio:
        server = Server(app.wsgi_app)
        server.watch("app/templates/**/*.*")
        server.watch("app/static/**/*.*")
        server.watch("app/routes/**/*.py")
        serve_with_retry(server, host=APP_HOST, start_port=APP_PORT, max_tries=APP_MAX_TRIES)
    else:
        serve_socketio_with_retry(sio, app, host=APP_HOST, start_port=APP_PORT, max_tries=APP_MAX_TRIES)
