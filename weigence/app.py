from app import create_app
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
    server = Server(app.wsgi_app)
    server.watch("app/templates/**/*.*")     # recarga al cambiar HTML/Jinja
    server.watch("app/static/**/*.*")        # recarga al cambiar CSS/JS
    server.watch("app/routes/**/*.py")  # recarga al cambiar rutas
    # Intentar arrancar evitando crash si el puerto 5000 ya está en uso
    serve_with_retry(server, host="127.0.0.1", start_port=5000, max_tries=10)

