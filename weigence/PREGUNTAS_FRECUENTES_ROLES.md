# ❓ Preguntas Frecuentes: Sistema de Roles - Weigence

## 🔐 Autenticación y Seguridad

### P: ¿Qué pasa si alguien intenta modificar su rol en la base de datos?
**R:** No afecta la sesión actual. La sesión almacena el rol en memoria del servidor, no se refresca hasta hacer logout/login. Cuando el usuario intente hacer logout o la sesión expire, tendrá que volver a ingresar con el nuevo rol.

### P: ¿Alguien sin sesión puede acceder a las rutas protegidas?
**R:** No. El decorador `@requiere_rol` verifica primero si `session.get('usuario_logueado')` es `True`. Si no, redirige al login.

### P: ¿Las contraseñas están encriptadas?
**R:** Actualmente se almacenan en texto plano en la base de datos. Se recomienda usar hashing con `werkzeug.security.generate_password_hash()` en futuras versiones.

### P: ¿Qué información se almacena en la sesión?
**R:** 
- `usuario_logueado` (bool)
- `usuario_id` (RUT)
- `usuario_nombre` (string)
- `usuario_correo` (string)
- `usuario_rol` (string) ← **Esto es clave**
- `recordarme_activado` (bool)

---

## 👥 Gestión de Usuarios y Roles

### P: ¿Quién puede crear nuevos usuarios?
**R:** Solo **Jefe** y **Administrador**. Está protegido con `@requiere_rol('jefe', 'administrador')`.

### P: ¿Quién puede cambiar el rol de un usuario?
**R:** Solo **Jefe** y **Administrador**. Al cambiar el rol, el usuario debe hacer logout y login nuevamente para que se actualice su sesión.

### P: ¿Un usuario puede cambiar su propio rol?
**R:** No, físicamente no puede. El backend valida que quien intenta editar no sea a sí mismo, y aunque pudiera, necesitaría permisos de Jefe/Admin.

### P: ¿Qué pasa si un usuario tiene permisos de Jefe pero intenta crear otro Jefe?
**R:** Puede hacerlo. El sistema permite que cualquier Jefe cree a otro Jefe o cualquier otro rol.

### P: ¿Hay límite de usuarios que puede crear?
**R:** No hay límite técnico. El límite sería la capacidad de la base de datos (Supabase).

### P: ¿Puedo eliminar un usuario?
**R:** Solo **Jefe** y **Administrador** pueden eliminar usuarios. Un usuario no puede eliminarse a sí mismo.

---

## 🔄 Cambio de Roles

### P: ¿Qué ven cuando cierro sesión después de cambiar de rol?
**R:** Nada. Se borra la sesión. Cuando vuelven a hacer login, cargan su nuevo rol.

### P: ¿Mi sidebar se actualiza automáticamente si me cambian de rol?
**R:** No automáticamente. Solo cuando:
1. Haces logout
2. Vuelves a hacer login
3. Se carga tu nuevo rol en la sesión

### P: ¿Un supervisor puede convertirse a bodeguera?
**R:** No, solo un Jefe o Administrador pueden cambiar su rol.

### P: ¿Si tengo acceso a Usuarios, puedo ver todos los usuarios en el sistema?
**R:** Sí, si eres Jefe o Admin, ves todos. El acceso es completo a la tabla de usuarios.

---

## 🚀 Desarrollo y API

### P: ¿Cómo agrego una nueva ruta protegida?
**R:**
```python
from .decorators import requiere_rol

@bp.route('/mi-nueva-ruta')
@requiere_rol('jefe', 'administrador')
def mi_nueva_ruta():
    return render_template('mi_template.html')
```

### P: ¿Cómo protejo un endpoint de API?
**R:**
```python
@bp.route('/api/mi-endpoint', methods=['POST'])
@requiere_rol('jefe')
def mi_api_endpoint():
    data = request.get_json()
    return jsonify({'success': True}), 201
```

### P: ¿Qué devuelve una API protegida si no tengo permisos?
**R:**
```json
{
    "success": false,
    "error": "Acceso denegado",
    "code": 403,
    "rol_requerido": ["jefe", "admin"],
    "rol_usuario": "bodeguera"
}
```

### P: ¿Cómo sé qué error tuvo mi solicitud?
**R:** Revisa el código HTTP:
- `401` = No autenticado (sin sesión)
- `403` = No autorizado (sin permisos suficientes)
- `200` = Éxito

### P: ¿Puedo usar múltiples decoradores en una ruta?
**R:** Sí, pero cuidado con el orden. El más restrictivo debe ser el más cercano a la función:
```python
@bp.route('/mi-ruta')
@puede_realizar_accion('usuarios', 'eliminar')
@requiere_rol('jefe', 'admin')
def mi_ruta():
    pass
```

---

## 🎨 Frontend y Vistas

### P: ¿Cómo muestro algo solo para cierto rol en un template?
**R:**
```html
{% if session.get('usuario_rol') == 'jefe' %}
  <p>Solo para jefes</p>
{% endif %}

<!-- O múltiples roles -->
{% if session.get('usuario_rol') in ['jefe', 'administrador'] %}
  <p>Solo para jefe y admin</p>
{% endif %}
```

### P: ¿Mi sidebar se ve diferente por rol?
**R:** Sí, está configurado en `app/templates/componentes/sidebar.html` con validaciones de rol.

### P: ¿Puedo cambiar los colores del sidebar por rol?
**R:** Sí, edita `sidebar.html` y agrega estilos dinámicos según `session.usuario_rol`.

---

## 🐛 Troubleshooting

### P: Intento acceder a una ruta y siempre me redirige al login
**R:** Probablemente:
1. Tu sesión expiró
2. Tu navegador está en modo privado (no guarda cookies)
3. Las cookies están deshabilitadas
4. El servidor Flask no reinició después de cambios

**Solución:** 
- Limpia cookies/cache
- Intenta en otra pestaña/navegador
- Reinicia el servidor

### P: Me dice "Acceso denegado" pero el decorador dice que tengo permiso
**R:** Verifica:
1. `session.get('usuario_rol')` es exacto (minúsculas)
2. Tu rol está en `ROLES_DISPONIBLES`
3. Tu rol está listado en el decorador
4. Hiciste logout/login después del cambio de rol

### P: Una API devuelve 403 en Postman pero funciona en el navegador
**R:** En Postman no estás enviando la cookie de sesión. Agrega:
```
Headers:
Cookie: session=YOUR_SESSION_ID
```

O mejor aún, prueba en el navegador con las herramientas de desarrollador.

### P: El sidebar no muestra mi nueva ruta
**R:** Verifica que:
1. La ruta existe en `bp`
2. El template tiene validación de rol
3. Tu rol tiene permiso para esa sección
4. Reiniciaste el servidor

---

## 💾 Base de Datos

### P: ¿Dónde se almacenan los roles en Supabase?
**R:** En la tabla `usuarios`, columna `rol`. Las opciones son:
- `farmaceutico`
- `bodeguera`
- `supervisor`
- `jefe`
- `administrador`

### P: ¿Qué pasa si un rol tiene valor NULL?
**R:** El decorador lo rechazará por no ser válido. Verifica que todos los usuarios tengan un rol asignado.

### P: ¿Puedo agregar un nuevo rol directamente en la BD?
**R:** Técnicamente sí, pero el sistema no lo reconocerá hasta que:
1. Lo agregues en `app/config/roles_permisos.py`
2. Lo agregues en `ROLES_DISPONIBLES`
3. Reinicies el servidor Flask

---

## 📊 Reportes y Auditoría

### P: ¿Hay un registro de quién cambió qué rol?
**R:** No actualmente. Se podría implementar agregando logs a `app/routes/usuarios.py` que registren cambios de rol en una tabla `auditoria`.

### P: ¿Quién puede ver el historial de cambios?
**R:** El rol que acceda a `/historial` que es solo **Jefe** y **Administrador**.

---

## 🔄 Migraciones y Actualizaciones

### P: ¿Qué pasa si actualizo el rol en production?
**R:** 
1. Las sesiones activas no se actualizan automáticamente
2. Los usuarios deben hacer logout/login
3. Se recomienda avisar con 1-2 horas de anticipación

### P: ¿Cómo hago rollback de cambios de rol?
**R:** 
1. Accede a Supabase
2. Edita la columna `rol` de nuevo a su valor anterior
3. Los usuarios tendrán el rol anterior después de logout/login

---

## 🔒 Mejores Prácticas

### ✅ HACER
- ✅ Usar `@requiere_rol()` en todas las rutas
- ✅ Validar en backend, no solo frontend
- ✅ Usar nombres de rol en minúsculas (`'jefe'`, no `'Jefe'`)
- ✅ Hacer logout después de cambiar roles
- ✅ Registrar intentos de acceso no autorizados

### ❌ NO HACER
- ❌ Confiar solo en validación de frontend
- ❌ Mezclar rolesnúclas en decoradores (`'Jefe'` vs `'jefe'`)
- ❌ Permitir que usuarios cambien su propio rol
- ❌ Guardar roles en localStorage/sessionStorage
- ❌ Hardcodear roles en templates sin validación

---

## 📞 Contacto y Soporte

Si tu pregunta no está aquí:
1. Lee **DOCUMENTACION_SISTEMA_ROLES.md**
2. Revisa **IMPLEMENTACION_ROLES_COMPLETADA.md**
3. Ejecuta `python verificar_roles.py`
4. Consulta los logs del servidor: `print()` o use `logging`

---

**Última actualización**: 12 de noviembre de 2025  
**Versión**: 1.0  
**FAQ completado**: ✅
