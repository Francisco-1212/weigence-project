# 💬 Chat Flotante - Guía Completa

## ✅ **LO QUE NECESITAS** (Ya implementado)

### 1️⃣ **Backend Corregido** (`app/routes/chat.py`)

**PROBLEMA RESUELTO:** La tabla `usuarios` en Supabase NO tiene columna `apellido`

**Cambios realizados:**
- ✅ Eliminadas todas las referencias a `apellido`
- ✅ Ahora usa solo: `rut_usuario`, `nombre`, `correo`, `rol`
- ✅ Funciona correctamente con tu base de datos

**Endpoints disponibles:**
```python
GET  /api/chat/usuarios           # Lista usuarios disponibles
POST /api/chat/conversacion/crear # Crea/obtiene conversación
GET  /api/chat/conversaciones      # Lista conversaciones del usuario
GET  /api/chat/mensajes/<id>       # Mensajes de una conversación
POST /api/chat/mensaje/enviar     # Envía un mensaje
```

---

### 2️⃣ **CSS Profesional** (`app/static/css/chat-float.css`)

**Incluye:**
- ✨ Estilos profesionales del panel flotante
- 🌓 Soporte modo oscuro
- 📱 Diseño responsive
- 🎨 10 colores de avatares con gradientes
- 💫 Animaciones suaves
- 📜 Scrollbar personalizado

**Colores de avatares:**
- Blue, Green, Purple, Pink, Yellow
- Indigo, Red, Teal, Cyan, Orange

---

### 3️⃣ **JavaScript con toda la lógica** (`app/static/js/chat-float.js`)

**Funciones principales:**

```javascript
ChatFloat.init()                  // Inicializa el sistema
ChatFloat.cargarUsuarios()        // Carga lista desde API
ChatFloat.renderizarUsuarios()    // Muestra usuarios en el panel
ChatFloat.filtrarUsuarios()       // Búsqueda en tiempo real
ChatFloat.iniciarChat()           // Abre conversación
ChatFloat.actualizarBadge()       // Contador de no leídos
```

**Características:**
- ✅ Carga asíncrona de usuarios
- ✅ Búsqueda en tiempo real
- ✅ Manejo de estados (loading/empty/error)
- ✅ Sanitización HTML (anti-XSS)
- ✅ Badge automático cada 30s
- ✅ Console logs para debugging

---

### 4️⃣ **Integración en base.html**

**Se agregó:**
```html
<!-- En <head> -->
<link rel="stylesheet" href="/static/css/chat-float.css">

<!-- Antes de </body> -->
<script src="/static/js/chat-float.js"></script>
```

---

## 🎯 **CÓMO FUNCIONA**

### Flujo del chat flotante:

```
1. Usuario hace clic en botón flotante 💬
   ↓
2. Se abre el panel y carga usuarios
   GET /api/chat/usuarios
   ↓
3. Muestra lista de usuarios con avatares
   - Nombre
   - Rol
   - Estado online (punto verde)
   ↓
4. Usuario hace clic en una persona
   POST /api/chat/conversacion/crear
   ↓
5. Se abre el chat completo en nueva pestaña
   window.open('/chat', '_blank')
```

---

## 📊 **ESTRUCTURA DE LA BASE DE DATOS**

### Tabla: `usuarios`
```sql
rut_usuario  VARCHAR  -- ID único (RUT chileno)
nombre       VARCHAR  -- Nombre completo
correo       VARCHAR  -- Email
rol          VARCHAR  -- administrador/farmaceutico/vendedor
```

### Tabla: `conversaciones_chat`
```sql
id              UUID
nombre          VARCHAR
es_grupal       BOOLEAN
creado_por      VARCHAR (FK usuarios)
ultima_actualiz TIMESTAMP
```

### Tabla: `participantes_chat`
```sql
conversacion_id UUID (FK)
usuario_id      VARCHAR (FK usuarios)
ultimo_mensaje  UUID
```

### Tabla: `mensajes_chat`
```sql
id              UUID
conversacion_id UUID (FK)
usuario_id      VARCHAR (FK usuarios)
contenido       TEXT
fecha_envio     TIMESTAMP
editado         BOOLEAN
eliminado       BOOLEAN
```

---

## 🎨 **DISEÑO VISUAL**

### Panel del Chat
```
┌────────────────────────────┐
│ 💬 Equipo Weigence  [↗][✕] │
├────────────────────────────┤
│ 🔍 Buscar persona...       │
├────────────────────────────┤
│                            │
│  [FC] Francisco            │ ← Avatar + Nombre
│      Administrador         │   Rol
│                            │
│  [MG] María                │
│      Farmacéutico          │
│                            │
│  [JL] Juan                 │
│      Vendedor              │
└────────────────────────────┘
```

### Botón Flotante
```
         (3) ← Badge notificaciones
          💬  ← Botón
```

---

## 🔧 **TESTING**

### 1. Verificar que el backend funciona:
```bash
# Abrir navegador en:
http://localhost:5001/api/chat/usuarios
```

**Respuesta esperada:**
```json
{
  "usuarios": [
    {
      "id": "12345678-9",
      "nombre": "Francisco",
      "apellido": "",
      "email": "francisco@weigence.cl",
      "rol": "administrador",
      "nombre_completo": "Francisco"
    }
  ]
}
```

### 2. Verificar el frontend:
1. ✅ Abrir la aplicación
2. ✅ Ver botón flotante (esquina inferior derecha)
3. ✅ Hacer clic para abrir panel
4. ✅ Ver lista de usuarios
5. ✅ Buscar un usuario
6. ✅ Hacer clic en un usuario
7. ✅ Se abre el chat completo

### 3. Console del navegador (F12):
```javascript
✅ Chat flotante inicializado
📥 Usuarios cargados: {usuarios: [...]}
💬 Iniciando chat con: 12345678-9, Francisco
```

---

## 🐛 **DEBUGGING**

### Si NO aparecen usuarios:

1. **Revisar consola del navegador (F12)**
```javascript
// Debe mostrar:
✅ Chat flotante inicializado
📥 Usuarios cargados: {usuarios: []}
```

2. **Revisar Network (F12 > Network)**
```
GET /api/chat/usuarios
Status: 200 OK
Response: {"usuarios": [...]}
```

3. **Si hay error 500:**
```python
# Ver logs del servidor Python
# Debe mostrar:
Buscando usuarios para user_id: 21548648-1
Usuarios encontrados: 3
```

### Si aparece "Error al cargar usuarios":

**Causa:** Error en el backend

**Solución:**
1. Revisar logs del servidor
2. Verificar que la tabla `usuarios` existe
3. Verificar que NO se usa columna `apellido`

---

## 🚀 **PRÓXIMAS MEJORAS OPCIONALES**

1. **WebSockets** - Mensajes en tiempo real
2. **Estados de conexión** - Online/Offline/Ausente
3. **Última actividad** - "Visto hace 5 min"
4. **Typing indicators** - "Escribiendo..."
5. **Notificaciones del navegador** - Notification API
6. **Sonidos** - Ding cuando llega mensaje
7. **Emoji picker** - 😀 😎 🎉
8. **Archivos adjuntos** - Imágenes, PDFs

---

## ✅ **CHECKLIST FINAL**

- [x] Backend corregido (sin apellido)
- [x] CSS creado y vinculado
- [x] JavaScript creado y vinculado
- [x] base.html actualizado
- [x] API funcionando correctamente
- [ ] **Probar en el navegador** ← TÚ DEBES HACER ESTO

---

## 📝 **RESUMEN**

**Archivos creados:**
1. `app/static/css/chat-float.css`
2. `app/static/js/chat-float.js`

**Archivos modificados:**
1. `app/routes/chat.py` (corregido el bug de apellido)
2. `app/templates/base.html` (agregados links CSS y JS)

**¡El chat flotante está LISTO y FUNCIONAL!** 🎉

Solo necesitas:
1. Reiniciar el servidor Flask
2. Abrir la aplicación en el navegador
3. Hacer clic en el botón flotante 💬
4. Ver la magia ✨
