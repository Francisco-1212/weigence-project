const notificationButton = document.getElementById('notification-button');
const notificationPanel = document.getElementById('notification-panel');
const closeNotificationPanel = document.getElementById('close-notification-panel');
const notificationBackdrop = document.getElementById('notification-backdrop');

// Constantes para los iconos de severidad de IA
const AI_SEVERITY_ICONS = {
  info: 'auto_awesome',
  warning: 'warning',
  error: 'error',
  success: 'check_circle'
};

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

// Clase para gestionar las recomendaciones de IA
// Clase para gestionar las recomendaciones de IA
class AIRecommendationManager {
  constructor() {
    this.container = document.getElementById('ai-recomendacion-header');
    this.textElement = document.getElementById('ai-recomendacion-text');
    this.iconElement = this.container?.querySelector('[data-ia-icon]');
    this.currentRecommendation = null;

    if (this.container && this.textElement) {
      this.loadOnce();
    }
  }

  async loadOnce() {
    try {
      const page =
        document.body.dataset.page ||
        window.location.pathname.replace("/", "") ||
        "dashboard";

      const response = await fetch(`/api/recomendacion/header?page=${page}`);
      if (!response.ok) throw new Error("Error al obtener recomendación");

      const payload = await response.json();
      if (!payload.ok || !payload.data) throw new Error("Respuesta inválida del servicio IA");

      this.displayRecommendation(payload.data);
    } catch (error) {
      console.error("Error al cargar recomendación IA:", error);
      this.displayError();
    }
  }

  displayRecommendation(data) {
    if (!data || typeof data !== "object") return;

    const icon =
      AI_SEVERITY_ICONS[data.severidad] || AI_SEVERITY_ICONS.info;
    if (this.iconElement) this.iconElement.textContent = icon;

    this.container.dataset.severity = data.severidad || "info";
    this.textElement.textContent =
      data.mensaje || "No hay recomendaciones disponibles";
    this.textElement.title =
      data.detalle || data.mensaje || "";

    this.textElement.classList.add("visible");
    this.currentRecommendation = data.mensaje;
  }

  displayError() {
    if (this.iconElement)
      this.iconElement.textContent = AI_SEVERITY_ICONS.error;
    this.container.dataset.severity = "error";
    this.textElement.textContent =
      "No se pudo obtener la recomendación";
    this.textElement.title = "Error al conectar con el servicio de IA";
  }
}


document.addEventListener("DOMContentLoaded", () => {
  new AIRecommendationManager();
});

