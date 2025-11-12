# ✅ Solución Final: Nombre de Columna Correcto en Supabase

## El Problema
Supabase estaba devolviendo errores porque el código intentaba actualizar un campo llamado:
- ❌ `numero_celular` (con guion bajo)

Pero el campo real en la tabla se llama:
- ✅ `numero celular` (con **espacio**)

## Estructura Real de la Tabla `usuarios`

```
1. rut_usuario          (PRIMARY KEY)
2. nombre
3. correo
4. rol
5. fecha_registro
6. Contraseña
7. numero celular       ← ¡AQUÍ ESTÁ, con espacio!
8. reset_token
9. reset_token_expires
```

## Cambios Realizados en `app/routes/perfil.py`

### 1. En la ruta POST `/editar` (formulario tradicional)
```python
# ANTES ❌
update_data = {
    "numero_celular": numero_celular_formateado
}

# AHORA ✅
update_data = {
    "numero celular": numero_celular_formateado  # Con espacio
}
```

### 2. En la ruta POST `/api/editar-perfil` (API AJAX)
```python
# ANTES ❌
update_data = {
    "numero_celular": numero_celular_formateado
}

# AHORA ✅
update_data = {
    "numero celular": numero_celular_formateado  # Con espacio
}
```

## ¿Por Qué Pasó Esto?

El nombre de la columna en Supabase tiene un **espacio en lugar de un guion bajo**. Esto es inusual pero perfectamente válido en SQL cuando se usan comillas:

```sql
-- Así lee Supabase el campo:
UPDATE usuarios SET "numero celular" = '...'
```

## ¿Cómo lo Descubrimos?

Ejecutamos el script `verificar_campos_supabase.py` que:
1. Conectó a Supabase
2. Obtuvo el primer registro de `usuarios`
3. Listó todos los campos reales
4. Mostró exactamente qué nombres usaba cada columna

## Próximos Pasos

✅ **Ahora puede funcionar:**
1. Detén Flask (Ctrl+C)
2. Recarga la página del navegador (Ctrl+Shift+R)
3. Abre el modal "Editar Perfil"
4. Modifica los datos y guarda
5. ¡Debería funcionar correctamente!

## Nota Importante

⚠️ El nombre de la columna en Supabase es **`numero celular`** (con espacio). Esto es un poco inusual y puede causar problemas. En el futuro, podría ser buena idea en Supabase renombrar la columna a `numero_celular` (con guion bajo) para mantener consistencia con las demás columnas.
