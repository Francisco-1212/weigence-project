# 🚀 Chat 1:1 - Instalación Rápida

## ⚡ **QUICK START (3 pasos)**

### 1️⃣ Instalar dependencias
```powershell
pip install flask-socketio python-socketio python-engineio
```

### 2️⃣ Iniciar servidor
```powershell
python app.py
```

### 3️⃣ ¡Listo!
Abre `http://localhost:5000/chat`

---

## 📁 **ARCHIVOS CREADOS**

```
app/
├── db/
│   ├── __init__.py           ✅ Nuevo
│   └── chat_queries.py       ✅ Nuevo (500+ líneas)
│
├── routes/
│   ├── chat.py               ✅ Reescrito (51 líneas)
│   └── chat_api.py           ✅ Nuevo (300+ líneas)
│
├── sockets/
│   ├── __init__.py           ✅ Nuevo
│   └── chat_ws.py            ✅ Nuevo (350+ líneas)
│
├── __init__.py               ✅ Modificado (SocketIO agregado)
└── requirements.txt          ✅ Modificado (Flask-SocketIO)

app.py                         ✅ Modificado (WebSocket)
```

---

## 🎯 **LO QUE TIENES AHORA**

### ✅ Backend completo
- 6 endpoints API REST
- WebSocket tiempo real
- Consultas SQL optimizadas
- Seguridad y validaciones

### ✅ Compatible con tu frontend
- Tu `chat.js` funciona SIN CAMBIOS
- API cumple con formato esperado
- Campos `apellido`, `iniciales`, etc. incluidos

---

## 📡 **API ENDPOINTS**

```
GET  /api/chat/usuarios           # Lista usuarios
GET  /api/chat/conversaciones     # Conversaciones del usuario
POST /api/chat/conversacion/crear # Crear conversación 1:1
GET  /api/chat/mensajes/<id>      # Historial de mensajes
POST /api/chat/mensaje/enviar     # Enviar mensaje
POST /api/chat/mensaje/marcar-leido # Marcar leídos
```

---

## ⚡ **WebSocket Events**

### Cliente → Servidor
- `unirse_conversacion`
- `salir_conversacion`
- `mensaje_enviar`
- `escribiendo`

### Servidor → Cliente
- `mensaje_recibido`
- `usuario_escribiendo`
- `nueva_conversacion`

---

## 🔧 **TROUBLESHOOTING**

### Si el servidor no arranca:
```powershell
pip install --upgrade flask-socketio
```

### Si dice "Puerto en uso":
El sistema automáticamente probará 5001, 5002, etc.

### Si no aparecen mensajes en tiempo real:
El sistema tiene fallback a polling. WebSocket es opcional.

---

## 📖 **DOCUMENTACIÓN COMPLETA**

Ver: `CHAT_SISTEMA_COMPLETO.md`

---

## ✅ **CHECKLIST**

- [x] Backend Flask completo
- [x] WebSocket SocketIO
- [x] Consultas SQL optimizadas
- [x] API REST con 6 endpoints
- [x] Compatible con chat.js existente
- [x] Código limpio y documentado
- [x] Seguridad y validaciones
- [x] Logging completo
- [x] Sin modificar frontend

---

## 🎉 **SISTEMA LISTO**

Tu chat 1:1 profesional está completo y funcional.

**Ejecuta:**
```powershell
python app.py
```

**Y empieza a chatear** 💬✨
