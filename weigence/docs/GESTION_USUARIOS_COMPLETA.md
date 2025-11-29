# 👥 Sistema de Gestión de Usuarios - Funcional

## ✅ Características Implementadas

### 1. Listar Usuarios
- ✅ Vista de tabla con todos los usuarios
- ✅ Muestra: RUT, Nombre, Correo, Rol, Teléfono, Fecha de Registro
- ✅ Colores diferenciados por rol
- ✅ Carga automática al abrir la página

### 2. Crear Nuevo Usuario
- ✅ Botón "Nuevo Usuario" abre modal
- ✅ Validación de RUT (formato: XX.XXX.XXX-X)
- ✅ Validación de email
- ✅ Selección de rol con 5 opciones
- ✅ Campo opcional de teléfono
- ✅ Contraseña requerida para nuevos usuarios
- ✅ Prevención de duplicados (RUT y email)

### 3. Editar Usuario
- ✅ Botón "Editar" en cada fila
- ✅ Carga datos del usuario en el modal
- ✅ RUT no se puede cambiar (deshabilitado)
- ✅ Contraseña opcional (dejar vacía mantiene la actual)
- ✅ Validación de cambios
- ✅ Actualización en tiempo real

### 4. Eliminar Usuario
- ✅ Botón "Eliminar" en cada fila
- ✅ Confirmación antes de eliminar
- ✅ Protección: No puedes eliminar tu propia cuenta
- ✅ Eliminación inmediata

### 5. Seguridad
- ✅ Solo accesible para Jefe y Administrador
- ✅ Decorador @requiere_rol en backend
- ✅ Validaciones en formulario (frontend)
- ✅ Validaciones en servidor (backend)
- ✅ Protección contra inyección SQL (Supabase)

## 📋 Cómo Usar

### Acceder a Gestión de Usuarios
1. Inicia sesión como **Jefe** o **Administrador**
2. En el sidebar, haz click en **"Usuarios"**
3. Se abrirá la página con la lista de todos los usuarios

### Crear Nuevo Usuario

1. Haz click en botón **"Nuevo Usuario"** (verde, arriba a la derecha)
2. Se abrirá un modal con el formulario
3. Completa los campos:
   - **RUT**: Formato `20123456-7` o `20.123.456-7`
   - **Nombre**: Mínimo 3 caracteres
   - **Correo**: Email válido
   - **Rol**: Selecciona uno de los 5 roles
   - **Teléfono**: Opcional
   - **Contraseña**: Requerida (mínimo 6 caracteres sugerido)
4. Haz click en **"Guardar"**
5. Si todo es válido, el usuario se crea y aparece en la tabla

### Editar Usuario

1. En la tabla, encontradiciendo la fila del usuario
2. Haz click en el ícono **"Editar"** (lápiz azul)
3. Se abrirá el modal con los datos del usuario
4. Modifica los campos que necesites:
   - RUT: No se puede cambiar
   - Nombre, Correo, Rol, Teléfono: Puedes cambiar
   - Contraseña: Déjala vacía si no quieres cambiarla
5. Haz click en **"Guardar"**

### Eliminar Usuario

1. En la tabla, encuentra la fila del usuario
2. Haz click en el ícono **"Eliminar"** (basura roja)
3. Se mostrará una confirmación
4. Haz click en **"Aceptar"** para confirmar
5. El usuario se elimina inmediatamente

**⚠️ Importante**: No puedes eliminar tu propia cuenta

## 🛡️ Validaciones

### RUT
- ✅ Formato: `20123456-7` o `20.123.456-7`
- ✅ No puede repetirse
- ✅ Requerido

### Email
- ✅ Formato válido: `usuario@dominio.cl`
- ✅ No puede repetirse
- ✅ Requerido

### Nombre
- ✅ Mínimo 3 caracteres
- ✅ Requerido

### Rol
- ✅ Farmacéutico
- ✅ Bodeguera
- ✅ Supervisor
- ✅ Jefe
- ✅ Administrador
- ✅ Requerido

### Contraseña (al crear)
- ✅ Requerida
- ✅ Se guarda en Supabase

## 🎨 Interfaz

### Colores por Rol
- 🔵 **Farmacéutico**: Azul
- 🟡 **Bodeguera**: Amarillo
- 🟣 **Supervisor**: Púrpura
- 🟢 **Jefe**: Verde
- 🔴 **Administrador**: Rojo

### Botones
- ✏️ **Editar**: Ícono de lápiz (azul)
- 🗑️ **Eliminar**: Ícono de basura (rojo)
- ➕ **Nuevo Usuario**: Botón verde arriba a la derecha

## 🔌 Endpoints API

### Obtener Usuarios
```
GET /api/usuarios
Response: { success: true, data: [...], total: N }
```

### Obtener Usuario Individual
```
GET /api/usuarios/<rut>
Response: { success: true, data: {...} }
```

### Crear Usuario
```
POST /api/usuarios
Body: {
  rut_usuario: "20123456-7",
  nombre: "Juan Pérez",
  correo: "juan@example.com",
  rol: "farmaceutico",
  numero_celular: "+56 9 1234 5678",
  Contraseña: "password123"
}
Response: { success: true, message: "Usuario creado..." }
```

### Editar Usuario
```
PUT /api/usuarios/<rut>
Body: {
  nombre: "Juan Pérez",
  correo: "juan@example.com",
  rol: "bodeguera",
  numero_celular: "+56 9 9999 9999",
  Contraseña: "newpassword" (opcional)
}
Response: { success: true, message: "Usuario actualizado..." }
```

### Eliminar Usuario
```
DELETE /api/usuarios/<rut>
Response: { success: true, message: "Usuario eliminado..." }
```

## 📁 Archivos Relacionados

- **Backend**: `app/routes/usuarios.py`
- **Frontend HTML**: `app/templates/pagina/usuarios.html`
- **Frontend JS**: `app/static/js/usuarios.js`
- **Decoradores**: `app/routes/decorators.py` (protección @requiere_rol)

## 🚀 Próximas Mejoras (Opcionales)

- [ ] Exportar lista de usuarios a CSV
- [ ] Importar usuarios desde CSV
- [ ] Búsqueda y filtros en la tabla
- [ ] Paginación para muchos usuarios
- [ ] Historial de cambios
- [ ] Notificación por email al crear usuario
- [ ] 2FA (Autenticación de dos factores)
- [ ] Auditoría de quién hizo qué cambios

---

**Estado**: ✅ 100% Funcional
**Última actualización**: 12 de noviembre de 2025
