from app import create_app
from livereload import Server

app = create_app()

if __name__ == "__main__":
    server = Server(app.wsgi_app)
    server.watch("app/templates/**/*.*")     # recarga al cambiar HTML/Jinja
    server.watch("app/static/**/*.*")        # recarga al cambiar CSS/JS
    server.watch("app/routes/**/*.py")  # recarga al cambiar rutas
    server.serve(port=5000, host="127.0.0.1", debug=True)

