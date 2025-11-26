// ===========================================================
// Sistema de Chat en Tiempo Real - Weigence
// ===========================================================

const Chat = {
  state: {
    conversacionActual: null,
    conversaciones: [],
    usuarios: [],
    mensajes: {},
    polling: null
  },

  init() {
    this.cacheDOM();
    this.bindEvents();
    this.cargarConversaciones();
    this.iniciarPolling();
    console.info("Chat inicializado correctamente");
  },

  cacheDOM() {
    this.dom = {
      listaConversaciones: document.getElementById('lista-conversaciones'),
      areaConversacion: document.getElementById('area-conversacion'),
      sinConversacion: document.getElementById('sin-conversacion'),
      mensajesContenedor: document.getElementById('mensajes-contenedor'),
      chatNombre: document.getElementById('chat-nombre'),
      chatInfo: document.getElementById('chat-info'),
      chatAvatar: document.getElementById('chat-avatar'),
      inputMensaje: document.getElementById('input-mensaje'),
      formEnviar: document.getElementById('form-enviar-mensaje'),
      btnNuevoChat: document.getElementById('btn-nuevo-chat'),
      modalNuevoChat: document.getElementById('modal-nuevo-chat'),
      cerrarModal: document.getElementById('cerrar-modal'),
      modalBackdrop: document.getElementById('modal-backdrop'),
      listaUsuarios: document.getElementById('lista-usuarios'),
      buscarUsuario: document.getElementById('buscar-usuario'),
      buscarConversacion: document.getElementById('buscar-conversacion')
    };
  },

  bindEvents() {
    this.dom.formEnviar.addEventListener('submit', (e) => {
      e.preventDefault();
      this.enviarMensaje();
    });

    this.dom.btnNuevoChat.addEventListener('click', () => this.abrirModalNuevoChat());
    this.dom.cerrarModal.addEventListener('click', () => this.cerrarModal());
    this.dom.modalBackdrop.addEventListener('click', () => this.cerrarModal());

    this.dom.buscarUsuario.addEventListener('input', (e) => this.filtrarUsuarios(e.target.value));
    this.dom.buscarConversacion.addEventListener('input', (e) => this.filtrarConversaciones(e.target.value));
  },

  async cargarConversaciones() {
    try {
      const response = await fetch('/api/chat/conversaciones');
      const data = await response.json();
      
      if (data.conversaciones) {
        this.state.conversaciones = data.conversaciones;
        this.renderizarConversaciones();
      }
    } catch (error) {
      console.error('Error al cargar conversaciones:', error);
    }
  },

  renderizarConversaciones(filtro = '') {
    const conversaciones = filtro 
      ? this.state.conversaciones.filter(c => 
          this.obtenerNombreConversacion(c).toLowerCase().includes(filtro.toLowerCase())
        )
      : this.state.conversaciones;

    if (conversaciones.length === 0) {
      this.dom.listaConversaciones.innerHTML = `
        <div class="p-8 text-center text-neutral-500 dark:text-neutral-400">
          <span class="material-symbols-outlined text-4xl mb-2 opacity-50">chat</span>
          <p class="text-sm">No hay conversaciones</p>
        </div>
      `;
      return;
    }

    this.dom.listaConversaciones.innerHTML = conversaciones.map(conv => {
      const nombre = this.obtenerNombreConversacion(conv);
      const avatar = this.obtenerAvatarConversacion(conv);
      const ultimoMensaje = conv.ultimo_mensaje;
      const noLeidos = conv.mensajes_no_leidos || 0;
      const activa = this.state.conversacionActual?.id === conv.id;

      return `
        <div class="conversacion-item p-3 border-b border-gray-200 dark:border-neutral-700 cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors ${activa ? 'bg-neutral-100 dark:bg-neutral-800' : ''}"
             data-id="${conv.id}">
          <div class="flex items-start gap-3">
            <div class="w-12 h-12 rounded-full bg-[var(--primary-color)] flex items-center justify-center text-white font-bold flex-shrink-0">
              ${avatar}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-start mb-1">
                <h4 class="font-semibold text-neutral-900 dark:text-neutral-100 truncate">${nombre}</h4>
                ${noLeidos > 0 ? `<span class="ml-2 px-2 py-0.5 rounded-full bg-[var(--primary-color)] text-white text-xs font-bold flex-shrink-0">${noLeidos}</span>` : ''}
              </div>
              ${ultimoMensaje ? `
                <p class="text-sm text-neutral-600 dark:text-neutral-400 truncate">
                  ${this.truncarTexto(ultimoMensaje.contenido, 40)}
                </p>
                <p class="text-xs text-neutral-400 dark:text-neutral-500 mt-1">
                  ${this.formatearFecha(ultimoMensaje.fecha_envio)}
                </p>
              ` : '<p class="text-sm text-neutral-400">Sin mensajes</p>'}
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Event listeners para las conversaciones
    this.dom.listaConversaciones.querySelectorAll('.conversacion-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        const conv = this.state.conversaciones.find(c => c.id === id);
        if (conv) this.abrirConversacion(conv);
      });
    });
  },

  obtenerNombreConversacion(conv) {
    if (conv.es_grupal) {
      return conv.nombre || 'Grupo sin nombre';
    }
    const participante = conv.participantes[0];
    return participante ? `${participante.nombre} ${participante.apellido}` : 'Usuario';
  },

  obtenerAvatarConversacion(conv) {
    if (conv.es_grupal) {
      return '<span class="material-symbols-outlined">groups</span>';
    }
    const participante = conv.participantes[0];
    return participante ? (participante.nombre[0] + (participante.apellido[0] || '')).toUpperCase() : 'U';
  },

  async abrirConversacion(conv) {
    this.state.conversacionActual = conv;
    
    // Actualizar UI
    this.dom.sinConversacion.classList.add('hidden');
    this.dom.areaConversacion.classList.remove('hidden');
    
    const nombre = this.obtenerNombreConversacion(conv);
    const avatar = this.obtenerAvatarConversacion(conv);
    
    this.dom.chatNombre.textContent = nombre;
    this.dom.chatAvatar.innerHTML = avatar;
    
    if (conv.es_grupal) {
      this.dom.chatInfo.textContent = `${conv.participantes.length + 1} participantes`;
    } else {
      const participante = conv.participantes[0];
      this.dom.chatInfo.textContent = participante?.email || '';
    }
    
    // Cargar mensajes
    await this.cargarMensajes(conv.id);
    
    // Renderizar lista para actualizar estado activo
    this.renderizarConversaciones();
  },

  async cargarMensajes(conversacionId) {
    try {
      const response = await fetch(`/api/chat/mensajes/${conversacionId}`);
      const data = await response.json();
      
      if (data.mensajes) {
        this.state.mensajes[conversacionId] = data.mensajes;
        this.renderizarMensajes(data.mensajes);
        
        // Marcar como leído el último mensaje
        if (data.mensajes.length > 0) {
          const ultimoMensaje = data.mensajes[data.mensajes.length - 1];
          await this.marcarComoLeido(conversacionId, ultimoMensaje.id);
        }
      }
    } catch (error) {
      console.error('Error al cargar mensajes:', error);
    }
  },

  renderizarMensajes(mensajes) {
    this.dom.mensajesContenedor.innerHTML = mensajes.map(msg => {
      const esPropio = msg.es_propio ?? msg.es_mio ?? false;
      const usuario = msg.usuario || { nombre: 'Usuario', apellido: '' };
      const iniciales = `${(usuario.nombre?.[0] || 'U').toUpperCase()}${(usuario.apellido?.[0] || '').toUpperCase()}`;
      
      return `
        <div class="flex ${esPropio ? 'justify-end' : 'justify-start'} items-end gap-2">
          ${!esPropio ? `
            <div class="w-8 h-8 rounded-full bg-neutral-300 dark:bg-neutral-700 flex items-center justify-center text-xs font-bold flex-shrink-0">
              ${iniciales}
            </div>
          ` : ''}
          <div class="max-w-[70%]">
            ${!esPropio ? `<p class="text-xs text-neutral-500 dark:text-neutral-400 mb-1 ml-1">${usuario.nombre} ${usuario.apellido}</p>` : ''}
            <div class="rounded-2xl px-4 py-2 ${esPropio 
              ? 'bg-[var(--primary-color)] text-white rounded-br-sm' 
              : 'bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 rounded-bl-sm'}">
              <p class="text-sm break-words">${this.escaparHTML(msg.contenido)}</p>
              <p class="text-xs mt-1 ${esPropio ? 'text-white/70' : 'text-neutral-500 dark:text-neutral-400'}">
                ${this.formatearHora(msg.fecha_envio)}${msg.editado ? ' (editado)' : ''}
              </p>
            </div>
          </div>
        </div>
      `;
    }).join('');
    
    // Scroll al final
    this.scrollAlFinal();
  },

  async enviarMensaje() {
    const contenido = this.dom.inputMensaje.value.trim();
    
    if (!contenido || !this.state.conversacionActual) return;
    
    try {
      const response = await fetch('/api/chat/mensaje/enviar', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        body: JSON.stringify({
          conversacion_id: this.state.conversacionActual.id,
          contenido: contenido
        })
      });
      
      if (response.ok) {
        this.dom.inputMensaje.value = '';
        await this.cargarMensajes(this.state.conversacionActual.id);
        await this.cargarConversaciones(); // Actualizar lista
      }
    } catch (error) {
      console.error('Error al enviar mensaje:', error);
    }
  },

  async marcarComoLeido(conversacionId, mensajeId) {
    try {
      await fetch('/api/chat/mensaje/marcar-leido', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        body: JSON.stringify({
          conversacion_id: conversacionId,
          mensaje_id: mensajeId
        })
      });
    } catch (error) {
      console.error('Error al marcar como leído:', error);
    }
  },

  async abrirModalNuevoChat() {
    this.dom.modalNuevoChat.classList.remove('hidden');
    await this.cargarUsuarios();
  },

  cerrarModal() {
    this.dom.modalNuevoChat.classList.add('hidden');
    this.dom.buscarUsuario.value = '';
  },

  async cargarUsuarios() {
    try {
      const response = await fetch('/api/chat/usuarios');
      const data = await response.json();
      
      if (data.usuarios) {
        this.state.usuarios = data.usuarios;
        this.renderizarUsuarios();
      }
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
    }
  },

  renderizarUsuarios(filtro = '') {
    const usuarios = filtro 
      ? this.state.usuarios.filter(u => 
          u.nombre_completo.toLowerCase().includes(filtro.toLowerCase()) ||
          u.email.toLowerCase().includes(filtro.toLowerCase())
        )
      : this.state.usuarios;

    this.dom.listaUsuarios.innerHTML = usuarios.map(user => {
      const iniciales = (user.nombre[0] + (user.apellido[0] || '')).toUpperCase();
      
      return `
        <div class="usuario-item p-3 rounded-lg border border-gray-300 dark:border-neutral-700 hover:bg-neutral-100 dark:hover:bg-neutral-800 cursor-pointer transition-colors"
             data-id="${user.id}">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-[var(--primary-color)] flex items-center justify-center text-white font-bold">
              ${iniciales}
            </div>
            <div class="flex-1">
              <h4 class="font-semibold text-neutral-900 dark:text-neutral-100">${user.nombre_completo}</h4>
              <p class="text-xs text-neutral-500 dark:text-neutral-400">${user.email}</p>
              <p class="text-xs text-neutral-400 dark:text-neutral-500">${user.rol}</p>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Event listeners para los usuarios
    this.dom.listaUsuarios.querySelectorAll('.usuario-item').forEach(item => {
      item.addEventListener('click', () => {
        const id = item.dataset.id;
        this.iniciarConversacion(id);
      });
    });
  },

  async iniciarConversacion(usuarioId) {
    try {
      // Obtener el ID del usuario actual desde el DOM, variable global, o sesión
      // Ejemplo: desde un atributo data en el body
      const usuarioActualId = document.body.dataset.usuarioId;
      if (!usuarioActualId) {
        alert('No se pudo obtener el ID del usuario actual');
        return;
      }
      const response = await fetch('/api/chat/conversacion/crear', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content || ''
        },
        body: JSON.stringify({
          participantes: [usuarioActualId, usuarioId]
        })
      });
      const data = await response.json();
      if (data.conversacion) {
        this.cerrarModal();
        await this.cargarConversaciones();
        // Abrir la conversación nueva o existente
        const conv = this.state.conversaciones.find(c => c.id === data.conversacion.id);
        if (conv) {
          this.abrirConversacion(conv);
        }
      }
    } catch (error) {
      console.error('Error al iniciar conversación:', error);
    }
  },

  filtrarUsuarios(texto) {
    this.renderizarUsuarios(texto);
  },

  filtrarConversaciones(texto) {
    this.renderizarConversaciones(texto);
  },

  iniciarPolling() {
    // Actualizar conversaciones cada 5 segundos
    this.state.polling = setInterval(async () => {
      await this.cargarConversaciones();
      
      // Si hay una conversación activa, actualizar mensajes
      if (this.state.conversacionActual) {
        await this.cargarMensajes(this.state.conversacionActual.id);
      }
    }, 5000);
  },

  scrollAlFinal() {
    this.dom.mensajesContenedor.scrollTop = this.dom.mensajesContenedor.scrollHeight;
  },

  formatearFecha(fecha) {
    const date = new Date(fecha);
    const ahora = new Date();
    const diff = ahora - date;
    const dias = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (dias === 0) {
      return this.formatearHora(fecha);
    } else if (dias === 1) {
      return 'Ayer';
    } else if (dias < 7) {
      return `Hace ${dias} días`;
    } else {
      return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' });
    }
  },

  formatearHora(fecha) {
    return new Date(fecha).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  },

  truncarTexto(texto, max) {
    return texto.length > max ? texto.substring(0, max) + '...' : texto;
  },

  escaparHTML(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  Chat.init();
});
