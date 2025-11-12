# 🔐 Sistema de Control de Acceso por Roles - Weigence

## 📋 Resumen

Se ha implementado un sistema completo de gestión de usuarios y control de acceso por roles en Weigence. El sistema restringe las vistas y funciones según el rol del usuario.

## 👥 Roles Disponibles

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| **Farmacéutico** | Personal de farmacia | Dashboard, Inventario, Perfil |
| **Bodeguera** | Personal de bodega | Dashboard, Inventario, Movimientos, Perfil |
| **Supervisor** | Supervisa operaciones | Dashboard, Inventario, Movimientos, Auditoría, Perfil |
| **Jefe** | Gestión total | Dashboard, Inventario, Movimientos, Ventas, Alertas, Auditoría, Usuarios, Perfil |
| **Administrador** | Control total | Todas las secciones |

## 🔓 Control de Acceso

### Decoradores Disponibles

El sistema incluye dos decoradores en `app/routes/decorators.py`:

#### 1. `@requiere_rol(*roles_permitidos)`
Restringe el acceso a usuarios con roles específicos.

```python
from app.routes.decorators import requiere_rol

@bp.route('/usuarios')
@requiere_rol('administrador', 'jefe')
def usuarios():
    # Solo admin y jefe pueden acceder
    pass
```

#### 2. `@requiere_autenticacion`
Simplemente verifica que el usuario esté logueado.

```python
from app.routes.decorators import requiere_autenticacion

@bp.route('/mi-seccion')
@requiere_autenticacion
def mi_seccion():
    # Solo usuarios logueados pueden acceder
    pass
```

### Flujo de Validación

1. Usuario intenta acceder a una ruta protegida
2. Decorador verifica sesión: `session.get('usuario_logueado')`
3. Decorador verifica rol: `session.get('usuario_rol')`
4. Si no tiene permisos:
   - ❌ Para rutas normales: redirige al dashboard
   - ❌ Para APIs: devuelve JSON con error 403

## 👤 Módulo CRUD de Usuarios

### Ubicación
- **Ruta**: `/usuarios`
- **Template**: `app/templates/pagina/usuarios.html`
- **Rutas API**: `app/routes/usuarios.py`
- **Acceso**: Solo **Jefe** y **Administrador**

### Funcionalidades

#### 📖 Ver Usuarios
```bash
GET /api/usuarios
```
Devuelve lista de todos los usuarios.

#### 👁️ Ver Usuario Individual
```bash
GET /api/usuarios/<rut>
```

#### ✨ Crear Usuario
```bash
POST /api/usuarios
Content-Type: application/json

{
  "rut_usuario": "20123456-7",
  "nombre": "Juan Pérez",
  "correo": "juan@example.com",
  "rol": "farmaceutico",
  "numero_celular": "+56912345678",
  "contraseña": "MiContraseña123"
}
```

#### ✏️ Editar Usuario
```bash
PUT /api/usuarios/<rut>
Content-Type: application/json

{
  "nombre": "Juan Pablo Pérez",
  "correo": "juanpablo@example.com",
  "rol": "supervisor",
  "numero_celular": "+56998765432",
  "contraseña": "NuevaContraseña123"  // Opcional: dejar vacío para mantener contraseña actual
}
```

#### 🗑️ Eliminar Usuario
```bash
DELETE /api/usuarios/<rut>
```

### Validaciones

#### Email
- Debe tener formato válido: `usuario@dominio.ext`

#### RUT
- Formato esperado: `XX.XXX.XXX-X` o `XXXXXXXX-X`

#### Rol
Debe ser uno de:
- `farmaceutico`
- `bodeguera`
- `supervisor`
- `jefe`
- `administrador`

#### Duplicados
- No permite crear usuarios con RUT existente
- No permite crear usuarios con email existente

### Restricciones de Eliminación
- Un usuario NO puede eliminarse a sí mismo
- Solo Jefe y Administrador pueden eliminar usuarios

## 🎨 Interfaz de Usuario

### Página de Usuarios

#### Tabla de Usuarios
- Muestra todos los usuarios del sistema
- Campos: RUT, Nombre, Correo, Rol (con color), Teléfono, Fecha Registro
- Roles con colores:
  - 🟣 Administrador (Púrpura)
  - 🔵 Jefe (Azul)
  - 🟡 Supervisor (Amarillo)
  - ⚪ Otros (Gris)

#### Botones de Acción
- ✏️ **Editar**: Abre modal para editar usuario
- 🗑️ **Eliminar**: Elimina usuario con confirmación

#### Modal Crear/Editar
- Campos: RUT, Nombre, Correo, Rol (dropdown), Teléfono, Contraseña
- Validaciones en tiempo real
- Mensajes de éxito/error

## 🔒 Seguridad

### Protección de Datos
- Las contraseñas NO se devuelven en APIs
- Solo Jefe y Administrador pueden acceder a usuarios

### Sesión
- Variables de sesión: `usuario_id`, `usuario_rol`, `usuario_nombre`, `usuario_correo`
- La sesión se valida en cada petición protegida

### Validación de Rol
- Se valida en backend (no solo en frontend)
- Las APIs devuelven 403 si el usuario no tiene permiso

## 📝 Variables de Sesión

```python
session['usuario_logueado']      # bool - Si está autenticado
session['usuario_id']             # str - RUT del usuario
session['usuario_nombre']         # str - Nombre completo
session['usuario_correo']         # str - Email
session['usuario_rol']            # str - Rol actual
session['recordarme_activado']    # bool - Si marcó "Recordarme"
session['usuario_numero_celular'] # str - Teléfono
```

## 🎯 Control en el Sidebar

El sidebar se actualiza dinámicamente según el rol:

```html
<!-- Ejemplo: Inventario solo para roles permitidos -->
{% if session.get('usuario_rol') in ['farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador'] %}
  <a href="{{ url_for('main.inventario') }}">Inventario</a>
{% endif %}
```

## 📊 Permisos por Rol (PERMISOS_POR_ROL)

```python
PERMISOS_POR_ROL = {
    'farmaceutico': ['dashboard', 'inventario', 'perfil'],
    'bodeguera': ['dashboard', 'inventario', 'movimientos', 'perfil'],
    'supervisor': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'perfil'],
    'jefe': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'perfil'],
    'administrador': ['dashboard', 'inventario', 'movimientos', 'auditoria', 'ventas', 'alertas', 'usuarios', 'historial', 'recomendaciones', 'perfil']
}
```

## 🚀 Uso del Sistema

### Para Desarrolladores

#### Proteger una Nueva Ruta
```python
from app.routes.decorators import requiere_rol

@bp.route('/nueva-seccion')
@requiere_rol('administrador', 'jefe')  # Solo para admin y jefe
def nueva_seccion():
    return render_template('nueva_seccion.html')
```

#### Acceder al Rol Actual
```python
from flask import session

rol_actual = session.get('usuario_rol')
usuario_id = session.get('usuario_id')
```

### Para Administradores

1. **Acceder a Usuarios**: Navega a `/usuarios` (solo si eres Jefe o Administrador)
2. **Crear Usuario**: Haz clic en "Nuevo Usuario", completa el formulario
3. **Editar Usuario**: Haz clic en ✏️ en la fila del usuario
4. **Eliminar Usuario**: Haz clic en 🗑️ y confirma
5. **Cambiar Rol**: Al editar, puedes cambiar el rol del usuario

## 🐛 Troubleshooting

### Error: "Acceso denegado"
- Verifica que tu usuario tiene el rol correcto
- Contacta al administrador para solicitar permisos

### Error: "Usuario no encontrado"
- El RUT del usuario no existe en la base de datos
- Verifica que el RUT está bien escrito

### La sección no aparece en el sidebar
- Tu rol no tiene permisos para esa sección
- Pide que cambien tu rol

## 📚 Archivos Relacionados

```
app/
├── routes/
│   ├── __init__.py          # Registra todas las rutas (incluye usuarios)
│   ├── decorators.py        # Decoradores de control de acceso
│   ├── usuarios.py          # CRUD de usuarios
│   └── login.py             # Autenticación y sesión
├── templates/
│   ├── componentes/
│   │   └── sidebar.html     # Sidebar con control de permisos
│   └── pagina/
│       └── usuarios.html    # Página de gestión de usuarios
```

## 🔄 Próximas Mejoras

- [ ] Historial de cambios de permisos
- [ ] Roles personalizados
- [ ] Dos factores de autenticación
- [ ] Auditoría de acciones de usuarios
- [ ] Exportar usuarios a CSV
- [ ] Importar usuarios desde CSV
