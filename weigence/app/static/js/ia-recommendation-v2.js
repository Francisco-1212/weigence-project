// Clase para manejar el estado del contexto de la IA
class IAContextManager {
  constructor() {
    this.pageContext = document.body.dataset.page || 'dashboard';
    this.contextData = {};
  }

  // Actualiza los datos del contexto
  updateContextData(data) {
    this.contextData = {...this.contextData, ...data};
  }

  // Obtiene los datos actuales para enviar a la API
  getCurrentContext() {
    return {
      ...this.contextData,
      page: this.pageContext,
      timestamp: new Date().toISOString()
    };
  }

  // Limpia los datos del contexto
  clearContext() {
    this.contextData = {};
  }
}

// Clase actualizada para gestionar recomendaciones con contexto
class IARecommendationManager {
  constructor(options = {}) {
    this.container = options.container;
    this.textElement = options.textElement;
    this.iconElement = options.iconElement;
    this.endpoint = options.endpoint || '/api/recomendacion';
    this.updateInterval = options.updateInterval || 60000;
    this.context = new IAContextManager();
    
    this.currentRecommendation = null;
    this.isUpdating = false;

    if (this.container && this.textElement) {
      this.initialize();
    }
  }

  initialize() {
    // Iniciar actualización periódica
    this.updateRecommendation();
    setInterval(() => this.updateRecommendation(), this.updateInterval);

    // Eventos de expansión/colapso
    if (this.container) {
      this.container.addEventListener('click', () => {
        this.container.classList.toggle('ia-expanded');
      });
    }
  }

  updateContextData(data) {
    this.context.updateContextData(data);
  }

  async updateRecommendation() {
    if (this.isUpdating) return;
    this.isUpdating = true;

    try {
      const contextData = this.context.getCurrentContext();
      const response = await fetch(
        `${this.endpoint}/${contextData.page}`, 
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(contextData)
        }
      );

      if (!response.ok) throw new Error('Error al obtener recomendación');
      
      const data = await response.json();
      this.displayRecommendation(data);
    } catch (error) {
      console.error('Error al actualizar recomendación:', error);
      this.displayError();
    } finally {
      this.isUpdating = false;
    }
  }

  displayRecommendation(data) {
    if (!data || typeof data !== 'object') return;

    // Actualizar icono por severidad
    if (this.iconElement) {
      const icon = AI_SEVERITY_ICONS[data.severidad] || AI_SEVERITY_ICONS.info;
      this.iconElement.textContent = icon;
    }

    // Actualizar severidad del panel
    this.container.dataset.severity = data.severidad || 'info';

    // Actualizar mensaje
    this.textElement.textContent = data.mensaje || 'No hay recomendaciones disponibles';
    this.textElement.title = data.detalle || data.mensaje || '';

    // Animar si el mensaje cambió
    if (this.currentRecommendation !== data.mensaje) {
      this.textElement.classList.add('ia-text-update');
      setTimeout(() => this.textElement.classList.remove('ia-text-update'), 500);
      this.currentRecommendation = data.mensaje;
    }
  }

  displayError() {
    if (this.iconElement) {
      this.iconElement.textContent = AI_SEVERITY_ICONS.error;
    }
    this.container.dataset.severity = 'error';
    this.textElement.textContent = 'No se pudo obtener la recomendación';
    this.textElement.title = 'Error al conectar con el servicio de IA';
  }
}

// Clase mejorada para recomendaciones detalladas
class IARecommendationCard extends IARecommendation {
  constructor(element) {
    super(element);
    this.manager = new IARecommendationManager({
      container: element,
      textElement: this.message,
      iconElement: this.icon,
      endpoint: element.dataset.iaEndpoint
    });
  }

  updateData(data) {
    this.manager.updateContextData(data);
  }
}

// Inicializar sistema de recomendaciones
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar tarjetas de recomendación
  const cards = document.querySelectorAll('[data-ia-card]');
  cards.forEach(el => new IARecommendationCard(el));

  // Inicializar recomendación del header
  const header = document.getElementById('ai-recomendacion-header');
  if (header) {
    new IARecommendationManager({
      container: header,
      textElement: document.getElementById('ai-recomendacion-text'),
      iconElement: header.querySelector('[data-ia-icon]')
    });
  }
});