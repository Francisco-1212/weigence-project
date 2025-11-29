# ✅ Solución: Error de Columna en Supabase

## Problema Original
```
Error en Supabase: Could not find the 'email' column of 'usuarios' in the schema cache
```

## Causa
La tabla `usuarios` en Supabase usa `correo` como nombre de columna, pero el código estaba intentando actualizar una columna llamada `email` (que no existe).

## Estructura Real de la Tabla `usuarios`
```
- rut_usuario (PK)
- nombre
- correo        ← ¡Aquí está, no "email"!
- numero_celular
- rol
- ... otras columnas
```

## Cambios Realizados

### En `app/routes/perfil.py`

#### 1. Ruta `/editar` (Formulario tradicional)
- ✅ Cambió: `email` → `correo`
- ✅ Ahora: `update_data["correo"] = correo if correo else None`
- ✅ Ahora: `session['usuario_correo'] = correo if correo else ...`

#### 2. Ruta `/api/editar-perfil` (API AJAX)
- ✅ Cambió: `email` → `correo`
- ✅ Cambió: `update_data["email"]` → `update_data["correo"]`
- ✅ Cambió: respuesta JSON para devolver `'correo': correo`

## Cómo Funciona Ahora
1. Frontend envía `{ nombre, email, numero_celular }` (el nombre sigue siendo `email` porque es el campo del formulario)
2. Backend recibe `email` del JSON
3. Convierte internamente a `correo` para trabajar con Supabase
4. Supabase actualiza la columna `correo` correctamente
5. Sesión se actualiza con `usuario_correo`

## Próximos Pasos
✅ Intenta guardar cambios nuevamente en el modal
✅ Deberías ver éxito sin errores de Supabase
✅ Los cambios se guardarán en Supabase correctamente
