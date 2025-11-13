# 🔐 Documentación Completa: Sistema de Roles y Control de Acceso - Weigence

## 📋 Índice
1. [Visión General](#visión-general)
2. [Roles Disponibles](#roles-disponibles)
3. [Permisos por Rol](#permisos-por-rol)
4. [Flujo de Autenticación](#flujo-de-autenticación)
5. [Protección de Rutas](#protección-de-rutas)
6. [Implementación Técnica](#implementación-técnica)
7. [Ejemplos de Uso](#ejemplos-de-uso)
8. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## 🎯 Visión General

Weigence implementa un sistema robusto de **control de acceso basado en roles (RBAC)** que asegura que:

✅ **Los usuarios solo ven secciones permitidas** para su rol  
✅ **Las APIs rechazarán solicitudes no autorizadas**  
✅ **La sesión valida permisos en cada petición**  
✅ **El frontend y backend están sincronizados**  

---

## 👥 Roles Disponibles

### 1. 💊 **Farmacéutico**
- **Descripción**: Personal de farmacia
- **Acceso**: Solo lectura de inventario
- **Funciones principales**:
  - Ver dashboard
  - Consultar inventario (stock, vencimientos, información básica)
  - Registrar ventas
  - Ver información de productos

### 2. 📦 **Bodeguera**
- **Descripción**: Personal de bodega
- **Acceso**: Gestión de movimientos e inventario
- **Funciones principales**:
  - Ver dashboard
  - Crear/editar productos
  - Registrar entrada y salida de productos
  - Ver alertas de pesas inteligentes
  - Actualizar stock

### 3. 👔 **Supervisor**
- **Descripción**: Supervisión de operaciones
- **Acceso**: Bodeguera + Auditoría
- **Funciones principales**:
  - Todas las de Bodeguera
  - Ver auditoría del sistema
  - Ver historial de cambios
  - Generar reportes
  - Monitoreo general

### 4. 👨‍💼 **Jefe**
- **Descripción**: Gestión total del sistema
- **Acceso**: Todas las secciones incluyendo gestión de usuarios
- **Funciones principales**:
  - Todas las funciones del sistema
  - ⭐ **Crear, editar, eliminar usuarios**
  - ⭐ **Asignar y cambiar roles**
  - Ver reportes de ventas
  - Acceder a recomendaciones IA
  - Gestión completa de inventario

### 5. 🔑 **Administrador**
- **Descripción**: Control total del sistema
- **Acceso**: Todas las secciones sin restricciones
- **Funciones principales**:
  - ✓ Todas las funciones disponibles
  - ✓ Gestión de usuarios (crear, editar, eliminar)
  - ✓ Asignar y cambiar roles
  - ✓ Exportar reportes (futuro)
  - ✓ Configuración de IA
  - ✓ Acceso a historial completo

---

## 📊 Permisos por Rol

### Matriz de Acceso a Secciones

| Sección | Farmacéutico | Bodeguera | Supervisor | Jefe | Admin |
|---------|:---:|:---:|:---:|:---:|:---:|
| Dashboard | ✓ | ✓ | ✓ | ✓ | ✓ |
| Inventario | ✓* | ✓ | ✓ | ✓ | ✓ |
| Movimientos | ✗ | ✓ | ✓ | ✓ | ✓ |
| Alertas | ✗ | ✓ | ✓ | ✓ | ✓ |
| Ventas | ✗ | ✗ | ✗ | ✓ | ✓ |
| Auditoría | ✗ | ✗ | ✓ | ✓ | ✓ |
| Usuarios | ✗ | ✗ | ✗ | ✓ | ✓ |
| Historial | ✗ | ✗ | ✗ | ✓ | ✓ |
| Recomendaciones IA | ✗ | ✗ | ✗ | ✓ | ✓ |
| Perfil | ✓ | ✓ | ✓ | ✓ | ✓ |

*Farmacéutico: Solo lectura  
✓ = Acceso completo  
✗ = Sin acceso

---

## 🔄 Flujo de Autenticación

```
┌─────────────────────────────────────────────────────────────┐
│                  1. Usuario intenta LOGIN                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────────┐
         │ Validar credenciales
         │ en Supabase       │
         └───────┬───────────┘
                 │
         ┌───────▼───────┐
         │ ¿Válido?      │
         └───┬───────┬───┘
             │       │
        SÍ  │       │ NO
            ▼       ▼
         ┌──────────────────────┐
         │ Guardar en sesión:   │
         │ - usuario_logueado   │
         │ - usuario_id (RUT)   │
         │ - usuario_rol ⭐     │
         │ - usuario_nombre     │
         │ - usuario_correo     │
         └──────┬───────────────┘
                │
                ▼
      ┌──────────────────────┐
      │ Redirect a dashboard │
      └──────────────────────┘
```

---

## 🛡️ Protección de Rutas

### Todos los endpoints están protegidos con decoradores

```python
# ✅ CORRECTO - Todas las rutas están protegidas

@bp.route("/dashboard")
@requiere_rol('farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador')
def dashboard():
    return render_template('pagina/index.html')

@bp.route("/usuarios")
@requiere_rol('administrador', 'jefe')  # Solo Jefe y Admin
def usuarios():
    return render_template('pagina/usuarios.html')

@bp.route("/api/usuarios", methods=['POST'])
@requiere_rol('administrador', 'jefe')  # Solo para crear usuarios
def api_crear_usuario():
    # Crear nuevo usuario
    pass
```

### Decoradores Disponibles

#### 1. `@requiere_rol(*roles_permitidos)`
Protege acceso a usuarios con roles específicos

```python
@bp.route('/mi-ruta')
@requiere_rol('jefe', 'administrador')
def mi_ruta():
    """Solo jefe y admin pueden acceder"""
    return "Acceso permitido"
```

#### 2. `@requiere_autenticacion`
Protege acceso solo verificando que el usuario está logueado

```python
@bp.route('/mi-ruta')
@requiere_autenticacion
def mi_ruta():
    """Cualquier usuario logueado puede acceder"""
    return "Acceso permitido"
```

#### 3. `@puede_realizar_accion(seccion, accion)`
Valida acciones específicas en secciones

```python
@bp.route('/usuarios/<rut>', methods=['DELETE'])
@puede_realizar_accion('usuarios', 'eliminar')
def eliminar_usuario(rut):
    """Solo usuarios con permiso de eliminar en usuarios"""
    pass
```

---

## 🔧 Implementación Técnica

### Estructura de Archivos

```
app/
├── config/
│   └── roles_permisos.py          # ⭐ Configuración centralizada
├── routes/
│   ├── decorators.py              # ⭐ Decoradores de protección
│   ├── login.py                   # Autenticación
│   ├── dashboard.py               # @requiere_rol
│   ├── inventario.py              # @requiere_rol
│   ├── movimientos.py             # @requiere_rol
│   ├── ventas.py                  # @requiere_rol
│   ├── alertas.py                 # @requiere_rol
│   ├── auditoria.py               # @requiere_rol
│   ├── usuarios.py                # @requiere_rol
│   └── ...
└── templates/
    ├── login.html                 # Con info de roles
    ├── componentes/
    │   └── sidebar.html           # Menú dinámico por rol
    └── pagina/
        └── usuarios.html          # Solo visible para Jefe/Admin
```

### Archivo de Configuración: `app/config/roles_permisos.py`

```python
ROLES_DISPONIBLES = [
    'farmaceutico',
    'bodeguera',
    'supervisor',
    'jefe',
    'administrador'
]

PERMISOS_POR_ROL = {
    'farmaceutico': ['dashboard', 'inventario', 'perfil'],
    'bodeguera': ['dashboard', 'inventario', 'movimientos', 'alertas', 'perfil'],
    'supervisor': ['dashboard', 'inventario', 'movimientos', 'alertas', 'auditoria', 'perfil'],
    'jefe': ['dashboard', 'inventario', 'movimientos', 'alertas', 'auditoria', 'ventas', 'usuarios', 'historial', 'recomendaciones', 'perfil'],
    'administrador': ['dashboard', 'inventario', 'movimientos', 'alertas', 'auditoria', 'ventas', 'usuarios', 'historial', 'recomendaciones', 'perfil']
}

ACCIONES_POR_ROL = {
    'farmaceutico': {
        'inventario': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False},
        'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False}
    },
    'bodeguera': {
        'inventario': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False},
        'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False}
    },
    # ...
    'jefe': {
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'asignar_rol': True},
        # ...
    },
    'administrador': {
        'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'asignar_rol': True},
        # ...
    }
}
```

### Cómo Funciona en Backend

```python
# En decorators.py

def requiere_rol(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1️⃣ Verificar que está logueado
            if not session.get('usuario_logueado'):
                flash('Por favor inicia sesión', 'error')
                return redirect(url_for('main.login'))
            
            # 2️⃣ Obtener rol del usuario
            rol_usuario = session.get('usuario_rol', '').lower()
            
            # 3️⃣ Verificar que el rol está permitido
            if rol_usuario not in roles_permitidos:
                flash('Acceso denegado', 'error')
                
                # Si es AJAX → JSON
                if request.is_json:
                    return jsonify({'error': 'Acceso denegado'}), 403
                
                # Si es navegador → redirect
                return redirect(url_for('main.dashboard'))
            
            # 4️⃣ Permitir acceso
            return f(*args, **kwargs)
        
        return decorated_function
    return decorador
```

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Proteger una página HTML

```python
# app/routes/usuarios.py

@bp.route('/usuarios')
@requiere_rol('administrador', 'jefe')
def usuarios():
    """Solo admin y jefe pueden ver esta página"""
    usuarios = supabase.table("usuarios").select("*").execute().data
    return render_template('pagina/usuarios.html', usuarios=usuarios)
```

### Ejemplo 2: API protegida

```python
@bp.route('/api/usuarios', methods=['POST'])
@requiere_rol('administrador', 'jefe')
def api_crear_usuario():
    """API para crear nuevo usuario (solo jefe y admin)"""
    data = request.get_json()
    
    # Crear usuario...
    resultado = supabase.table("usuarios").insert(usuario_data).execute()
    
    return jsonify({'success': True}), 201
```

### Ejemplo 3: Acceso condicional en template

```html
<!-- app/templates/componentes/sidebar.html -->

<!-- Usuarios - Solo visible para Jefe y Admin -->
{% if session.get('usuario_rol') in ['jefe', 'administrador'] %}
<a href="{{ url_for('main.usuarios') }}">
  <span class="material-symbols-outlined">people</span>
  <span>Usuarios</span>
</a>
{% endif %}

<!-- Inventario - Visible para todos excepto admin puro -->
{% if session.get('usuario_rol') in ['farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador'] %}
<a href="{{ url_for('main.inventario') }}">
  <span class="material-symbols-outlined">inventory_2</span>
  <span>Inventario</span>
</a>
{% endif %}
```

### Ejemplo 4: Validar en JavaScript

```javascript
// app/static/js/usuarios.js

async function crearUsuario(userData) {
    try {
        const response = await fetch('/api/usuarios', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userData)
        });
        
        if (response.status === 403) {
            alert('No tienes permisos para crear usuarios');
            return;
        }
        
        const data = await response.json();
        if (data.success) {
            alert('Usuario creado exitosamente');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## 🔍 Preguntas Frecuentes

### ¿Qué pasa si un usuario intenta acceder a una ruta protegida?

**Respuesta**: El decorador `@requiere_rol` lo rechaza:
- **Si es página HTML**: Lo redirige al dashboard con mensaje de error
- **Si es API (JSON)**: Devuelve `HTTP 403` con mensaje de error

### ¿Puedo cambiar mi propio rol?

**Respuesta**: No. Solo los Jefes y Administradores pueden asignar o cambiar roles a otros usuarios. Un usuario no puede cambiar su propio rol.

### ¿Qué sucede si logout y vuelvo a login con otro rol?

**Respuesta**: La sesión se actualiza automáticamente con el nuevo rol. El sidebar y las rutas protegidas se ajustan al nuevo rol.

### ¿Cómo verifico qué permisos tiene mi usuario actual?

**Respuesta**: En cualquier template puedes verificar:
```html
Rol actual: {{ session.get('usuario_rol') }}
```

O en backend:
```python
rol_usuario = session.get('usuario_rol')
permisos = PERMISOS_POR_ROL.get(rol_usuario, [])
```

### ¿Qué pasa si un usuario modifica su rol en la base de datos?

**Respuesta**: 
1. El cambio no afecta su sesión actual (que sigue siendo el rol anterior)
2. Cuando haga logout y vuelva a hacer login, el nuevo rol se cargará
3. En cada petición se valida el rol contra la sesión

### ¿Puedo tener múltiples roles?

**Respuesta**: Actualmente **no**. Cada usuario tiene un único rol. Si necesitas múltiples permisos, el usuario debe tener el rol "Jefe" o "Administrador" que tienen acceso completo.

### ¿Cómo agrego un nuevo rol al sistema?

**Respuesta**: Modifica `app/config/roles_permisos.py`:

```python
ROLES_DISPONIBLES = [
    'farmaceutico',
    # ... otros roles
    'nuevo_rol'  # ← Agregar aquí
]

PERMISOS_POR_ROL = {
    # ... otros roles
    'nuevo_rol': ['dashboard', 'inventario', 'perfil']  # ← Definir permisos
}
```

---

## ✅ Checklist de Seguridad

- ✅ Todas las rutas están protegidas con `@requiere_rol`
- ✅ Las APIs validan roles en backend (no solo frontend)
- ✅ La sesión se valida en cada petición
- ✅ Los decoradores lanzan excepciones si hay problema
- ✅ El sidebar solo muestra opciones permitidas
- ✅ Los usuarios no pueden cambiar su propio rol
- ✅ Los logs registran intentos de acceso denegado

---

## 📞 Soporte

Si encuentras problemas con el sistema de roles:

1. Verifica que el usuario está logueado: `session.get('usuario_logueado')`
2. Verifica que el rol es válido: `session.get('usuario_rol')`
3. Revisa que el decorador está bien: `@requiere_rol('rol1', 'rol2')`
4. Busca errores en los logs del servidor
5. Limpia cache del navegador (Ctrl+Shift+Delete)

---

**Última actualización**: 12 de noviembre de 2025  
**Versión del sistema**: 1.0 - Sistema de Roles y Control de Acceso
