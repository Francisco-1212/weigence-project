const notificationButton = document.getElementById('notification-button');
const notificationPanel = document.getElementById('notification-panel');
const closeNotificationPanel = document.getElementById('close-notification-panel');
const notificationBackdrop = document.getElementById('notification-backdrop');

notificationButton.addEventListener('click', () => {
  notificationPanel.classList.remove('translate-x-full');
  notificationBackdrop.classList.remove('opacity-0','pointer-events-none');
});

closeNotificationPanel.addEventListener('click', () => {
  notificationPanel.classList.add('translate-x-full');
  notificationBackdrop.classList.add('opacity-0','pointer-events-none');
});

notificationBackdrop.addEventListener('click', () => {
  notificationPanel.classList.add('translate-x-full');
  notificationBackdrop.classList.add('opacity-0','pointer-events-none');
});

// Delegación de eventos para toggle de detalle y botón descartar
notificationPanel.addEventListener('click', e => {
  // Evento descartar: si se hizo clic en el botón descartar
  if (e.target.classList.contains('notif-discard')) {
    e.stopPropagation();
    const item = e.target.closest('.notif-item');
    if (item) item.remove();
    return;
  }

  // Evento toggle detalle: si hizo clic en alguna notificación
  const item = e.target.closest('.notif-item');
  if (!item) return;

  const detalle = item.querySelector('.notif-detalle');
  if (detalle) detalle.classList.toggle('hidden');
});

// Clase para gestionar las recomendaciones de IA con rotación
class AIRecommendationManager {
  constructor() {
    this.container = document.getElementById('ai-recomendacion-header');
    this.textElement = document.getElementById('ai-recomendacion-text');
    this.iconElement = this.container?.querySelector('[data-ia-icon]');
    this.messages = [];
    this.currentIndex = 0;
    this.autoRotateInterval = null;
    this.navButtons = null;

    if (this.container && this.textElement) {
      this.setupNavigationButtons();
      this.loadOnce();
    }
  }

  setupNavigationButtons() {
    // Crear botones de navegación sutiles
    const navContainer = document.createElement('div');
    navContainer.className = 'ia-header-nav';
    navContainer.innerHTML = `
      <button class="ia-nav-btn ia-nav-prev" aria-label="Mensaje anterior" title="Anterior">‹</button>
      <button class="ia-nav-btn ia-nav-next" aria-label="Mensaje siguiente" title="Siguiente">›</button>
    `;
    
    this.container.appendChild(navContainer);
    this.navButtons = navContainer;
    
    // Event listeners
    navContainer.querySelector('.ia-nav-prev').addEventListener('click', (e) => {
      e.stopPropagation();
      this.showPrevious();
      this.resetAutoRotate();
    });
    
    navContainer.querySelector('.ia-nav-next').addEventListener('click', (e) => {
      e.stopPropagation();
      this.showNext();
      this.resetAutoRotate();
    });
  }

  async loadOnce() {
    try {
      this.showLoading();

      const page =
        document.body.dataset.page ||
        window.location.pathname.replace("/", "") ||
        "dashboard";

      const response = await fetch(`/api/recomendacion/header?page=${page}`);
      if (!response.ok) throw new Error("Error al obtener recomendación");

      const payload = await response.json();
      if (!payload.ok || !payload.data) throw new Error("Respuesta inválida del servicio IA");

      this.initializeMessages(payload.data);
    } catch (error) {
      console.error("Error al cargar recomendación IA:", error);
      this.displayError();
    }
  }

  initializeMessages(data) {
    // Extraer array de mensajes del payload
    this.messages = data.mensajes || [{
      mensaje: data.mensaje || "No hay recomendaciones disponibles",
      severidad: data.severidad || "info",
      detalle: data.detalle
    }];

    console.log('[IA Header] Mensajes cargados:', this.messages.length, this.messages);

    this.currentIndex = 0;
    this.displayCurrentMessage();
    
    // Mostrar/ocultar navegación según cantidad de mensajes
    if (this.messages.length > 1) {
      this.navButtons.style.display = 'flex';
      this.startAutoRotate();
      console.log('[IA Header] Navegación activada - Auto-rotación cada 15s');
    } else {
      this.navButtons.style.display = 'none';
      console.log('[IA Header] Solo 1 mensaje - Navegación oculta');
    }
  }

  displayCurrentMessage() {
    if (!this.messages.length) return;

    this.iconElement?.classList.remove('animate-spin');

    const current = this.messages[this.currentIndex];
    const icon = AI_SEVERITY_ICONS[current.severidad] || AI_SEVERITY_ICONS.info;
    
    if (this.iconElement) this.iconElement.textContent = icon;
    this.container.dataset.severity = current.severidad || "info";
    this.textElement.textContent = current.mensaje;
    this.textElement.title = current.detalle || current.mensaje;
    this.textElement.classList.add("visible");
  }

  showNext() {
    this.currentIndex = (this.currentIndex + 1) % this.messages.length;
    this.displayCurrentMessage();
  }

  showPrevious() {
    this.currentIndex = (this.currentIndex - 1 + this.messages.length) % this.messages.length;
    this.displayCurrentMessage();
  }

  startAutoRotate() {
    // Rotación automática cada 15 segundos
    this.autoRotateInterval = setInterval(() => {
      this.showNext();
    }, 15000);
  }

  resetAutoRotate() {
    // Reiniciar timer cuando usuario navega manualmente
    if (this.autoRotateInterval) {
      clearInterval(this.autoRotateInterval);
      this.startAutoRotate();
    }
  }

  showLoading() {
    if (this.iconElement) this.iconElement.textContent = 'sync';
    this.container.dataset.severity = 'info';
    this.textElement.textContent = 'Analizando datos...';
    this.iconElement?.classList.add('animate-spin');
    if (this.navButtons) this.navButtons.style.display = 'none';
  }

  displayError() {
    this.iconElement?.classList.remove('animate-spin');
    
    if (this.iconElement)
      this.iconElement.textContent = AI_SEVERITY_ICONS.error;
    this.container.dataset.severity = "error";
    this.textElement.textContent = "No se pudo obtener la recomendación";
    this.textElement.title = "Error al conectar con el servicio de IA";
    if (this.navButtons) this.navButtons.style.display = 'none';
  }
}


document.addEventListener("DOMContentLoaded", () => {
  new AIRecommendationManager();

  // Funcionalidad del botón "Ver Tabla de Productos" en Inventario
  const btnVerTablaProductos = document.getElementById('btn-ver-tabla-productos');
  if (btnVerTablaProductos) {
    btnVerTablaProductos.addEventListener('click', () => {
      const tablaProductos = document.getElementById('tabla-productos');
      if (tablaProductos) {
        tablaProductos.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }
    });
  }

  // Funcionalidad del botón "Exportar" en Alertas (header)
  const btnExportarAlertasHeader = document.getElementById('btn-exportar-alertas-header');
  if (btnExportarAlertasHeader) {
    btnExportarAlertasHeader.addEventListener('click', () => {
      // Buscar el botón original de exportar en la página de alertas si existe
      const btnExportarAlertas = document.getElementById('btn-exportar-alertas');
      if (btnExportarAlertas) {
        btnExportarAlertas.click();
      } else {
        // Si no existe el botón original, ejecutar la función directamente
        if (typeof exportarAlertas === 'function') {
          exportarAlertas();
        }
      }
    });
  }

  // Nota: El botón "Registrar un movimiento" del header es manejado directamente
  // por movimiento_inventario.js, no necesita lógica adicional aquí
});

