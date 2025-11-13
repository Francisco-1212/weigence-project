# 🔍 Guía para Diagnosticar el Problema del Sidebar

## El Problema
Solo aparece Dashboard en el sidebar para jefe, administrador y supervisor.

## Cambios Realizados ✅

1. **Login.py** - El rol ahora se convierte a minúsculas
   ```python
   session["usuario_rol"] = str(usuario_encontrado.get("rol", "")).lower()
   ```

2. **Sidebar.html** - Corregidas las validaciones de permisos:
   - ✅ Alertas: ahora incluye bodeguera, supervisor, jefe, administrador
   - ✅ Historial: agregado para jefe, administrador
   - ✅ Recomendaciones: agregado para jefe, administrador

## Para Diagnosticar el Problema

### Opción 1: Ver datos de sesión en JSON
1. Inicia sesión en la aplicación
2. Abre: `http://localhost:5000/debug-sesion`
3. Verifica que `usuario_rol` esté en minúsculas y sea correcto

### Opción 2: Ver datos de sesión visualmente
1. Inicia sesión en la aplicación
2. Abre: `http://localhost:5000/debug-sesion-visual`
3. Verifica las comparaciones de rol

## Checklist de Verificación

- [ ] ¿El `usuario_rol` en sesión es minúsculas? (`jefe`, `bodeguera`, `supervisor`, etc.)
- [ ] ¿Los valores coinciden exactamente? (sin espacios extra)
- [ ] ¿Se actualizó el código después del login.py cambio?
- [ ] ¿Se recargó el navegador después de los cambios?

## Pasos para Resolver

### Paso 1: Verificar Base de Datos
Los roles en Supabase deben estar exactamente así:
- `farmaceutico` (sin tilde)
- `bodeguera`
- `supervisor`
- `jefe`
- `administrador`

### Paso 2: Limpiar Caché del Navegador
Presiona: `Ctrl + Shift + Delete` y limpia el caché

### Paso 3: Cerrar Sesión y Volver a Iniciar
1. Cierra sesión
2. Recarga la página
3. Inicia sesión nuevamente

### Paso 4: Si Sigue Sin Funcionar
Revisa la consola del navegador (F12) y busca errores de JavaScript

## Verificación Rápida

Después de iniciar sesión como Jefe, deberías ver:
- ✅ Dashboard
- ✅ Inventario  
- ✅ Movimientos
- ✅ Alertas
- ✅ Auditoría
- ✅ Historial
- ✅ Usuarios
- ✅ Recomendaciones

Si solo ves Dashboard, algo está mal con las variables de sesión o las condiciones Jinja2.

## Debug Code (si necesitas modificar sidebar.html)

Para verificar qué rol tiene el usuario, añade esto temporalmente al sidebar.html al inicio:

```html
<!-- DEBUG: Mostrar rol actual -->
<div style="background: yellow; padding: 10px; margin: 10px;">
  Rol actual: {{ session.get('usuario_rol') }} (tipo: {{ session.get('usuario_rol').__class__.__name__ }})
</div>
```

Luego elimínalo cuando verifiques que funciona.
