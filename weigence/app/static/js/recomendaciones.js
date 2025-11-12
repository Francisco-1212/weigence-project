(function () {
  const cards = Array.from(document.querySelectorAll('#auditoria [data-ia-card]'));

  if (!cards.length) return;

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

  const state = { status: 'idle', data: null, requestId: 0 };

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

  function aplicarCard(card, data) {
    const { titulo, mensaje, solucion, severidad } = data;
    const icon = card.querySelector('[data-ia-icon]');
    const title = card.querySelector('[data-ia-title]');
    const severity = card.querySelector('[data-ia-severity]');
    const message = card.querySelector('[data-ia-message]');
    const solution = card.querySelector('[data-ia-solution]');

    card.dataset.severity = severidad;

    if (icon) icon.textContent = severityIcons[severidad];
    if (title) title.textContent = titulo;
    if (severity) severity.textContent = severityLabels[severidad];
    if (message) message.textContent = mensaje;
    if (solution) solution.textContent = solucion;
  }

  async function cargarRecomendacion(contexto) {
    const url = new URL(`/api/recomendacion/${contexto}`, window.location.origin);
    const requestId = ++state.requestId;
    state.status = 'loading';

    try {
      const res = await fetch(url.toString(), { headers: { Accept: 'application/json' }, cache: 'no-store' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const payload = await res.json();
      if (requestId !== state.requestId) return;

      if (!payload.ok) throw new Error(payload?.error?.message || 'Error IA');
      const data = normalizar(payload.data);
      state.data = data;
      state.status = 'ready';
      cards.forEach((c) => aplicarCard(c, data));
    } catch (err) {
      console.error('[IA] Error al cargar recomendación:', err);
      const fallback = { ...DEFAULT_DATA, mensaje: 'No se pudo obtener la recomendación.', severidad: 'warning' };
      cards.forEach((c) => aplicarCard(c, fallback));
    }
  }

  function inicializarAuditoria() {
    if (obtenerContexto() === 'auditoria') {
      cargarRecomendacion('auditoria'); // SIEMPRE carga al entrar
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAuditoria);
  } else {
    initAuditoria();
  }

  const refresh = document.getElementById('btn-refresh-auditoria');
  if (refresh) {
    refresh.addEventListener('click', (e) => {
      e.preventDefault();
      cargarRecomendacion(obtenerContexto());
    });
  }

  // --- ejecutar siempre ---
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarAuditoria);
  } else {
    inicializarAuditoria(); // si el DOM ya está cargado
  }
})();
