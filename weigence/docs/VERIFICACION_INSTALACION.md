# ✅ Verificación e Instalación del Sistema de Roles

## 📋 Checklist de Instalación

### Paso 1: Verificar Archivos Creados

Asegúrate de que existan estos archivos:

```
✅ app/routes/decorators.py
✅ app/routes/usuarios.py
✅ app/templates/pagina/usuarios.html
✅ SISTEMA_ROLES_USUARIOS.md
✅ IMPLEMENTACION_COMPLETADA.md
✅ GUIA_RAPIDA_ROLES.md
```

**Comando para verificar**:
```bash
ls -la app/routes/decorators.py app/routes/usuarios.py app/templates/pagina/usuarios.html
```

### Paso 2: Verificar Modificaciones

Asegúrate de que estos archivos fueron modificados:

```
✅ app/routes/__init__.py           (importa usuarios)
✅ app/templates/componentes/sidebar.html  (control por rol)
```

### Paso 3: Reiniciar Flask

Detén y reinicia la aplicación:

```bash
# En la terminal de Flask
Ctrl+C

# Luego
python app.py
```

O si usas flask run:
```bash
flask run
```

### Paso 4: Verificar Base de Datos

Asegúrate de que la tabla `usuarios` en Supabase tiene estos campos:

```
✅ rut_usuario (PRIMARY KEY)
✅ nombre
✅ correo
✅ rol              ← IMPORTANTE: Verificar que existe y tiene valores
✅ numero celular
✅ Contraseña
✅ fecha_registro
✅ reset_token
✅ reset_token_expires
```

**¿Cómo verificar?**
```python
# En Python
from api.conexion_supabase import supabase
response = supabase.table("usuarios").select("*").limit(1).execute()
if response.data:
    print(list(response.data[0].keys()))
```

## 🧪 Pruebas

### Prueba 1: Acceso a Usuarios

1. Inicia sesión con un usuario **Jefe** o **Administrador**
2. En el sidebar, deberías ver **"Usuarios"** (con ícono 👥)
3. Haz clic en él
4. Deberías ver una tabla con todos los usuarios

**Resultado esperado**: ✅ Página carga correctamente

### Prueba 2: Crear Usuario

1. En `/usuarios`, haz clic en "Nuevo Usuario"
2. Completa:
   - RUT: `21123456-8`
   - Nombre: `Test User`
   - Correo: `test@example.com`
   - Rol: `farmaceutico`
   - Contraseña: `TestPass123`
3. Haz clic en "Guardar"

**Resultado esperado**: ✅ "Usuario creado correctamente" y aparece en la tabla

### Prueba 3: Editar Usuario

1. En la tabla, busca al usuario que acabas de crear
2. Haz clic en el ícono ✏️
3. Cambia el nombre a `Test User Editado`
4. Haz clic en "Guardar"

**Resultado esperado**: ✅ Nombre actualizado en la tabla

### Prueba 4: Control de Acceso

1. Inicia sesión con un usuario **Farmacéutico**
2. En el sidebar, NO deberías ver "Usuarios"
3. Intenta acceder directamente a `/usuarios`

**Resultado esperado**: ❌ Redirección al dashboard + "Acceso denegado"

### Prueba 5: Cambiar Rol

1. Crea un usuario con rol `farmaceutico`
2. Edita el usuario
3. Cambia el rol a `jefe`
4. Guarda
5. Cierra la sesión del usuario
6. Inicia sesión con ese usuario
7. En el sidebar deberías ver más opciones

**Resultado esperado**: ✅ El usuario ahora ve secciones del jefe

## 🔍 Verificación de Código

### Verificar que decoradores funcionan

```python
# En una terminal Python interactiva
from app.routes.decorators import requiere_rol, requiere_autenticacion
print("✅ Decoradores importados correctamente")
```

### Verificar que rutas están registradas

```python
# En app.py o similar
from app import create_app
app = create_app()

# Ver todas las rutas
for rule in app.url_map.iter_rules():
    if 'usuario' in str(rule):
        print(rule)
```

**Deberías ver**:
```
/usuarios                    (GET)
/usuarios                    (POST)
/usuarios/<rut>              (GET)
/usuarios/<rut>              (PUT)
/usuarios/<rut>              (DELETE)
/api/usuarios                (GET)
/api/usuarios                (POST)
/api/usuarios/<rut>          (GET)
/api/usuarios/<rut>          (PUT)
/api/usuarios/<rut>          (DELETE)
```

## 📊 Verificación de Datos

### ¿Todos los usuarios tienen rol?

```python
from api.conexion_supabase import supabase

response = supabase.table("usuarios").select("rut_usuario, nombre, rol").execute()
usuarios = response.data

# Verificar que todos tienen rol
sin_rol = [u for u in usuarios if not u.get('rol')]

if sin_rol:
    print(f"⚠️ {len(sin_rol)} usuarios sin rol:")
    for u in sin_rol:
        print(f"  - {u['nombre']}")
else:
    print("✅ Todos los usuarios tienen rol asignado")
```

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'app.routes.decorators'"

**Solución**:
1. Verifica que `app/routes/decorators.py` existe
2. Reinicia Flask
3. Limpia caché de Python: `rm -rf app/routes/__pycache__`

### Problema: "usuarios" no aparece en el sidebar

**Solución**:
1. Verifica que tu usuario tiene rol `jefe` o `administrador`
2. Recarga la página (Ctrl+Shift+R)
3. Verifica que `sidebar.html` fue modificado correctamente

### Problema: Error 500 al crear usuario

**Solución**:
1. Revisa la consola de Flask para el error exacto
2. Verifica que el usuario_id en sesión existe
3. Verifica que Supabase está conectado correctamente

### Problema: "Acceso denegado" aunque tengo el rol correcto

**Solución**:
1. Cierra sesión y abre nuevamente
2. Verifica que `session['usuario_rol']` tiene el valor correcto
3. Recarga la página

## 📈 Escalabilidad

### Para agregar un nuevo rol

1. Actualiza la lista de roles en `app/routes/usuarios.py`:
```python
ROLES_DISPONIBLES = ['farmaceutico', 'bodeguera', 'supervisor', 'jefe', 'administrador', 'nuevo_rol']
```

2. Actualiza permisos:
```python
PERMISOS_POR_ROL['nuevo_rol'] = ['dashboard', 'inventario']
```

3. Actualiza el dropdown en `usuarios.html`

### Para agregar una nueva sección

1. Crea la ruta:
```python
@bp.route('/nueva-seccion')
@requiere_rol('jefe', 'administrador')
def nueva_seccion():
    return render_template('pagina/nueva_seccion.html')
```

2. Agrega al sidebar:
```html
{% if session.get('usuario_rol') in ['jefe', 'administrador'] %}
  <a href="{{ url_for('main.nueva_seccion') }}">Nueva Sección</a>
{% endif %}
```

3. Actualiza `PERMISOS_POR_ROL` si es necesario

## ✅ Checklist Final

- [ ] Archivos creados existen
- [ ] Archivos modificados tienen cambios
- [ ] Flask está reiniciado
- [ ] Base de datos está actualizada
- [ ] Prueba 1: Acceso a usuarios ✅
- [ ] Prueba 2: Crear usuario ✅
- [ ] Prueba 3: Editar usuario ✅
- [ ] Prueba 4: Control de acceso ✅
- [ ] Prueba 5: Cambiar rol ✅
- [ ] Documentación es clara
- [ ] Todo funciona correctamente

## 📞 Soporte

Si algo no funciona:
1. Revisa los logs de Flask (consola)
2. Consulta `SISTEMA_ROLES_USUARIOS.md`
3. Ejecuta el checklist de Troubleshooting
4. Verifica la base de datos en Supabase

---

**Estado**: ✅ Listo para producción
**Última actualización**: 11 de Noviembre de 2025
