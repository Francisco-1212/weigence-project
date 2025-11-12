# 🚀 Guía Rápida - Sistema de Roles y Usuarios

## ⚡ Lo Más Importante

### Los 5 Roles
```
👨‍⚕️  Farmacéutico  → Dashboard, Inventario
📦 Bodeguera     → Dashboard, Inventario, Movimientos
👔 Supervisor    → Dashboard, Inventario, Movimientos, Auditoría
👨‍💼 Jefe         → TODOS + Gestión de Usuarios ⭐
🔑 Administrador → TODOS + Gestión de Usuarios ⭐
```

### ¿Dónde está el módulo de Usuarios?
**Ruta**: `/usuarios` (solo visible en sidebar para Jefe y Admin)

### ¿Cómo crear un usuario desde la interfaz?
1. Navega a `/usuarios`
2. Haz clic en "Nuevo Usuario" 🟦
3. Completa el formulario
4. Haz clic en "Guardar"

### ¿Cómo proteger una ruta nueva?
```python
from app.routes.decorators import requiere_rol

@bp.route('/mi-ruta')
@requiere_rol('administrador', 'jefe')
def mi_ruta():
    return render_template('mi_template.html')
```

## 📂 Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `app/routes/decorators.py` | Decoradores de permisos |
| `app/routes/usuarios.py` | CRUD de usuarios |
| `app/templates/pagina/usuarios.html` | Interfaz de usuarios |
| `app/templates/componentes/sidebar.html` | Sidebar dinámico |

## 🔌 Endpoints API

```
GET    /api/usuarios           → Listar todos
GET    /api/usuarios/<rut>     → Obtener uno
POST   /api/usuarios           → Crear
PUT    /api/usuarios/<rut>     → Editar
DELETE /api/usuarios/<rut>     → Eliminar
```

## 📝 Ejemplo: Crear usuario por API

```bash
curl -X POST http://localhost:5000/api/usuarios \
  -H "Content-Type: application/json" \
  -d '{
    "rut_usuario": "20123456-7",
    "nombre": "Juan",
    "correo": "juan@example.com",
    "rol": "farmaceutico",
    "numero_celular": "+56912345678",
    "contraseña": "Pass123"
  }'
```

## 🔑 Variables de Sesión

```python
session['usuario_id']           # RUT
session['usuario_nombre']       # Nombre
session['usuario_correo']       # Email
session['usuario_rol']          # Rol actual
session['usuario_logueado']     # True/False
session['recordarme_activado']  # True/False
```

## ⚙️ Configuración de Permisos

Archivo: `app/routes/usuarios.py`

```python
PERMISOS_POR_ROL = {
    'farmaceutico': ['dashboard', 'inventario', 'perfil'],
    'bodeguera': ['dashboard', 'inventario', 'movimientos', 'perfil'],
    'supervisor': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'perfil'],
    'jefe': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'perfil'],
    'administrador': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil']
}
```

## 🎯 Validaciones

- ✅ Email: `usuario@dominio.ext`
- ✅ RUT: `XX.XXX.XXX-X`
- ✅ Rol: Solo valores permitidos
- ✅ No duplicados: RUT y email únicos

## 🐛 Errores Comunes

**Error: "Acceso denegado"**
→ Tu rol no tiene permiso. Pide que cambien tu rol.

**Error: "Usuario no encontrado"**
→ El RUT no existe. Verifica que esté bien escrito.

**No veo "Usuarios" en el sidebar**
→ Tu rol no es Jefe ni Administrador.

## 💻 Para Desarrolladores

### Agregar nueva sección con control de rol
```python
@bp.route('/nueva-seccion')
@requiere_rol('administrador')  # Solo admin
def nueva_seccion():
    return render_template('nueva_seccion.html')
```

### Agregar opción en sidebar
```html
{% if session.get('usuario_rol') in ['administrador'] %}
  <a href="{{ url_for('main.nueva_seccion') }}">
    <span class="material-symbols-outlined">icon_name</span>
    <span>Nueva Sección</span>
  </a>
{% endif %}
```

## 📞 Soporte

- 📖 Documentación completa: `SISTEMA_ROLES_USUARIOS.md`
- 📋 Implementación: `IMPLEMENTACION_COMPLETADA.md`
- 🐍 Código fuente: `app/routes/usuarios.py`
