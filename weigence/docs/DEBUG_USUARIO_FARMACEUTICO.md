# 🔍 Debugging: Usuario Farmacéutico Mostrando Perfil de Administrador

## El Problema
Cuando inicia sesión como **farmacéutico**, aparece el **perfil de administrador**.

## Causas Posibles

### 1. ❌ El usuario "farmacéutico" en Supabase tiene rol "administrador"
   - **Solución**: Edita el usuario en Supabase y cambia su rol a "farmaceutico"

### 2. ❌ Hay un problema al buscar el usuario en login
   - **Síntoma**: Se está tomando otro usuario en lugar de farmacéutico
   - **Solución**: Verificar que el nombre de usuario es exacto

### 3. ❌ El rol está guardado con mayúsculas en Supabase
   - **Síntoma**: session["usuario_rol"] = "Farmaceutico" en lugar de "farmaceutico"
   - **Solución**: Convertir a minúsculas (ya implementado en login.py)

## Cómo Diagnosticar

### Paso 1: Ver información de sesión actual
1. Inicia sesión como **farmacéutico**
2. Abre: `http://localhost:5000/debug-usuario`
3. **Nota exactamente**:
   - ¿Qué dice `usuario_nombre`?
   - ¿Qué dice `usuario_rol`?

### Paso 2: Verificar Supabase
1. Abre Supabase dashboard
2. Ve a tabla `usuarios`
3. Busca el usuario con nombre = al que viste en el paso 1
4. Verifica que su `rol` sea `farmaceutico` (sin mayúsculas, sin tilde)

### Paso 3: Comparar
- Si `usuario_rol` en sesión NO es `farmaceutico` → Problema en Supabase
- Si `usuario_rol` EN sesión ES `farmaceutico` → Problema en el sidebar o BD

## Posibles Soluciones

### Solución A: Si el usuario farmacéutico tiene rol incorrecto en Supabase
```sql
UPDATE usuarios 
SET rol = 'farmaceutico'
WHERE nombre = 'nombreDelUsuario'
```

### Solución B: Si el nombre del usuario es diferente
Verifica que el nombre exacto sea el que estás usando para iniciar sesión.

### Solución C: Si hay múltiples usuarios farmacéutico
El login busca POR NOMBRE primero:
```python
usuario_encontrado = next(
    (u for u in usuarios if u.get("nombre") == usuario_input 
     or u.get("correo") == usuario_input 
     or u.get("rut_usuario") == usuario_input),
    None
)
```
Asegúrate que haya solo UN usuario con ese nombre.

## Verificación Rápida

### En la terminal (si tienes Python):
```python
from api.conexion_supabase import supabase

usuarios = supabase.table('usuarios').select('nombre, rol, rut_usuario').execute().data
for u in usuarios:
    print(f"{u.get('nombre'):20} → {u.get('rol'):15} (RUT: {u.get('rut_usuario')})")
```

### En Supabase UI:
Tabla `usuarios` → Busca la columna `rol` → Verifica que sea:
- ✅ `farmaceutico` (minúsculas, sin tilde)
- ✅ No `Farmaceutico` o `FARMACEUTICO`
- ✅ No `farmacéutico` (con tilde)

## Estado Esperado

Cuando inicies como **farmacéutico** deberías ver:
- usuario_nombre: `farmacéutico` (o el nombre que uses para iniciar)
- usuario_rol: `farmaceutico`
- Sidebar: Solo Dashboard, Inventario, Perfil

## Si Sigue Sin Funcionar

1. **Limpia caché completo**: Ctrl+Shift+Delete
2. **Cierra navegador completamente**
3. **Limpia cookies de la aplicación**
4. **Reabre navegador e inicia sesión nuevamente**
5. **Si persiste, reporta:**
   - Lo que ves en `/debug-usuario`
   - Lo que dice Supabase para ese usuario
   - Exactamente qué escribiste para iniciar sesión

---

**Herramientas de Debug Disponibles:**
- `http://localhost:5000/debug-sesion` (JSON)
- `http://localhost:5000/debug-sesion-visual` (Visual)
- `http://localhost:5000/debug-usuario` (Detallado)
