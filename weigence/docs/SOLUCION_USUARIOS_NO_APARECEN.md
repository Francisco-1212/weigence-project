# 🔧 Solución: Usuarios no se muestran

## ¿Qué hice?

Creé una versión **simple y funcional** del script `usuarios_simple.js` que:
- ✅ Carga usuarios del API
- ✅ Los muestra en tabla
- ✅ Abre modal para crear
- ✅ Tiene logs detallados en consola

## Pasos para Verificar

### 1. Recarga la Página
```
http://localhost:5000/usuarios
Presiona: Ctrl + F5 (limpiar caché)
```

### 2. Abre DevTools
```
Presiona: F12
Ve a: Console
```

### 3. Verifica los Logs
Deberías ver:
```
[USUARIOS.JS] Script cargado
[USUARIOS] DOM listo, inicializando...
[USUARIOS] Elementos encontrados: {...}
[USUARIOS] Cargando usuarios...
[USUARIOS] Datos recibidos: {...}
[USUARIOS] Tabla actualizada con X usuarios
```

### 4. Verifica Errores
Si hay errores rojos, cópialos completos

## Si Sigue Sin Funcionar

### Opción A: Revisar API
En DevTools Console, ejecuta:
```javascript
fetch('/api/usuarios')
  .then(r => r.json())
  .then(d => console.log(d))
```

Debería mostrar los usuarios.

### Opción B: Revisar Permisos
- ¿Estás logueado como Jefe o Admin?
- ¿Sidebar muestra "Usuarios"?
- Si no, no tienes permisos

### Opción C: Botón Crear
Haz click en "Nuevo Usuario" y dime qué pasa

## Comando Para Probar Todo

En la consola del navegador (F12), ejecuta:
```javascript
console.log('Rol:', localStorage.getItem('usuario_rol') || 'no found');
fetch('/debug-usuario').then(r => r.text()).then(html => {
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  console.log('Debug:', doc.body.innerText);
});
```

---

**Nota**: Estoy usando `usuarios_simple.js` temporalmente. Es más fácil de debuggear.
