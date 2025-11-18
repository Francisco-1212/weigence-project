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
    mlInsights: card.querySelector('[data-ml-insights]'),
    mlTrack: card.querySelector('[data-ml-track]'),
    mlDots: card.querySelector('[data-ml-dots]'),
    mlPrev: card.querySelector('[data-ml-prev]'),
    mlNext: card.querySelector('[data-ml-next]'),
    situacionMensaje: card.querySelector('[data-situacion-mensaje]'),
    situacionTexto: card.querySelector('[data-situacion-texto]'),
    carouselState: { currentIndex: 0, totalCards: 0 },
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

    // Mostrar mensaje de situación si hay uno
    if (elements.situacionMensaje && situacion_actual) {
      elements.situacionMensaje.style.display = 'flex';
      if (elements.situacionTexto) {
        elements.situacionTexto.textContent = situacion_actual;
      }
    } else if (elements.situacionMensaje) {
      elements.situacionMensaje.style.display = 'none';
    }

    // Mostrar badge ML si detectó anomalía
    if (elements.mlBadge) {
      elements.mlBadge.style.display = ml_anomaly_detected ? 'inline-block' : 'none';
    }

    // Mostrar insights ML con carrusel si detectó anomalía
    if (elements.mlInsights && ml_anomaly_detected && ml_insights_cards.length > 0) {
      elements.mlInsights.style.display = 'block';
      setupCarousel(elements, ml_insights_cards);
    } else if (elements.mlInsights) {
      elements.mlInsights.style.display = 'none';
    }

    animateContent(elements);
    elements.card.classList.add('is-visible');
  }

  function setupCarousel(elements, cards) {
    if (!elements.mlTrack) return;

    // Limpiar carrusel anterior
    elements.mlTrack.innerHTML = '';
    if (elements.mlDots) elements.mlDots.innerHTML = '';

    // Referencias al header dinámico
    const headerTitle = elements.card.querySelector('[data-ml-carousel-title]');
    const headerSubtitle = elements.card.querySelector('[data-ml-carousel-subtitle]');
    const counterEl = elements.card.querySelector('[data-ml-counter]');

    // Crear cards
    cards.forEach((card, index) => {
      const cardEl = document.createElement('div');
      cardEl.className = 'ml-carousel__card';
      cardEl.dataset.cardTitle = card.titulo; // Guardar título para header dinámico
      cardEl.innerHTML = `
        <div class="ml-carousel__card-header">
          <span class="ml-carousel__icon">${card.icono}</span>
          <h4 class="ml-carousel__title">${card.titulo}</h4>
        </div>
        <p class="ml-carousel__description">${card.descripcion}</p>
        ${card.accion ? `
          <button class="ml-carousel__action">
            ${card.accion}
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        ` : ''}
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
      elements.mlPrev.addEventListener('click', () => {
        goToSlide(elements, elements.carouselState.currentIndex - 1);
      });
    }

    if (elements.mlNext) {
      elements.mlNext.addEventListener('click', () => {
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