from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get("rut_usuario")
        self.nombre = user_data.get("nombre")
        self.rol = user_data.get("rol")
        self.correo = user_data.get("correo")