import app as app_package
from livereload import Server

app = app_package.create_app()


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


if __name__ == "__main__":
    sio = app_package.socketio_instance
    if not sio:
        server = Server(app.wsgi_app)
        server.watch("app/templates/**/*.*")
        server.watch("app/static/**/*.*")
        server.watch("app/routes/**/*.py")
        serve_with_retry(server, host="127.0.0.1", start_port=5000, max_tries=10)
    else:
        try:
            sio.run(app, host="127.0.0.1", port=5000, debug=True, allow_unsafe_werkzeug=True)
        except OSError as e:
            if getattr(e, "winerror", None) == 10048:
                print("Puerto 5000 en uso, intentando 5001...")
                sio.run(app, host="127.0.0.1", port=5001, debug=True, allow_unsafe_werkzeug=True)
            else:
                raise
