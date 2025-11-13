# 🧪 Testing - Guía Completa

## Pre-Testing Checklist

- [ ] Aplicación Flask corriendo
- [ ] Base de datos Supabase conectada
- [ ] Navegador limpio (caché borrado)
- [ ] Console DevTools abierta (F12)

## ✅ Test 1: Login y Roles

### Test 1.1: Login como Farmacéutico
```
1. Abre http://localhost:5000/
2. Usuario: "Verónica Ríos" (o cualquier farmacéutico)
3. Contraseña: su contraseña
4. Click "Iniciar Sesión"
```

**Resultado esperado:**
- ✅ Redirecciona a Dashboard
- ✅ En `/debug-usuario` debe mostrar: `usuario_rol: farmaceutico`
- ✅ Sidebar muestra: Dashboard, Inventario, Perfil
- ✅ NO muestra: Movimientos, Alertas, Auditoría, Usuarios, Historial

### Test 1.2: Login como Bodeguera
```
1. Cerrar sesión (click Logout)
2. Usuario: "Patricia Torres"
3. Contraseña: su contraseña
4. Click "Iniciar Sesión"
```

**Resultado esperado:**
- ✅ Dashboard cargado
- ✅ Sidebar muestra: Dashboard, Inventario, Movimientos, Alertas, Perfil
- ✅ NO muestra: Auditoría, Usuarios, Historial

### Test 1.3: Login como Supervisor
```
1. Cerrar sesión
2. Usuario: "Jorge Morales"
3. Click "Iniciar Sesión"
```

**Resultado esperado:**
- ✅ Sidebar muestra: Dashboard, Inventario, Movimientos, Alertas, Auditoría, Perfil
- ✅ NO muestra: Usuarios, Historial, Recomendaciones

### Test 1.4: Login como Jefe
```
1. Cerrar sesión
2. Usuario: "Paulo Brito"
3. Click "Iniciar Sesión"
```

**Resultado esperado:**
- ✅ Sidebar muestra TODAS las opciones
- ✅ Incluyendo: Usuarios, Historial, Recomendaciones

### Test 1.5: Login como Administrador
```
1. Cerrar sesión
2. Usuario: "Nelson Duarte" o "Francisco Carrasco"
3. Click "Iniciar Sesión"
```

**Resultado esperado:**
- ✅ Sidebar muestra TODAS las opciones
- ✅ Acceso total

---

## ✅ Test 2: Gestión de Usuarios

### Test 2.1: Acceso a Usuarios (Jefe)
```
1. Login como Jefe
2. En sidebar, click en "Usuarios"
```

**Resultado esperado:**
- ✅ Página carga
- ✅ Tabla muestra todos los usuarios
- ✅ Botón "Nuevo Usuario" visible

### Test 2.2: Acceso a Usuarios (Farmacéutico)
```
1. Login como Farmacéutico
2. Intenta acceder a http://localhost:5000/usuarios
```

**Resultado esperado:**
- ✅ Error 403 (Acceso Denegado)
- ✅ Sidebar no muestra "Usuarios"

### Test 2.3: Crear Nuevo Usuario
```
1. Login como Jefe
2. Go to Usuarios
3. Click "Nuevo Usuario"
4. Completa:
   - RUT: 25123456-8
   - Nombre: Test Usuario
   - Correo: test@farmacia.cl
   - Rol: Bodeguera
   - Teléfono: +56 9 1234 5678
   - Contraseña: password123
5. Click "Guardar"
```

**Resultado esperado:**
- ✅ Usuario aparece en tabla
- ✅ Con rol mostrado en color correcto
- ✅ Mensaje de éxito

### Test 2.4: Editar Usuario
```
1. En tabla de usuarios
2. Click en ícono "Editar" de Test Usuario
3. Cambiar Rol a "Supervisor"
4. Click "Guardar"
```

**Resultado esperado:**
- ✅ Usuario actualizado
- ✅ Rol cambiado en tabla
- ✅ Mensaje de éxito

### Test 2.5: Eliminar Usuario
```
1. En tabla, click ícono "Eliminar" de Test Usuario
2. Confirmar eliminación
```

**Resultado esperado:**
- ✅ Usuario desaparece de tabla
- ✅ Mensaje de éxito

---

## ✅ Test 3: Validaciones

### Test 3.1: RUT Inválido
```
1. Crear nuevo usuario
2. RUT: "INVALIDO"
3. Intentar guardar
```

**Resultado esperado:**
- ❌ Error: "Formato de RUT inválido"

### Test 3.2: Email Duplicado
```
1. Crear nuevo usuario
2. RUT: 26123456-9
3. Email: veronica.rios@farmacia.cl (existente)
4. Intentar guardar
```

**Resultado esperado:**
- ❌ Error: "El email ya está registrado"

### Test 3.3: RUT Duplicado
```
1. Crear nuevo usuario
2. RUT: 13245789-3 (Verónica Ríos)
3. Intentar guardar
```

**Resultado esperado:**
- ❌ Error: "El usuario (RUT) ya existe"

### Test 3.4: Email Inválido
```
1. Crear nuevo usuario
2. Email: "notanemail"
3. Intentar guardar
```

**Resultado esperado:**
- ❌ Error: "Formato de correo inválido"

---

## ✅ Test 4: Seguridad

### Test 4.1: No puedes eliminar tu propia cuenta
```
1. Login como Admin
2. Ir a Usuarios
3. Intentar eliminar tu propia cuenta (Nelson Duarte)
```

**Resultado esperado:**
- ❌ Error: "No puedes eliminar tu propia cuenta"

### Test 4.2: Acceso no autorizado a API
```
1. Login como Farmacéutico
2. Abrir consola (F12)
3. Ejecutar: fetch('/api/usuarios')
```

**Resultado esperado:**
- ❌ Error 403: "No autorizado"

### Test 4.3: Protección de rutas
```
1. Logout
2. Intenta acceder a: http://localhost:5000/usuarios
```

**Resultado esperado:**
- 🔄 Redirecciona a login

---

## ✅ Test 5: Debug

### Test 5.1: Verificar sesión
```
1. Login como Jefe
2. Abre: http://localhost:5000/debug-sesion-visual
```

**Resultado esperado:**
- ✅ usuario_rol: "jefe" (minúsculas)
- ✅ usuario_nombre: "Paulo Brito"
- ✅ Comparaciones muestran true

### Test 5.2: Verificar usuario
```
1. Login como cualquier usuario
2. Abre: http://localhost:5000/debug-usuario
```

**Resultado esperado:**
- ✅ Datos de sesión mostrados correctamente
- ✅ Rol en minúsculas

---

## 🎯 Checklist de Testing Final

Usuarios:
- [ ] Farmacéutico: Acceso correcto
- [ ] Bodeguera: Acceso correcto
- [ ] Supervisor: Acceso correcto
- [ ] Jefe: Acceso correcto
- [ ] Administrador: Acceso correcto

Gestión:
- [ ] Listar usuarios: Funciona
- [ ] Crear usuario: Funciona
- [ ] Editar usuario: Funciona
- [ ] Eliminar usuario: Funciona

Validaciones:
- [ ] RUT validado
- [ ] Email validado
- [ ] Duplicados detectados
- [ ] Campos requeridos validados

Seguridad:
- [ ] Acceso no autorizado bloqueado
- [ ] Sesión protegida
- [ ] No puedo borrar mi cuenta
- [ ] Rutas protegidas

Debug:
- [ ] `/debug-sesion` muestra datos
- [ ] `/debug-sesion-visual` muestra comparaciones
- [ ] `/debug-usuario` muestra información

---

## 📊 Resultado Final

Si todos los tests pasan:

✅ **Sistema de Roles**: Funciona perfectamente
✅ **Gestión de Usuarios**: Funciona perfectamente
✅ **Seguridad**: Implementada correctamente
✅ **Validaciones**: Completas

**Estado**: 🟢 LISTO PARA PRODUCCIÓN

---

**Fecha de Testing**: 12 de noviembre de 2025
