(function () {
  const auditoriaCard = document.getElementById('ai-recomendacion-auditoria');
  if (!auditoriaCard) return;

  const cards = [auditoriaCard];

  const severityLabels = {
    info: 'Nivel informativo',
    warning: 'Atención requerida',
    critical: 'Riesgo crítico',
  };

  const severityIcons = {
    info: 'auto_awesome',
    warning: 'warning',
    critical: 'report',
  };

  const DEFAULT_DATA = {
    titulo: 'Recomendación automática',
    mensaje: 'Sin detalles disponibles.',
    solucion: 'Sin acciones sugeridas.',
    severidad: 'info',
  };

  const AUTO_REFRESH_INTERVAL = 60_000;

  const state = { status: 'idle', data: null, requestId: 0, timer: null };

  const mappedCards = cards.map((card) => ({
    card,
    icon: card.querySelector('[data-ia-icon]'),
    title: card.querySelector('[data-ia-title]'),
    severity: card.querySelector('[data-ia-severity]'),
    message: card.querySelector('[data-ia-message]'),
    solution: card.querySelector('[data-ia-solution]'),
    mlBadge: card.querySelector('[data-ml-badge]'),
    // Elementos de módulo
    moduleContainer: card.querySelector('[data-ia-module]'),
    moduleIcon: card.querySelector('[data-module-icon]'),
    moduleName: card.querySelector('[data-module-name]'),
    // Elementos de severidad
    severityDetail: card.querySelector('[data-severity-detail]'),
    severityIndicator: card.querySelector('[data-severity-indicator]'),
    severityBar: card.querySelector('[data-severity-bar]'),
    severityText: card.querySelector('[data-severity-text]'),
    // Navegación entre hallazgos
    mlNavigation: card.querySelector('[data-ml-navigation]'),
    navPrev: card.querySelector('[data-nav-prev]'),
    navNext: card.querySelector('[data-nav-next]'),
    navCounter: card.querySelector('[data-nav-counter]'),
    navCurrent: card.querySelector('[data-nav-current]'),
    navTotal: card.querySelector('[data-nav-total]'),
    // Estado de navegación
    mlHallazgos: [],
    currentHallazgoIndex: 0,
  }));

  function obtenerContexto() {
    const path = window.location.pathname.split('/').filter(Boolean);
    return path[0] || 'auditoria';
  }

  function asegurarTexto(valor, fallback) {
    return typeof valor === 'string' && valor.trim() ? valor.trim() : fallback;
  }

  function asegurarSeveridad(valor) {
    const safe = asegurarTexto(valor, 'info').toLowerCase();
    return ['info', 'warning', 'critical'].includes(safe) ? safe : 'info';
  }

  function normalizar(raw) {
    const origen = raw && typeof raw === 'object' ? raw : {};
    return {
      titulo: asegurarTexto(origen.titulo, DEFAULT_DATA.titulo),
      mensaje: asegurarTexto(origen.mensaje, DEFAULT_DATA.mensaje),
      solucion: asegurarTexto(origen.solucion, DEFAULT_DATA.solucion),
      severidad: asegurarSeveridad(origen.severidad),
      // Datos ML
      ml_anomaly_detected: Boolean(origen.ml_anomaly_detected),
      ml_anomaly_score: Number(origen.ml_anomaly_score || 0),
      ml_severity: asegurarTexto(origen.ml_severity, 'low'),
      situacion_actual: asegurarTexto(origen.situacion_actual, ''),
      ml_insights_cards: Array.isArray(origen.ml_insights_cards) ? origen.ml_insights_cards : [],
    };
  }

  function setStatus(status) {
    state.status = status;
    mappedCards.forEach(({ card }) => {
      card.dataset.iaStatus = status;
      card.setAttribute('aria-busy', status === 'loading' ? 'true' : 'false');
    });
  }

  function animateContent(elements) {
    ['title', 'message', 'solution'].forEach((key) => {
      const el = elements[key];
      if (!el) return;
      el.classList.remove('updating');
      // fuerza reflow para reiniciar la animación
      void el.offsetWidth;
      el.classList.add('updating');
    });
  }

  function aplicarCard(elements, data) {
    const { titulo, mensaje, solucion, severidad, ml_anomaly_detected, ml_severity, situacion_actual, ml_insights_cards } = data;

    elements.card.dataset.severity = severidad;

    if (elements.icon) elements.icon.textContent = severityIcons[severidad];
    if (elements.title) elements.title.textContent = titulo;
    if (elements.severity) elements.severity.textContent = severityLabels[severidad];
    if (elements.message) elements.message.textContent = mensaje;
    if (elements.solution) elements.solution.textContent = solucion;

    // Mostrar badge ML si detectó anomalía
    if (elements.mlBadge) {
      elements.mlBadge.style.display = ml_anomaly_detected ? 'inline-block' : 'none';
    }

    // Si hay hallazgos ML, configurar navegación
    if (ml_anomaly_detected && ml_insights_cards.length > 0) {
      elements.mlHallazgos = ml_insights_cards;
      elements.currentHallazgoIndex = 0;
      mostrarHallazgo(elements, 0);
      configurarNavegacion(elements);
    } else {
      // Ocultar elementos ML si no hay hallazgos
      if (elements.moduleContainer) elements.moduleContainer.style.display = 'none';
      if (elements.severityDetail) elements.severityDetail.style.display = 'none';
      if (elements.mlNavigation) elements.mlNavigation.style.display = 'none';
    }

    animateContent(elements);
    elements.card.classList.add('is-visible');
  }

  // Iconos de módulos
  const moduleIcons = {
    dashboard: 'dashboard',
    inventario: 'inventory_2',
    movimientos: 'swap_horiz',
    ventas: 'point_of_sale',
    alertas: 'notifications_active',
    auditoria: 'shield',
  };

  // Función para mostrar un hallazgo específico
  function mostrarHallazgo(elements, index) {
    const hallazgo = elements.mlHallazgos[index];
    if (!hallazgo) return;

    // Actualizar título y descripción
    if (elements.title) elements.title.textContent = hallazgo.titulo || hallazgo.title || 'Hallazgo detectado';
    if (elements.message) elements.message.textContent = hallazgo.descripcion || hallazgo.description || 'Sin detalles disponibles';

    // Mostrar módulo afectado
    if (elements.moduleContainer) {
      const modulo = hallazgo.modulo || 'general';
      elements.moduleContainer.style.display = 'flex';
      if (elements.moduleIcon) elements.moduleIcon.textContent = moduleIcons[modulo] || 'dashboard';
      if (elements.moduleName) {
        const moduloLabels = {
          dashboard: 'Dashboard',
          inventario: 'Inventario',
          movimientos: 'Movimientos',
          ventas: 'Ventas',
          alertas: 'Alertas',
          auditoria: 'Auditoría'
        };
        elements.moduleName.textContent = moduloLabels[modulo] || modulo;
      }
    }

    // Mostrar severidad
    if (elements.severityDetail && hallazgo.ml_severity) {
      elements.severityDetail.style.display = 'block';
      const severityLevel = hallazgo.ml_severity.toLowerCase();
      const severityLabels = { low: 'Baja', medium: 'Media', high: 'Alta', critical: 'Crítica' };
      const severityColors = { low: '#10b981', medium: '#f59e0b', high: '#f97316', critical: '#ef4444' };
      
      if (elements.severityText) elements.severityText.textContent = severityLabels[severityLevel] || 'Media';
      if (elements.severityBar) {
        elements.severityBar.style.backgroundColor = severityColors[severityLevel] || '#f59e0b';
        const widths = { low: '25%', medium: '50%', high: '75%', critical: '100%' };
        elements.severityBar.style.width = widths[severityLevel] || '50%';
      }
    }

    // Plan de acción (si existe)
    if (elements.solution && hallazgo.plan_accion) {
      elements.solution.textContent = hallazgo.plan_accion;
    }

    // Actualizar contador
    if (elements.navCurrent) elements.navCurrent.textContent = index + 1;
    if (elements.navTotal) elements.navTotal.textContent = elements.mlHallazgos.length;

    // Actualizar estado de botones
    if (elements.navPrev) elements.navPrev.disabled = index === 0;
    if (elements.navNext) elements.navNext.disabled = index === elements.mlHallazgos.length - 1;

    elements.currentHallazgoIndex = index;
  }

  // Configurar navegación entre hallazgos
  function configurarNavegacion(elements) {
    if (!elements.mlNavigation || elements.mlHallazgos.length === 0) return;

    // Mostrar navegación solo si hay más de 1 hallazgo
    elements.mlNavigation.style.display = elements.mlHallazgos.length > 1 ? 'flex' : 'none';

    // Botón anterior
    if (elements.navPrev) {
      elements.navPrev.onclick = () => {
        const newIndex = Math.max(0, elements.currentHallazgoIndex - 1);
        mostrarHallazgo(elements, newIndex);
      };
    }

    // Botón siguiente
    if (elements.navNext) {
      elements.navNext.onclick = () => {
        const newIndex = Math.min(elements.mlHallazgos.length - 1, elements.currentHallazgoIndex + 1);
        mostrarHallazgo(elements, newIndex);
      };
    }

    // Navegación con teclado
    elements.card.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' && elements.currentHallazgoIndex > 0) {
        e.preventDefault();
        mostrarHallazgo(elements, elements.currentHallazgoIndex - 1);
      } else if (e.key === 'ArrowRight' && elements.currentHallazgoIndex < elements.mlHallazgos.length - 1) {
        e.preventDefault();
        mostrarHallazgo(elements, elements.currentHallazgoIndex + 1);
      }
    });
  }

  function setupCarouselmodulo(elements, cards) {
    if (!elements.mlTrack) return;

    // Limpiar carrusel anterior
    elements.mlTrack.innerHTML = '';
    if (elements.mlDots) elements.mlDots.innerHTML = '';

    // Referencias al header dinámico
    const headerTitle = elements.card.querySelector('[data-ml-carousel-title]');
    const headerSubtitle = elements.card.querySelector('[data-ml-carousel-subtitle]');
    const counterEl = elements.card.querySelector('[data-ml-counter]');

    // Crear tarjetas (6 módulos: dashboard, inventario, movimientos, ventas, alertas, auditoria)
    cards.forEach((card, index) => {
      const cardEl = document.createElement('div');
      cardEl.className = 'ml-carousel__card';
      cardEl.dataset.cardTitle = card.titulo; // Guardar título para header dinámico
      cardEl.dataset.cardModulo = card.modulo || 'general'; // Guardar módulo
      
      // Estructura de tarjeta: emoji + título + descripción (sin acciones anidadas)
      cardEl.innerHTML = `
        <div class="ml-carousel__card-header">
          <span class="ml-carousel__icon">${card.icono || card.emoji || '🔍'}</span>
          <h4 class="ml-carousel__title">${card.titulo || card.title || 'Hallazgo'}</h4>
        </div>
        <p class="ml-carousel__description">${card.descripcion || card.description || 'Sin detalles'}</p>
      `;
      elements.mlTrack.appendChild(cardEl);

      // Crear dot
      if (elements.mlDots) {
        const dot = document.createElement('button');
        dot.className = `ml-carousel__dot ${index === 0 ? 'ml-carousel__dot--active' : ''}`;
        dot.setAttribute('aria-label', `Ir a tarjeta ${index + 1}`);
        dot.addEventListener('click', () => goToSlide(elements, index));
        elements.mlDots.appendChild(dot);
      }
    });

    // Inicializar estado
    elements.carouselState.currentIndex = 0;
    elements.carouselState.totalCards = cards.length;

    // Setup navegación con flechas
    if (elements.mlPrev) {
      // Limpiar listeners anteriores clonando el elemento
      const newPrev = elements.mlPrev.cloneNode(true);
      elements.mlPrev.replaceWith(newPrev);
      elements.mlPrev = newPrev;
      
      newPrev.addEventListener('click', () => {
        goToSlide(elements, elements.carouselState.currentIndex - 1);
      });
    }

    if (elements.mlNext) {
      // Limpiar listeners anteriores clonando el elemento
      const newNext = elements.mlNext.cloneNode(true);
      elements.mlNext.replaceWith(newNext);
      elements.mlNext = newNext;
      
      newNext.addEventListener('click', () => {
        goToSlide(elements, elements.carouselState.currentIndex + 1);
      });
    }

    // Navegación con teclado (Arrow Left/Right)
    const carouselContainer = elements.mlInsights;
    if (carouselContainer) {
      carouselContainer.setAttribute('tabindex', '0');
      carouselContainer.addEventListener('keydown', (e) => {
        const { currentIndex, totalCards } = elements.carouselState;
        
        if (e.key === 'ArrowLeft' && currentIndex > 0) {
          e.preventDefault();
          goToSlide(elements, currentIndex - 1);
        } else if (e.key === 'ArrowRight' && currentIndex < totalCards - 1) {
          e.preventDefault();
          goToSlide(elements, currentIndex + 1);
        }
      });
    }

    updateCarousel(elements);
  }

  function goToSlide(elements, index) {
    const { totalCards } = elements.carouselState;
    if (index < 0 || index >= totalCards) return;

    elements.carouselState.currentIndex = index;
    updateCarousel(elements);
  }

  function updateCarousel(elements) {
    const { currentIndex, totalCards } = elements.carouselState;

    // Mover track
    if (elements.mlTrack) {
      elements.mlTrack.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    // Actualizar header dinámico
    const headerTitle = elements.card.querySelector('[data-ml-carousel-title]');
    const headerSubtitle = elements.card.querySelector('[data-ml-carousel-subtitle]');
    const counterEl = elements.card.querySelector('[data-ml-counter]');
    const currentCard = elements.mlTrack?.children[currentIndex];

    if (headerTitle && currentCard) {
      const cardTitle = currentCard.dataset.cardTitle || '¿Qué detectó el sistema?';
      headerTitle.textContent = cardTitle;
      
      // Actualizar subtítulo según contexto
      if (totalCards > 1) {
        headerSubtitle.textContent = `${currentIndex + 1} de ${totalCards} hallazgos`;
      } else {
        headerSubtitle.textContent = 'Detección automática';
      }
    }

    // Actualizar contador
    if (counterEl) {
      counterEl.textContent = `${currentIndex + 1} / ${totalCards}`;
    }

    // Actualizar dots
    if (elements.mlDots) {
      const dots = elements.mlDots.querySelectorAll('.ml-carousel__dot');
      dots.forEach((dot, i) => {
        dot.classList.toggle('ml-carousel__dot--active', i === currentIndex);
      });
    }

    // Actualizar botones de navegación
    if (elements.mlPrev) {
      elements.mlPrev.disabled = currentIndex === 0;
    }

    if (elements.mlNext) {
      elements.mlNext.disabled = currentIndex === totalCards - 1;
    }
  }

  async function cargarRecomendacion(contexto, { silent = false } = {}) {
    const url = new URL(`/api/recomendacion/${contexto}`, window.location.origin);
    const requestId = ++state.requestId;

    if (!silent) setStatus('loading');

    try {
      const res = await fetch(url.toString(), { headers: { Accept: 'application/json' }, cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const payload = await res.json();
      if (requestId !== state.requestId) return;

      if (!payload.ok) throw new Error(payload?.error?.message || 'Error IA');

      const data = normalizar(payload.data);
      state.data = data;
      setStatus('ready');

      mappedCards.forEach((elements) => aplicarCard(elements, data));
    } catch (err) {
      console.error('[IA] Error al cargar recomendación:', err);
      setStatus('error');

      const fallback = {
        ...DEFAULT_DATA,
        mensaje: 'No se pudo obtener la recomendación.',
        severidad: 'warning',
      };

      mappedCards.forEach((elements) => aplicarCard(elements, fallback));
    }
  }

  function iniciarAutoActualizacion(contexto) {
    if (state.timer) {
      clearInterval(state.timer);
    }

    state.timer = setInterval(() => {
      cargarRecomendacion(contexto, { silent: true });
    }, AUTO_REFRESH_INTERVAL);
  }

  function inicializarAuditoria() {
    if (obtenerContexto() !== 'auditoria') return;

    cargarRecomendacion('auditoria');
    iniciarAutoActualizacion('auditoria');

    const refresh = document.getElementById('btn-refresh-auditoria');
    if (refresh) {
      refresh.addEventListener('click', (event) => {
        event.preventDefault();
        cargarRecomendacion('auditoria');
        iniciarAutoActualizacion('auditoria');
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarAuditoria, { once: true });
  } else {
    inicializarAuditoria();
  }
})();