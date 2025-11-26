// ===========================================================
// EJEMPLO: Integración WebSocket en chat.js (OPCIONAL)
// ===========================================================
// Tu chat.js YA funciona sin esto.
// Esto es solo si quieres reemplazar polling por WebSocket.

// 1. AGREGAR SOCKET.IO CLIENT
// En base.html o chat.html:
// <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

// 2. CONECTAR AL WEBSOCKET
const socket = io();

// Evento: Conexión establecida
socket.on('conectado', (data) => {
  console.log('✅ WebSocket:', data.mensaje);
});

// 3. UNIRSE A CONVERSACIÓN AL ABRIRLA
// Modificar función abrirConversacion en chat.js:

/*
async abrirConversacion(conv) {
  this.state.conversacionActual = conv;
  
  // 🔥 NUEVO: Unirse a la sala WebSocket
  socket.emit('unirse_conversacion', {
    conversacion_id: conv.id
  });
  
  // Actualizar UI
  this.dom.sinConversacion.classList.add('hidden');
  this.dom.areaConversacion.classList.remove('hidden');
  
  // ... resto del código existente
}
*/

// 4. RECIBIR MENSAJES EN TIEMPO REAL
// Agregar al final de chat.js:

/*
socket.on('mensaje_recibido', (mensaje) => {
  console.log('📨 Nuevo mensaje:', mensaje);
  
  // Si el mensaje es de la conversación actual, mostrarlo
  if (mensaje.conversacion_id === Chat.state.conversacionActual?.id) {
    agregarMensajeAlDOM(mensaje);
  }
  
  // Actualizar lista de conversaciones
  actualizarUltimoMensaje(mensaje.conversacion_id, mensaje);
  
  // Actualizar badge de no leídos
  if (mensaje.usuario_id !== getCurrentUserId()) {
    incrementarBadge(mensaje.conversacion_id);
  }
});
*/

// 5. INDICADOR "ESCRIBIENDO..."
// Agregar al input de mensaje:

/*
this.dom.inputMensaje.addEventListener('input', () => {
  if (this.state.conversacionActual) {
    socket.emit('escribiendo', {
      conversacion_id: this.state.conversacionActual.id
    });
  }
});

socket.on('usuario_escribiendo', (data) => {
  if (data.conversacion_id === this.state.conversacionActual?.id) {
    mostrarIndicadorEscribiendo(data.nombre);
    
    // Ocultar después de 3 segundos
    setTimeout(() => ocultarIndicadorEscribiendo(), 3000);
  }
});
*/

// 6. ENVIAR MENSAJE (OPCIONAL - Puedes seguir usando fetch)
// Tu código actual con fetch funciona perfecto.
// Pero si quieres usar solo WebSocket:

/*
async enviarMensaje() {
  const contenido = this.dom.inputMensaje.value.trim();
  
  if (!contenido || !this.state.conversacionActual) return;
  
  // 🔥 ENVIAR POR WEBSOCKET
  socket.emit('mensaje_enviar', {
    conversacion_id: this.state.conversacionActual.id,
    contenido: contenido
  });
  
  // Limpiar input
  this.dom.inputMensaje.value = '';
}
*/

// ===========================================================
// FUNCIONES AUXILIARES
// ===========================================================

function agregarMensajeAlDOM(mensaje) {
  // Tu lógica existente para agregar mensaje al DOM
  const esPropio = mensaje.usuario_id === getCurrentUserId();
  
  const html = `
    <div class="mensaje ${esPropio ? 'mensaje-propio' : 'mensaje-otro'}">
      <div class="mensaje-contenido">
        ${mensaje.contenido}
      </div>
      <span class="mensaje-hora">${formatearHora(mensaje.fecha_envio)}</span>
    </div>
  `;
  
  document.getElementById('mensajes-contenedor').insertAdjacentHTML('beforeend', html);
  scrollToBottom();
}

function actualizarUltimoMensaje(conversacionId, mensaje) {
  // Actualizar el último mensaje en la lista de conversaciones
  const conv = Chat.state.conversaciones.find(c => c.id === conversacionId);
  if (conv) {
    conv.ultimo_mensaje = mensaje;
    Chat.renderizarConversaciones();
  }
}

function incrementarBadge(conversacionId) {
  const conv = Chat.state.conversaciones.find(c => c.id === conversacionId);
  if (conv) {
    conv.mensajes_no_leidos = (conv.mensajes_no_leidos || 0) + 1;
    Chat.renderizarConversaciones();
  }
}

function mostrarIndicadorEscribiendo(nombre) {
  const indicador = document.getElementById('indicador-escribiendo');
  indicador.textContent = `${nombre} está escribiendo...`;
  indicador.classList.remove('hidden');
}

function ocultarIndicadorEscribiendo() {
  const indicador = document.getElementById('indicador-escribiendo');
  indicador.classList.add('hidden');
}

function getCurrentUserId() {
  // Obtener del DOM o sesión
  return document.querySelector('[data-user-id]')?.dataset.userId;
}

function formatearHora(timestamp) {
  const fecha = new Date(timestamp);
  return fecha.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
  const container = document.getElementById('mensajes-contenedor');
  container.scrollTop = container.scrollHeight;
}

// ===========================================================
// NOTA IMPORTANTE
// ===========================================================
// 
// TU CHAT.JS ACTUAL YA FUNCIONA PERFECTO con el backend.
// Este archivo es SOLO si quieres agregar WebSocket.
// 
// El backend SIEMPRE emite eventos WebSocket cuando:
// - Se envía un mensaje via POST /api/chat/mensaje/enviar
// - Se crea una conversación
// - Alguien está escribiendo
// 
// Así que puedes agregar WebSocket cuando quieras,
// sin romper nada. El sistema es 100% compatible.
// 
// ===========================================================
