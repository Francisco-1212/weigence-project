(function () {
  const cards = Array.from(document.querySelectorAll('[data-ia-card]'));
  if (!cards.length) {
    return;
  }

  const severityLabels = {
    info: 'Nivel informativo',
    warning: 'Atención requerida',
    critical: 'Riesgo crítico',
  };

  const severityNivel = {
    info: 'normal',
    warning: 'advertencia',
    critical: 'critico',
  };

  const severityIcons = {
    info: 'auto_awesome',
    warning: 'warning',
    critical: 'report',
  };

  function obtenerContexto() {
    const path = window.location.pathname.split('/').filter(Boolean);
    return path[0] || 'auditoria';
  }

  function actualizarCard(card, data) {
    const { titulo, mensaje, solucion, severidad } = data;
    const normalizedSeverity = ['info', 'warning', 'critical'].includes(severidad)
      ? severidad
      : 'info';

    card.dataset.severity = normalizedSeverity;
    const nivel = severityNivel[normalizedSeverity] || severityNivel.info;
    card.setAttribute('data-nivel', nivel);
    const icon = card.querySelector('[data-ia-icon]');
    const title = card.querySelector('[data-ia-title]');
    const severity = card.querySelector('[data-ia-severity]');
    const message = card.querySelector('[data-ia-message]');
    const solution = card.querySelector('[data-ia-solution]');

    if (icon) {
      icon.textContent = severityIcons[normalizedSeverity] || severityIcons.info;
    }
    if (title) {
      title.textContent = titulo || 'Recomendación automática';
    }
    if (severity) {
      severity.textContent = severityLabels[normalizedSeverity] || severityLabels.info;
    }
    if (message) {
      message.textContent = mensaje || 'Sin detalles disponibles.';
    }
    if (solution) {
      const hasSolution = Boolean(solucion);
      solution.textContent = hasSolution
        ? solucion
        : 'Sin acciones sugeridas.';
      solution.classList.toggle('is-hidden', !hasSolution);
    }

    card.classList.remove('is-visible');
    void card.offsetWidth; // force reflow to restart animation
    card.classList.add('is-visible');
  }

  function mostrarFallback(error) {
    const payload = {
      titulo: 'Recomendación no disponible',
      mensaje: 'No se pudo obtener la recomendación automática. ' + (error?.message || ''),
      solucion: 'Revise la conectividad y vuelva a intentarlo en unos minutos.',
      severidad: 'warning',
    };
    cards.forEach((card) => actualizarCard(card, payload));
  }

  function cargarRecomendacion(contexto) {
    const url = new URL('/api/ia/auditoria', window.location.origin);
    if (contexto) {
      url.searchParams.set('contexto', contexto);
    }
    return fetch(url.toString(), { headers: { Accept: 'application/json' } })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Respuesta HTTP ' + response.status);
        }
        return response.json();
      })
      .then((data) => {
        if (!data || typeof data !== 'object') {
          throw new Error('Formato inesperado en la respuesta');
        }
        cards.forEach((card) => actualizarCard(card, data));
      })
      .catch((error) => {
        console.error('[recomendaciones] error', error);
        mostrarFallback(error);
      });
  }

  document.addEventListener('DOMContentLoaded', () => {
    const contexto = obtenerContexto();
    cargarRecomendacion(contexto);

    const refreshButton = document.getElementById('btn-refresh-auditoria');
    if (refreshButton) {
      refreshButton.addEventListener('click', (event) => {
        event.preventDefault();
        refreshButton.classList.add('animate-spin-once');
        cargarRecomendacion(contexto).finally(() => {
          refreshButton.classList.remove('animate-spin-once');
        });
      });
    }
  });
})();
