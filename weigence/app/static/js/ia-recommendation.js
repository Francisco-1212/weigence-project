// IA Recommendation Component Handler
class IARecommendation {
  constructor(element) {
    this.element = element;
    this.title = element.querySelector('[data-ia-title]');
    this.message = element.querySelector('[data-ia-message]');
    this.solution = element.querySelector('[data-ia-solution]');
    this.severity = element.querySelector('[data-ia-severity]');
    this.icon = element.querySelector('[data-ia-icon]');
    
    this.init();
  }

  init() {
    // Make component visible with animation
    setTimeout(() => {
      this.element.classList.add('is-visible');
    }, 100);

    // Listen for content updates
    this.setupUpdateListeners();
  }

  setupUpdateListeners() {
    // Watch for content changes and trigger animations
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          const target = mutation.target;
          this.animateContentUpdate(target);
        }
      });
    });

    // Observe content elements
    [this.title, this.message, this.solution].forEach(el => {
      if (el) {
        observer.observe(el, { childList: true });
      }
    });
  }

  animateContentUpdate(element) {
    element.classList.add('updating');
    element.addEventListener('animationend', () => {
      element.classList.remove('updating');
    }, { once: true });
  }

  updateSeverity(severity) {
    // Remove existing severity classes
    ['info', 'warning', 'critical'].forEach(s => {
      this.element.classList.remove(`ia-recommendation--${s}`);
    });
    
    // Add new severity class
    this.element.classList.add(`ia-recommendation--${severity}`);
    
    // Update data attribute
    this.element.dataset.severity = severity;
    
    // Update severity text if element exists
    if (this.severity) {
      this.severity.textContent = this.getSeverityText(severity);
    }
  }
  
  getSeverityText(severity) {
    const texts = {
      'info': 'Análisis operativo',
      'warning': 'Atención requerida',
      'critical': 'Acción urgente'
    };
    return texts[severity] || texts.info;
  }
}

// Initialize all IA recommendation components
document.addEventListener('DOMContentLoaded', () => {
  const recommendations = document.querySelectorAll('[data-ia-card]');
  recommendations.forEach(el => new IARecommendation(el));
});