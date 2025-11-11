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

  const DEFAULT_DATA = {
    titulo: 'Recomendación automática',
    mensaje: 'Sin detalles disponibles.',
    resumen: '',
    detalle: 'Sin detalles disponibles.',
    solucion: '',
    severidad: 'info',
    detalleExtendido: '',
  };

  const state = {
    status: 'idle',
    data: null,
    error: null,
    requestId: 0,
  };

  function obtenerContexto() {
    const path = window.location.pathname.split('/').filter(Boolean);
    return path[0] || 'auditoria';
  }

  function asegurarTexto(valor, fallback) {
    if (typeof valor === 'string') {
      const trimmed = valor.trim();
      return trimmed || fallback;
    }
    if (valor == null) {
      return fallback;
    }
    return String(valor);
  }

  function asegurarSeveridad(valor) {
    const safe = asegurarTexto(valor, 'info').toLowerCase();
    return ['info', 'warning', 'critical'].includes(safe) ? safe : 'info';
  }

  function sanitizarRecomendacion(raw) {
    const origen = raw && typeof raw === 'object' ? raw : {};
    const resumen = asegurarTexto(origen.mensaje_resumen, '');
    const mensaje = asegurarTexto(origen.mensaje, resumen || DEFAULT_DATA.mensaje);
    const detalleExtendido = asegurarTexto(origen.mensaje_detallado, '');
    const detalle = asegurarTexto(origen.detalle, detalleExtendido || mensaje);
    const solucion = asegurarTexto(origen.solucion, DEFAULT_DATA.solucion);

    return {
      titulo: asegurarTexto(origen.titulo, DEFAULT_DATA.titulo),
      mensaje,
      resumen: resumen || mensaje,
      detalle: detalle || mensaje,
      solucion,
      severidad: asegurarSeveridad(origen.severidad),
      detalleExtendido: detalleExtendido || detalle || mensaje,
    };
  }

  function aplicarEstado(status, error) {
    state.status = status;
    state.error = error || null;
    const isBusy = status === 'loading' || status === 'refreshing';

    cards.forEach((card) => {
      card.dataset.iaStatus = status;
      card.setAttribute('aria-busy', String(isBusy));
    });
  }

  function actualizarCard(card, data) {
    const { titulo, mensaje, solucion, severidad } = data;
    const normalizedSeverity = asegurarSeveridad(severidad);

    card.dataset.severity = normalizedSeverity;
    card.dataset.nivel = severityNivel[normalizedSeverity] || severityNivel.info;

    const icon = card.querySelector('[data-ia-icon]');
    const title = card.querySelector('[data-ia-title]');
    const severity = card.querySelector('[data-ia-severity]');
    const message = card.querySelector('[data-ia-message]');
    const marquee = card.querySelector('[data-ia-marquee]');
    const solution = card.querySelector('[data-ia-solution]');

    if (icon) {
      icon.textContent = severityIcons[normalizedSeverity] || severityIcons.info;
    }
    if (title) {
      title.textContent = titulo || DEFAULT_DATA.titulo;
      title.setAttribute('title', title.textContent);
    }
    if (severity) {
      severity.textContent = severityLabels[normalizedSeverity] || severityLabels.info;
    }

    const mensajeFinal = mensaje || DEFAULT_DATA.mensaje;
    if (message) {
      message.textContent = mensajeFinal;
      if (message !== marquee) {
        message.setAttribute('title', mensajeFinal);
      }
    }
    if (marquee) {
      marquee.textContent = mensajeFinal;
      marquee.setAttribute('title', mensajeFinal);
    }

    if (solution) {
      const hasSolution = Boolean(solucion);
      solution.textContent = hasSolution ? solucion : 'Sin acciones sugeridas.';
      solution.classList.toggle('is-hidden', !hasSolution);
    }

    if (!card.classList.contains('is-visible')) {
      card.classList.add('is-visible');
    }
  }

  function renderizarCards(data) {
    const normalizado = sanitizarRecomendacion(data);
    cards.forEach((card) => actualizarCard(card, normalizado));
  }

  function mostrarFallback(error) {
    const detalle = error && error.message ? ` Detalle: ${error.message}` : '';
    const payload = {
      titulo: 'Recomendación no disponible',
      mensaje: `No se pudo obtener la recomendación automática.${detalle}`.trim(),
      detalle: `La API de recomendaciones no respondió correctamente.${detalle}`.trim(),
      solucion: 'Revise la conectividad y vuelva a intentarlo en unos minutos.',
      severidad: 'warning',
    };
    renderizarCards(payload);
  }

  async function cargarRecomendacion(contexto) {
    const url = new URL('/api/ia/auditoria', window.location.origin);
    if (contexto) {
      url.searchParams.set('contexto', contexto);
    }

    const requestId = ++state.requestId;
    aplicarEstado(state.data ? 'refreshing' : 'loading');

    try {
      const response = await fetch(url.toString(), {
        headers: { Accept: 'application/json' },
        cache: 'no-store',
      });

      if (!response.ok) {
        throw new Error(`Respuesta HTTP ${response.status}`);
      }

      const payload = await response.json();
      if (requestId !== state.requestId) {
        return;
      }

      let contenido = payload;
      if (contenido && typeof contenido === 'object' && 'ok' in contenido) {
        if (!contenido.ok) {
          const mensajeError = asegurarTexto(
            contenido.error && contenido.error.message,
            'Servicio de recomendaciones no disponible.'
          );
          const error = new Error(mensajeError);
          error.cause = contenido.error || null;
          throw error;
        }
        contenido = contenido.data;
      }

      const normalizado = sanitizarRecomendacion(contenido);
      state.data = normalizado;
      aplicarEstado('ready');
      renderizarCards(normalizado);
    } catch (error) {
      if (requestId !== state.requestId) {
        return;
      }

      console.error('[recomendaciones] error', error);

      if (!state.data) {
        aplicarEstado('error', error);
        mostrarFallback(error);
      } else {
        aplicarEstado('stale', error);
      }
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const contextoInicial = obtenerContexto();
    cargarRecomendacion(contextoInicial);

    const refreshButton = document.getElementById('btn-refresh-auditoria');
    if (refreshButton) {
      refreshButton.addEventListener('click', (event) => {
        event.preventDefault();
        refreshButton.classList.add('animate-spin-once');
        const contexto = obtenerContexto();
        cargarRecomendacion(contexto)
          .catch(() => {
            /* el error ya fue gestionado en cargarRecomendacion */
          })
          .finally(() => {
            refreshButton.classList.remove('animate-spin-once');
          });
      });
    }
  });
})();
