(function () {
  'use strict';
  
  const auditoriaCard = document.getElementById('ai-recomendacion-auditoria');
  if (!auditoriaCard) return;

  // 📡 Canal de comunicación entre pestañas
  const systemChannel = new BroadcastChannel('weigence-system-updates');

  // ⚙️ Configuración
  const CONFIG = {
    AUTO_REFRESH_INTERVAL: 60000, // 60 segundos
    SEVERITY_LABELS: {
      info: 'Información',
      warning: 'Requiere Atención',
      critical: 'Acción Urgente',
    },
    SEVERITY_ICONS: {
      info: 'auto_awesome',
      warning: 'warning',
      critical: 'report',
    },
    MODULE_ICONS: {
      dashboard: 'dashboard',
      inventario: 'inventory_2',
      movimientos: 'swap_horiz',
      ventas: 'point_of_sale',
      alertas: 'notifications_active',
      auditoria: 'shield',
    },
    MODULE_LABELS: {
      dashboard: 'Dashboard',
      inventario: 'Inventario',
      movimientos: 'Movimientos',
      ventas: 'Ventas',
      alertas: 'Alertas',
      auditoria: 'Auditoría'
    },
    MODULE_ROUTES: {
      dashboard: '/dashboard',
      inventario: '/inventario',
      movimientos: '/movimientos',
      ventas: '/ventas',
      alertas: '/alertas',
      auditoria: '/auditoria'
    },
    SEVERITY_CONFIG: {
      low: { label: 'Baja', color: '#10b981', width: '25%' },
      medium: { label: 'Media', color: '#f59e0b', width: '50%' },
      high: { label: 'Alta', color: '#f97316', width: '75%' },
      critical: { label: 'Crítica', color: '#ef4444', width: '100%' }
    }
  };

  // 🔄 Estado global
  const state = { 
    status: 'idle', 
    data: null, 
    requestId: 0, 
    timer: null 
  };

  // 🎯 Elementos del DOM
  const elements = {
    card: auditoriaCard,
    icon: auditoriaCard.querySelector('[data-ia-icon]'),
    title: auditoriaCard.querySelector('[data-ia-title]'),
    severity: auditoriaCard.querySelector('[data-ia-severity]'),
    message: auditoriaCard.querySelector('[data-ia-message]'),
    solution: auditoriaCard.querySelector('[data-ia-solution]'),
    mlBadge: auditoriaCard.querySelector('[data-ml-badge]'),
    moduleContainer: auditoriaCard.querySelector('[data-ia-module]'),
    moduleIcon: auditoriaCard.querySelector('[data-module-icon]'),
    moduleName: auditoriaCard.querySelector('[data-module-name]'),
    severityDetail: auditoriaCard.querySelector('[data-severity-detail]'),
    severityBar: auditoriaCard.querySelector('[data-severity-bar]'),
    severityText: auditoriaCard.querySelector('[data-severity-text]'),
    mlNavigation: auditoriaCard.querySelector('[data-ml-navigation]'),
    navPrev: auditoriaCard.querySelector('[data-nav-prev]'),
    navNext: auditoriaCard.querySelector('[data-nav-next]'),
    navCurrent: auditoriaCard.querySelector('[data-nav-current]'),
    navTotal: auditoriaCard.querySelector('[data-nav-total]'),
    mlHallazgos: [],
    currentHallazgoIndex: 0,
  };

  // 🔧 Utilidades
  function obtenerContexto() {
    const path = window.location.pathname.split('/').filter(Boolean);
    return path[0] || 'auditoria';
  }

  function normalizar(raw) {
    const origen = raw && typeof raw === 'object' ? raw : {};
    console.log('[IA-CARD] Datos RAW recibidos:', raw);
    
    const normalizado = {
      titulo: origen.titulo?.trim() || 'Análisis Inteligente en Progreso',
      mensaje: origen.mensaje?.trim() || 'El sistema está procesando datos del ecosistema...',
      solucion: origen.solucion?.trim() || 'Los insights estarán disponibles en breve',
      severidad: ['info', 'warning', 'critical'].includes(origen.severidad?.toLowerCase()) 
        ? origen.severidad.toLowerCase() 
        : 'info',
      ml_anomaly_detected: Boolean(origen.ml_anomaly_detected),
      ml_insights_cards: Array.isArray(origen.ml_insights_cards) ? origen.ml_insights_cards : [],
    };
    
    console.log('[IA-CARD] Datos normalizados:', normalizado);
    return normalizado;
  }

  function setStatus(status) {
    state.status = status;
    elements.card.dataset.iaStatus = status;
    elements.card.setAttribute('aria-busy', status === 'loading' ? 'true' : 'false');
  }

  function aplicarCard(data) {
    const { titulo, mensaje, solucion, severidad, ml_anomaly_detected, ml_insights_cards } = data;

    console.log('[IA-CARD] Aplicando datos:', {
      ml_anomaly_detected,
      ml_insights_cards_length: ml_insights_cards?.length,
      ml_insights_cards,
      data_completo: data
    });

    elements.card.dataset.severity = severidad;
    if (elements.icon) elements.icon.textContent = CONFIG.SEVERITY_ICONS[severidad];
    if (elements.title) elements.title.textContent = titulo;
    if (elements.severity) elements.severity.textContent = CONFIG.SEVERITY_LABELS[severidad];
    if (elements.message) elements.message.textContent = mensaje;
    if (elements.solution) elements.solution.textContent = solucion;
    // Badge "Pro" siempre visible
    if (elements.mlBadge) elements.mlBadge.style.display = 'inline-flex';

    // Si hay hallazgos ML, configurar navegación (mostrar siempre que existan cards)
    console.log('[IA-CARD] Condición ML:', ml_anomaly_detected, 'cards:', ml_insights_cards?.length);
    if (ml_insights_cards && ml_insights_cards.length > 0) {
      elements.mlHallazgos = ml_insights_cards;
      elements.currentHallazgoIndex = 0;
      mostrarHallazgo(0);
      configurarNavegacion();
    } else {
      if (elements.moduleContainer) elements.moduleContainer.style.display = 'none';
      if (elements.severityDetail) elements.severityDetail.style.display = 'none';
      if (elements.mlNavigation) elements.mlNavigation.style.display = 'none';
    }

    elements.card.classList.add('is-visible');
  }

  // 🎯 Mostrar hallazgo específico
  function mostrarHallazgo(index) {
    const hallazgo = elements.mlHallazgos[index];
    if (!hallazgo) return;

    console.log('[IA-CARD] Mostrando hallazgo:', hallazgo);

    // Actualizar título
    if (elements.title) elements.title.textContent = hallazgo.titulo || 'Hallazgo detectado';

    // Actualizar mensaje/descripción
    if (elements.message) elements.message.textContent = hallazgo.descripcion || 'Sin detalles disponibles';

    // Mostrar módulo afectado con navegación
    if (elements.moduleContainer && hallazgo.modulo) {
      elements.moduleContainer.style.display = 'flex';
      elements.moduleContainer.style.cursor = 'pointer';
      elements.moduleContainer.title = `Ir a ${CONFIG.MODULE_LABELS[hallazgo.modulo] || hallazgo.modulo}`;
      
      if (elements.moduleIcon) elements.moduleIcon.textContent = CONFIG.MODULE_ICONS[hallazgo.modulo] || 'dashboard';
      if (elements.moduleName) elements.moduleName.textContent = CONFIG.MODULE_LABELS[hallazgo.modulo] || hallazgo.modulo;
      
      // Hacer clickeable el badge de módulo
      elements.moduleContainer.onclick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const route = CONFIG.MODULE_ROUTES[hallazgo.modulo];
        if (route) {
          console.log('[IA-CARD] Navegando a:', route);
          window.location.href = route;
        }
      };
      
      // Efecto hover
      elements.moduleContainer.onmouseenter = () => {
        elements.moduleContainer.style.backgroundColor = 'rgba(59, 130, 246, 0.15)';
        elements.moduleContainer.style.transform = 'scale(1.05)';
        elements.moduleContainer.style.transition = 'all 0.2s ease';
      };
      elements.moduleContainer.onmouseleave = () => {
        elements.moduleContainer.style.backgroundColor = '';
        elements.moduleContainer.style.transform = 'scale(1)';
      };
    } else if (elements.moduleContainer) {
      elements.moduleContainer.style.display = 'none';
      elements.moduleContainer.onclick = null;
      elements.moduleContainer.onmouseenter = null;
      elements.moduleContainer.onmouseleave = null;
    }

    // Mostrar severidad con barra de progreso
    if (elements.severityDetail && hallazgo.ml_severity) {
      elements.severityDetail.style.display = 'block';
      const severityConfig = CONFIG.SEVERITY_CONFIG[hallazgo.ml_severity.toLowerCase()] || CONFIG.SEVERITY_CONFIG.medium;
      
      if (elements.severityText) {
        elements.severityText.textContent = severityConfig.label;
        // Aplicar color al texto según severidad
        elements.severityText.style.backgroundColor = `${severityConfig.color}20`;
        elements.severityText.style.color = severityConfig.color;
        elements.severityText.style.borderColor = `${severityConfig.color}40`;
      }
      if (elements.severityBar) {
        elements.severityBar.style.backgroundColor = severityConfig.color;
        elements.severityBar.style.width = severityConfig.width;
      }
    } else if (elements.severityDetail) {
      elements.severityDetail.style.display = 'none';
    }

    // Actualizar plan de acción
    if (elements.solution && hallazgo.plan_accion) {
      elements.solution.textContent = hallazgo.plan_accion;
    } else if (elements.solution) {
      elements.solution.textContent = 'Sin acciones sugeridas';
    }

    // Actualizar contador de navegación
    if (elements.navCurrent) elements.navCurrent.textContent = index + 1;
    if (elements.navTotal) elements.navTotal.textContent = elements.mlHallazgos.length;

    // Actualizar estado de botones de navegación
    if (elements.navPrev) elements.navPrev.disabled = index === 0;
    if (elements.navNext) elements.navNext.disabled = index === elements.mlHallazgos.length - 1;

    elements.currentHallazgoIndex = index;
  }

  // 🎮 Configurar navegación
  function configurarNavegacion() {
    if (!elements.mlNavigation || elements.mlHallazgos.length === 0) return;

    // Mostrar navegación siempre (incluso con 1 hallazgo para mostrar contador)
    elements.mlNavigation.style.display = 'flex';

    if (elements.navPrev) {
      elements.navPrev.onclick = () => mostrarHallazgo(Math.max(0, elements.currentHallazgoIndex - 1));
    }

    if (elements.navNext) {
      elements.navNext.onclick = () => mostrarHallazgo(Math.min(elements.mlHallazgos.length - 1, elements.currentHallazgoIndex + 1));
    }

    // Navegación con teclado
    elements.card.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft' && elements.currentHallazgoIndex > 0) {
        e.preventDefault();
        mostrarHallazgo(elements.currentHallazgoIndex - 1);
      } else if (e.key === 'ArrowRight' && elements.currentHallazgoIndex < elements.mlHallazgos.length - 1) {
        e.preventDefault();
        mostrarHallazgo(elements.currentHallazgoIndex + 1);
      }
    });
  }

  // 📡 Cargar recomendaciones
  async function cargarRecomendacion(contexto, { silent = false } = {}) {
    const url = `/api/recomendacion/${contexto}`;
    const requestId = ++state.requestId;

    if (!silent) setStatus('loading');

    try {
      const res = await fetch(url, { 
        headers: { Accept: 'application/json' }, 
        cache: 'no-store' 
      });
      
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      if (requestId !== state.requestId) return;

      const payload = await res.json();
      console.log('[IA-CARD] Payload completo de API:', payload);
      
      if (!payload.ok) throw new Error(payload?.error?.message || 'Error IA');

      const data = normalizar(payload.data);
      state.data = data;
      setStatus('ready');
      aplicarCard(data);
    } catch (err) {
      console.error('[IA] Error al cargar recomendación:', err);
      setStatus('error');
      aplicarCard({
        titulo: 'Reconectando con el análisis',
        mensaje: 'El sistema está recalibrando los algoritmos de detección. Esto es temporal.',
        solucion: 'El análisis inteligente se reanudará automáticamente en unos momentos.',
        severidad: 'info',
        ml_anomaly_detected: false,
        ml_insights_cards: []
      });
    }
  }

  // ⏰ Auto-actualización
  function iniciarAutoActualizacion(contexto) {
    if (state.timer) clearInterval(state.timer);
    state.timer = setInterval(() => {
      cargarRecomendacion(contexto, { silent: true });
    }, CONFIG.AUTO_REFRESH_INTERVAL);
  }

  // 🚀 Inicialización
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

    // 🔄 Escuchar eventos locales
    window.addEventListener('system-data-changed', (event) => {
      console.log('[IA] Cambio detectado (local), refrescando...', event.detail);
      cargarRecomendacion('auditoria', { silent: true });
    });

    // 📡 Escuchar cambios desde otras pestañas
    systemChannel.onmessage = (event) => {
      if (event.data.type === 'data-changed') {
        console.log('[IA] Cambio detectado (otra pestaña), refrescando...', event.data.detail);
        cargarRecomendacion('auditoria', { silent: true });
      }
    };
  }

  // ▶️ Iniciar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializarAuditoria, { once: true });
  } else {
    inicializarAuditoria();
  }
})();