from app import create_app, socketio_instance
from livereload import Server
import sys

app = create_app()


def serve_with_retry(server: Server, host: str = "127.0.0.1", start_port: int = 5000, max_tries: int = 10):
    """Intenta iniciar el servidor en start_port y, si el puerto está en uso,
    prueba puertos consecutivos hasta max_tries. Si falla todos, sale con código 1.
    Esto evita que la app termine con OSError cuando ya hay otra instancia corriendo.
    """
    port = start_port
    for _ in range(max_tries):
        try:
            print(f"Iniciando servidor en http://{host}:{port}")
            
            # Si SocketIO está disponible, usarlo para servir
            if socketio_instance:
                print("🔥 Modo: Flask + SocketIO (WebSocket habilitado)")
                socketio_instance.run(app, host=host, port=port, debug=True, allow_unsafe_werkzeug=True)
            else:
                print("⚠️  Modo: Flask sin WebSocket")
                server.serve(port=port, host=host, debug=True)
            
            return
        except OSError as e:
            # WinError 10048 -> address already in use on Windows
            if getattr(e, "winerror", None) == 10048 or "Address already in use" in str(e):
                print(f"Puerto {port} en uso, intentando puerto {port + 1}...")
                port += 1
                continue
            # re-raise otros errores
            raise


if __name__ == "__main__":
    # Si NO hay SocketIO, usar livereload normal
    if not socketio_instance:
        server = Server(app.wsgi_app)
        server.watch("app/templates/**/*.*")
        server.watch("app/static/**/*.*")
        server.watch("app/routes/**/*.py")
        serve_with_retry(server, host="127.0.0.1", start_port=5000, max_tries=10)
    else:
        # Con SocketIO, servir directamente (livereload no compatible con socketio.run)
        try:
            socketio_instance.run(app, host="127.0.0.1", port=5000, debug=True, allow_unsafe_werkzeug=True)
        except OSError as e:
            if getattr(e, "winerror", None) == 10048:
                print("Puerto 5000 en uso, intentando 5001...")
                socketio_instance.run(app, host="127.0.0.1", port=5001, debug=True, allow_unsafe_werkzeug=True)
            else:
                raise

