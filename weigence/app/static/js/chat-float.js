// ===========================================================
// CHAT FLOTANTE - WEIGENCE
// ===========================================================

const ChatFloat = {
  state: {
    isOpen: false,
    usuarios: [],
    vista: 'usuarios', // 'usuarios' | 'chat'
    conversacionActual: null,
    mensajes: [],
    usuarioActual: null
  },

  init() {
    console.log('🔄 Iniciando chat flotante...');
    this.cacheDOM();
    this.bindEvents();
    this.actualizarBadge();
    setInterval(() => this.actualizarBadge(), 30000);
    console.info("✅ Chat flotante inicializado correctamente");
  },

  cacheDOM() {
    this.dom = {
      btn: document.getElementById('chat-float-btn'),
      panel: document.getElementById('chat-mini-panel'),
      closeBtn: document.getElementById('close-mini-chat'),
      backBtn: document.getElementById('back-to-users'),
      icon: document.getElementById('chat-icon'),
      usuarios: document.getElementById('mini-chat-usuarios'),
      buscar: document.getElementById('buscar-usuario-mini'),
      badge: document.getElementById('chat-float-badge'),
      chatContainer: document.getElementById('mini-chat-container'),
      chatMessages: document.getElementById('mini-chat-messages'),
      chatInput: document.getElementById('mini-chat-input'),
      sendBtn: document.getElementById('mini-chat-send'),
      headerTitle: document.getElementById('mini-chat-title')
    };
    
    console.log('🔍 Elementos encontrados:', {
      btn: !!this.dom.btn,
      panel: !!this.dom.panel,
      closeBtn: !!this.dom.closeBtn,
      backBtn: !!this.dom.backBtn,
      chatContainer: !!this.dom.chatContainer
    });
  },

  bindEvents() {
    if (this.dom.btn) {
      console.log('🔘 Event listener agregado al botón');
      this.dom.btn.addEventListener('click', () => {
        console.log('🖱️ Click en botón flotante');
        this.togglePanel();
      });
    }
    
    if (this.dom.closeBtn) {
      this.dom.closeBtn.addEventListener('click', () => {
        console.log('🖱️ Click en cerrar');
        this.closePanel();
      });
    }

    if (this.dom.backBtn) {
      this.dom.backBtn.addEventListener('click', () => {
        console.log('🖱️ Click en volver');
        this.volverAUsuarios();
      });
    }
    
    if (this.dom.buscar) {
      this.dom.buscar.addEventListener('input', (e) => this.filtrarUsuarios(e.target.value));
    }

    if (this.dom.sendBtn) {
      this.dom.sendBtn.addEventListener('click', () => this.enviarMensaje());
    }

    if (this.dom.chatInput) {
      this.dom.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.enviarMensaje();
        }
      });
    }
  },

  togglePanel() {
    console.log('🔄 Toggle panel - Estado actual:', this.state.isOpen);
    this.state.isOpen = !this.state.isOpen;
    
    if (this.state.isOpen) {
      console.log('📂 Abriendo panel');
      this.dom.panel.classList.remove('hidden');
      this.dom.icon.textContent = 'close';
      this.volverAUsuarios();
    } else {
      console.log('📁 Cerrando panel');
      this.closePanel();
    }
  },

  closePanel() {
    console.log('❌ Cerrando panel');
    this.state.isOpen = false;
    this.dom.panel.classList.add('hidden');
    this.dom.icon.textContent = 'chat';
    this.state.vista = 'usuarios';
    this.state.conversacionActual = null;
  },

  volverAUsuarios() {
    console.log('⬅️ Volviendo a lista de usuarios');
    this.state.vista = 'usuarios';
    this.state.conversacionActual = null;
    this.mostrarVista();
    if (this.state.usuarios.length === 0) {
      this.cargarUsuarios();
    }
  },

  mostrarVista() {
    const usuariosContainer = document.getElementById('mini-usuarios-container');
    const chatContainer = this.dom.chatContainer;
    const backBtn = this.dom.backBtn;

    if (this.state.vista === 'usuarios') {
      usuariosContainer?.classList.remove('hidden');
      chatContainer?.classList.add('hidden');
      backBtn?.classList.add('hidden');
    } else {
      usuariosContainer?.classList.add('hidden');
      chatContainer?.classList.remove('hidden');
      backBtn?.classList.remove('hidden');
    }
  },

  async cargarUsuarios() {
    try {
      this.mostrarEstado('loading');

      const response = await fetch('/api/chat/usuarios');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      
      console.log('📥 Usuarios cargados:', data);
      
      if (data.usuarios && Array.isArray(data.usuarios) && data.usuarios.length > 0) {
        this.state.usuarios = data.usuarios;
        this.renderizarUsuarios(this.state.usuarios);
      } else {
        this.mostrarEstado('empty');
      }
    } catch (error) {
      console.error('❌ Error al cargar usuarios:', error);
      this.mostrarEstado('error');
    }
  },

  mostrarEstado(tipo) {
    const estados = {
      loading: {
        icon: 'sync',
        texto: 'Cargando usuarios...'
      },
      empty: {
        icon: 'person_off',
        texto: 'No hay usuarios disponibles'
      },
      error: {
        icon: 'error',
        texto: 'Error al cargar usuarios'
      }
    };

    const estado = estados[tipo];
    
    this.dom.usuarios.innerHTML = `
      <div class="flex items-center justify-center h-full text-neutral-500 dark:text-neutral-400">
        <div class="text-center">
          <span class="material-symbols-outlined text-4xl mb-2 opacity-50">${estado.icon}</span>
          <p class="text-sm">${estado.texto}</p>
        </div>
      </div>
    `;
  },

  renderizarUsuarios(usuarios) {
    if (!usuarios || usuarios.length === 0) {
      this.mostrarEstado('empty');
      return;
    }

    const avatarClasses = [
      'avatar-blue', 'avatar-green', 'avatar-purple', 'avatar-pink', 
      'avatar-yellow', 'avatar-indigo', 'avatar-red', 'avatar-teal',
      'avatar-cyan', 'avatar-orange'
    ];

    this.dom.usuarios.innerHTML = usuarios.map((user, index) => {
      const nombre = user.nombre || '';
      const iniciales = nombre.substring(0, 2).toUpperCase() || '??';
      const avatarClass = avatarClasses[index % avatarClasses.length];
      const nombreCompleto = user.nombre_completo || nombre || 'Usuario';
      const rol = user.rol || 'Sin rol';
      const userId = user.id || user.rut_usuario;
      
      return `
        <div class="usuario-mini-item" 
             data-user-id="${userId}"
             data-user-name="${this.escaparHTML(nombreCompleto)}">
          <div class="flex items-center gap-3">
            <div class="relative">
              <div class="w-12 h-12 rounded-full ${avatarClass} flex items-center justify-center text-white font-bold flex-shrink-0 shadow-md">
                ${iniciales}
              </div>
              <span class="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 border-2 border-white dark:border-neutral-900 rounded-full"></span>
            </div>
            <div class="flex-1 min-w-0">
              <h4 class="font-semibold text-neutral-900 dark:text-neutral-100 text-sm truncate">${this.escaparHTML(nombreCompleto)}</h4>
              <p class="text-xs text-neutral-500 dark:text-neutral-400 truncate">${this.escaparHTML(rol)}</p>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Event listeners
    this.dom.usuarios.querySelectorAll('.usuario-mini-item').forEach(item => {
      item.addEventListener('click', () => {
        const userId = item.dataset.userId;
        const userName = item.dataset.userName;
        this.iniciarChat(userId, userName);
      });
    });
  },

  filtrarUsuarios(texto) {
    if (!texto.trim()) {
      this.renderizarUsuarios(this.state.usuarios);
      return;
    }

    const textoLower = texto.toLowerCase();
    const usuariosFiltrados = this.state.usuarios.filter(u => {
      const nombreCompleto = (u.nombre_completo || u.nombre || '').toLowerCase();
      const email = (u.email || u.correo || '').toLowerCase();
      const rol = (u.rol || '').toLowerCase();
      
      return nombreCompleto.includes(textoLower) || 
             email.includes(textoLower) || 
             rol.includes(textoLower);
    });

    this.renderizarUsuarios(usuariosFiltrados);
  },

  async iniciarChat(userId, userName) {
    try {
      console.log('💬 Iniciando chat con:', userId, userName);
      // Obtener el ID del usuario actual desde el body
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
          participantes: [usuarioActualId, userId]
        })
      });
      const data = await response.json();
      console.log('📦 Respuesta del servidor:', data);
      if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
      }
      if (data.conversacion && data.conversacion.id) {
        const usuario = this.state.usuarios.find(u => u.id === userId);
        this.abrirChat(data.conversacion.id, usuario || { nombre: userName, id: userId });
      } else if (data.conversacion_id) {
        const usuario = this.state.usuarios.find(u => u.id === userId);
        this.abrirChat(data.conversacion_id, usuario || { nombre: userName, id: userId });
      } else {
        throw new Error('No se recibió ID de conversación');
      }
    } catch (error) {
      console.error('❌ Error al crear conversación:', error);
      alert('No se pudo iniciar el chat: ' + error.message);
    }
  },

  async abrirChat(conversacionId, usuario) {
    console.log('📖 Abriendo chat:', conversacionId);
    this.state.vista = 'chat';
    this.state.conversacionActual = conversacionId;
    this.state.usuarioActual = usuario;
    
    if (this.dom.headerTitle) {
      this.dom.headerTitle.textContent = usuario?.nombre || 'Chat';
    }
    
    this.mostrarVista();
    await this.cargarMensajes();
    this.iniciarActualizacionAutomatica();
  },

  async cargarMensajes() {
    try {
      const response = await fetch(`/api/chat/mensajes/${this.state.conversacionActual}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      this.state.mensajes = data.mensajes || [];
      this.renderizarMensajes();
      
    } catch (error) {
      console.error('❌ Error al cargar mensajes:', error);
      if (this.dom.chatMessages) {
        this.dom.chatMessages.innerHTML = `
          <div class="flex items-center justify-center h-full text-neutral-500 dark:text-neutral-400">
            <p class="text-sm">Error al cargar mensajes</p>
          </div>
        `;
      }
    }
  },

  renderizarMensajes() {
    if (!this.dom.chatMessages) return;
    
    this.dom.chatMessages.innerHTML = this.state.mensajes.map(m => `
      <div class="flex ${m.es_mio ? 'justify-end' : 'justify-start'} mb-3">
        <div class="max-w-[70%] ${m.es_mio ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900'} rounded-lg px-4 py-2">
          <p class="text-sm">${this.escaparHTML(m.contenido)}</p>
          <span class="text-xs opacity-75 mt-1 block">
            ${this.formatearFecha(m.fecha_envio)}
          </span>
        </div>
      </div>
    `).join('');
    
    this.dom.chatMessages.scrollTop = this.dom.chatMessages.scrollHeight;
  },

  async enviarMensaje() {
    const mensaje = this.dom.chatInput?.value.trim();
    if (!mensaje || !this.state.conversacionActual) return;
    
    try {
      const response = await fetch('/api/chat/mensaje/enviar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversacion_id: this.state.conversacionActual,
          contenido: mensaje
        })
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      this.dom.chatInput.value = '';
      await this.cargarMensajes();
      
    } catch (error) {
      console.error('❌ Error al enviar mensaje:', error);
      alert('No se pudo enviar el mensaje');
    }
  },

  iniciarActualizacionAutomatica() {
    if (this.intervaloActualizacion) {
      clearInterval(this.intervaloActualizacion);
    }
    
    this.intervaloActualizacion = setInterval(() => {
      if (this.state.vista === 'chat' && this.state.conversacionActual) {
        this.cargarMensajes();
      }
    }, 3000);
  },

  escaparHTML(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
  },

  formatearFecha(fecha) {
    const d = new Date(fecha);
    const hoy = new Date();
    const esHoy = d.toDateString() === hoy.toDateString();
    
    if (esHoy) {
      return d.toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString('es-CL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  },

  async actualizarBadge() {
    try {
      const response = await fetch('/api/chat/conversaciones');
      const data = await response.json();
      
      if (data.conversaciones) {
        const totalNoLeidos = data.conversaciones.reduce((sum, conv) => {
          return sum + (conv.mensajes_no_leidos || 0);
        }, 0);
        
        if (totalNoLeidos > 0) {
          this.dom.badge.classList.remove('hidden');
          this.dom.badge.textContent = totalNoLeidos > 99 ? '99+' : totalNoLeidos;
        } else {
          this.dom.badge.classList.add('hidden');
        }
      }
    } catch (error) {
      console.error('❌ Error al actualizar badge:', error);
    }
  },

  escaparHTML(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
  }
};

// Inicializar
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => ChatFloat.init());
} else {
  ChatFloat.init();
}
