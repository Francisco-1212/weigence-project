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
    const { titulo, mensaje, solucion, severidad } = data;

    elements.card.dataset.severity = severidad;

    if (elements.icon) elements.icon.textContent = severityIcons[severidad];
    if (elements.title) elements.title.textContent = titulo;
    if (elements.severity) elements.severity.textContent = severityLabels[severidad];
    if (elements.message) elements.message.textContent = mensaje;
    if (elements.solution) elements.solution.textContent = solucion;

    animateContent(elements);
    elements.card.classList.add('is-visible');
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