# ⚡ Quick Start - Gestión de Usuarios

## 🚀 5 Pasos para Empezar

### 1. Inicia Sesión
- Usuario: "Paulo Brito" (Jefe)
- Contraseña: Tu contraseña
- Click "Iniciar Sesión"

### 2. Abre Gestión de Usuarios
- Sidebar → Click en "Usuarios"
- O accede directo: http://localhost:5000/usuarios

### 3. Crea un Usuario Nuevo
- Click en botón verde "Nuevo Usuario"
- Completa el formulario:
  ```
  RUT: 21123456-5
  Nombre: Carlos Gómez
  Correo: carlos@farmacia.cl
  Rol: Farmacéutico
  Teléfono: +56 9 9999 9999
  Contraseña: password123
  ```
- Click "Guardar"

### 4. Edita al Usuario
- En la tabla, click ícono lápiz (Editar)
- Cambia el rol a "Bodeguera"
- Click "Guardar"

### 5. Elimina al Usuario
- Click ícono basura (Eliminar)
- Confirma

¡Listo! 🎉

---

## 📋 Fórmatos Importantes

### RUT
✅ Formato correcto:
- `20123456-7`
- `20.123.456-7`

❌ Incorrecto:
- `201234567`
- `201234567-`

### Email
✅ Correcto:
- `usuario@ejemplo.com`
- `juan.perez@farmacia.cl`

❌ Incorrecto:
- `usuarioejemplo.com`
- `@ejemplo.com`

### Roles Disponibles
1. **Farmacéutico** - Acceso limitado a inventario
2. **Bodeguera** - Inventario, movimientos y alertas
3. **Supervisor** - Más acceso + auditoría
4. **Jefe** - Acceso casi completo + usuarios
5. **Administrador** - Acceso total

---

## 🔑 Usuarios de Prueba

| Nombre | Rol | Para Probar |
|--------|-----|-------------|
| Paulo Brito | Jefe | Gestión de usuarios |
| Nelson Duarte | Admin | Todas las funciones |
| Verónica Ríos | Farmacéutico | Acceso limitado |
| Patricia Torres | Bodeguera | Movimientos |
| Jorge Morales | Supervisor | Auditoría |

---

## ⚙️ Configuración (Si es necesario)

Los roles están definidos en:
```
app/config/roles_permisos.py
```

Los permisos en:
```
app/routes/usuarios.py
```

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo eliminar mi propia cuenta?**
R: No, el sistema te protege.

**P: ¿Qué pasa si ingreso un RUT duplicado?**
R: Se rechaza, debe ser único.

**P: ¿Puedo cambiar el RUT de un usuario?**
R: No, el RUT es inmutable (por seguridad).

**P: ¿La contraseña es requerida al editar?**
R: No, déjala vacía para mantener la actual.

**P: ¿Dónde se guardan los datos?**
R: En Supabase (PostgreSQL).

---

## 🆘 Si Algo Falla

1. **Botón no funciona**
   - Abre F12 (DevTools)
   - Ve a Console
   - Busca errores rojos

2. **Usuario no se crea**
   - Verifica formato de RUT
   - Verifica que no esté duplicado
   - Verifica email válido

3. **No ves la página de Usuarios**
   - ¿Estás logueado como Jefe o Admin?
   - Sidebar debe mostrar "Usuarios"
   - Si no, no tienes permisos

4. **Más ayuda**
   - Consulta: GESTION_USUARIOS_COMPLETA.md
   - O: GUIA_TESTING_COMPLETA.md

---

## 📞 Contacto

Para más información, consulta la documentación completa o contacta al equipo de desarrollo.

**Última actualización**: 12 de noviembre de 2025
