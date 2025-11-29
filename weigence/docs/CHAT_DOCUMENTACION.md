# Sistema de Chat en Tiempo Real - Weigence

## 📋 Descripción

Sistema de mensajería instantánea integrado que permite la comunicación en tiempo real entre usuarios de la plataforma Weigence.

## ✨ Características

### Funcionalidades Principales
- ✅ **Conversaciones individuales**: Chat 1 a 1 entre usuarios
- ✅ **Historial persistente**: Todos los mensajes se guardan en la base de datos
- ✅ **Mensajes no leídos**: Contador de mensajes pendientes por leer
- ✅ **Actualización en tiempo real**: Polling cada 5 segundos para nuevos mensajes
- ✅ **Búsqueda**: Filtrado de conversaciones y usuarios
- ✅ **Interfaz responsive**: Optimizada para móvil y desktop
- ✅ **Modo oscuro**: Compatible con el tema de la aplicación

### Características de la Interfaz
- **Panel izquierdo**: Lista de conversaciones con últimos mensajes
- **Panel derecho**: Área de chat activa con mensajes
- **Modal de nuevo chat**: Selector de usuarios disponibles
- **Indicadores visuales**: Avatares, timestamps, estado de lectura

## 🗄️ Estructura de Base de Datos

### Tablas

#### `conversaciones_chat`
```sql
- id: UUID (PK)
- nombre: VARCHAR(255)
- es_grupal: BOOLEAN
- creado_por: INTEGER (FK a usuarios)
- fecha_creacion: TIMESTAMP
- ultima_actualizacion: TIMESTAMP
```

#### `participantes_chat`
```sql
- id: UUID (PK)
- conversacion_id: UUID (FK a conversaciones_chat)
- usuario_id: INTEGER (FK a usuarios)
- fecha_ingreso: TIMESTAMP
- ultimo_mensaje_leido: UUID
```

#### `mensajes_chat`
```sql
- id: UUID (PK)
- conversacion_id: UUID (FK a conversaciones_chat)
- usuario_id: INTEGER (FK a usuarios)
- contenido: TEXT
- fecha_envio: TIMESTAMP
- editado: BOOLEAN
- eliminado: BOOLEAN
```

## 🚀 Instalación

### 1. Crear las tablas en Supabase

Ejecuta el script de migración:

```bash
python scripts/setup_chat.py
```

Luego copia el SQL generado y ejecútalo en el SQL Editor de Supabase:
https://supabase.com/dashboard/project/_/sql

### 2. Verificar instalación

Las siguientes tablas deben existir:
- `conversaciones_chat`
- `participantes_chat`
- `mensajes_chat`

### 3. Acceder al chat

Navega a: `http://localhost:5000/chat`

## 📡 API Endpoints

### GET `/api/chat/conversaciones`
Obtiene todas las conversaciones del usuario actual.

**Response:**
```json
{
  "conversaciones": [
    {
      "id": "uuid",
      "nombre": "string",
      "es_grupal": false,
      "participantes": [...],
      "ultimo_mensaje": {...},
      "mensajes_no_leidos": 0
    }
  ]
}
```

### GET `/api/chat/usuarios`
Obtiene la lista de usuarios disponibles para chatear.

**Response:**
```json
{
  "usuarios": [
    {
      "id": 1,
      "nombre": "Juan",
      "apellido": "Pérez",
      "email": "juan@example.com",
      "rol": "operador"
    }
  ]
}
```

### POST `/api/chat/conversacion/crear`
Crea una nueva conversación.

**Request:**
```json
{
  "participantes": [1, 2],
  "nombre": "Opcional para grupos"
}
```

**Response:**
```json
{
  "conversacion": {...},
  "existe": false
}
```

### GET `/api/chat/mensajes/<conversacion_id>`
Obtiene los mensajes de una conversación.

**Response:**
```json
{
  "mensajes": [
    {
      "id": "uuid",
      "contenido": "Hola!",
      "fecha_envio": "2025-11-25T10:30:00",
      "usuario": {...},
      "es_propio": true
    }
  ]
}
```

### POST `/api/chat/mensaje/enviar`
Envía un nuevo mensaje.

**Request:**
```json
{
  "conversacion_id": "uuid",
  "contenido": "Hola!"
}
```

### POST `/api/chat/mensaje/marcar-leido`
Marca mensajes como leídos.

**Request:**
```json
{
  "conversacion_id": "uuid",
  "mensaje_id": "uuid"
}
```

## 🎨 Interfaz de Usuario

### Componentes Principales

#### Lista de Conversaciones
- Avatar del usuario/grupo
- Nombre de la conversación
- Último mensaje (truncado)
- Timestamp
- Contador de mensajes no leídos

#### Área de Chat
- Header con información del contacto
- Contenedor de mensajes scrolleable
- Input para escribir mensaje
- Botón de envío

#### Modal Nuevo Chat
- Búsqueda de usuarios
- Lista de usuarios disponibles con:
  - Avatar
  - Nombre completo
  - Email
  - Rol

### Estilos CSS

El chat utiliza las variables CSS del tema principal:
- `--bg-light` / `--bg-dark`: Fondo general
- `--card-bg-light` / `--card-bg-dark`: Tarjetas y paneles
- `--primary-color`: Color de acento (mensajes propios)
- `--text-light` / `--text-dark`: Texto principal

## 🔧 Configuración

### Polling Interval

El chat actualiza las conversaciones cada 5 segundos. Para cambiar esto, edita en `chat.js`:

```javascript
iniciarPolling() {
  this.state.polling = setInterval(async () => {
    // ...
  }, 5000); // Cambiar este valor (en milisegundos)
}
```

### Formato de Fechas

Las fechas se muestran en formato español. Para cambiar, edita las funciones en `chat.js`:

```javascript
formatearFecha(fecha) {
  // Personalizar aquí
}

formatearHora(fecha) {
  // Personalizar aquí
}
```

## 🔒 Seguridad

### Autenticación
- Todas las rutas verifican que el usuario esté autenticado
- Se usa la sesión de Flask para identificar al usuario

### Autorización
- Los usuarios solo pueden ver conversaciones en las que participan
- No se pueden leer mensajes de conversaciones ajenas

### CSRF Protection
- Todos los POST requests incluyen token CSRF
- Se obtiene del meta tag en el header

### Sanitización
- El contenido de los mensajes se escapa en el frontend
- Prevención de XSS al renderizar mensajes

## 📱 Responsive Design

### Breakpoints

- **Móvil** (< 640px):
  - Panel de conversaciones ocupa todo el ancho
  - Al seleccionar chat, se oculta lista de conversaciones
  
- **Tablet** (640px - 1024px):
  - Panel de conversaciones: 320px (w-80)
  - Chat ocupa el resto del espacio
  
- **Desktop** (> 1024px):
  - Panel de conversaciones: 384px (w-96)
  - Chat ocupa el resto del espacio

## 🐛 Troubleshooting

### Los mensajes no se actualizan
- Verifica que el polling esté activo (consola del navegador)
- Revisa la consola del backend para errores
- Confirma que las tablas existen en Supabase

### No aparecen usuarios disponibles
- Verifica que existan otros usuarios en la tabla `usuarios`
- Confirma que el usuario actual está autenticado
- Revisa los permisos en Supabase

### Error al crear conversación
- Verifica que las tablas tengan las relaciones correctas
- Confirma que el trigger `actualizar_conversacion_timestamp` existe
- Revisa los logs del backend

### Mensajes duplicados
- Aumenta el intervalo de polling
- Verifica que no haya múltiples instancias del JavaScript

## 🚀 Futuras Mejoras

### Funcionalidades Planeadas
- [ ] **Grupos**: Conversaciones con múltiples participantes
- [ ] **Archivos adjuntos**: Envío de imágenes y documentos
- [ ] **Reacciones**: Emojis en mensajes
- [ ] **Edición de mensajes**: Modificar mensajes enviados
- [ ] **WebSockets**: Actualización en tiempo real sin polling
- [ ] **Notificaciones push**: Alertas de nuevos mensajes
- [ ] **Búsqueda en mensajes**: Buscar contenido específico
- [ ] **Mensajes de voz**: Grabación y envío de audio
- [ ] **Videollamadas**: Integración de llamadas

### Optimizaciones Técnicas
- [ ] Caché de conversaciones en memoria
- [ ] Lazy loading de mensajes antiguos
- [ ] Compresión de imágenes
- [ ] Índices adicionales en BD
- [ ] Rate limiting por usuario

## 📄 Licencia

Este sistema es parte del proyecto Weigence y está sujeto a las mismas condiciones de licencia.

## 👥 Soporte

Para reportar problemas o sugerir mejoras, contacta al equipo de desarrollo de Weigence.
