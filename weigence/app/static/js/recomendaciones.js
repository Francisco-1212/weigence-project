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
    timer: null,
    currentView: 'dashboard', // 'dashboard', 'detail'
    currentFilter: null, // 'critical', 'high', 'medium', 'low'
    filteredHallazgos: [],
    previousCounts: { critical: 0, high: 0, medium: 0, low: 0 }, // 🆕 Para tendencias
    filterModule: '' // 🆕 Para filtro de módulo
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
    mlNavigation: auditoriaCard.querySelectorAll('[data-ml-navigation]'),
    navPrev: auditoriaCard.querySelectorAll('[data-nav-prev]'),
    navNext: auditoriaCard.querySelectorAll('[data-nav-next]'),
    navCurrent: auditoriaCard.querySelectorAll('[data-nav-current]'),
    navTotal: auditoriaCard.querySelectorAll('[data-nav-total]'),
    // Nuevos elementos para pestañas
    tabs: auditoriaCard.querySelectorAll('[data-tab]'),
    panels: auditoriaCard.querySelectorAll('.ia-pro-panel'),
    timestamp: auditoriaCard.querySelector('[data-timestamp]'),
    moduloText: auditoriaCard.querySelector('[data-modulo-text]'),
    confidence: auditoriaCard.querySelector('[data-confidence]'),
    impactAnalysis: auditoriaCard.querySelector('[data-impact-analysis]'),
    metric1: auditoriaCard.querySelector('[data-metric-1]'),
    metric2: auditoriaCard.querySelector('[data-metric-2]'),
    metric3: auditoriaCard.querySelector('[data-metric-3]'),
    mlDetection: auditoriaCard.querySelector('[data-ml-detection]'),
    mlScore: auditoriaCard.querySelector('[data-ml-score]'),
    actionSteps: auditoriaCard.querySelector('[data-action-steps]'),
    severityBadge: auditoriaCard.querySelector('.severity-badge'),
    // Elementos de las 2 vistas
    dashboardView: auditoriaCard.querySelector('#ia-dashboard-view'),
    detailView: auditoriaCard.querySelector('#ia-detail-view'),
    btnBackToDashboard: auditoriaCard.querySelector('#btn-back-to-dashboard'),
    severityCards: auditoriaCard.querySelectorAll('[data-severity-filter]'),
    breadcrumbSeverity: auditoriaCard.querySelector('#breadcrumb-severity'),
    noFindings: auditoriaCard.querySelector('#ia-no-findings'),
    // Mensaje contextual dinámico
    dashboardContextTitle: auditoriaCard.querySelector('#dashboard-context-title'),
    dashboardContextMessage: auditoriaCard.querySelector('#dashboard-context-message'),
    mlHallazgos: [],
    currentHallazgoIndex: 0,
    // 🆕 Elementos de filtros
    filterModule: document.getElementById('ia-filter-module'),
    clearFilters: document.getElementById('ia-clear-filters'),
    // 🆕 Modal de atajos de teclado
    keyboardModal: document.getElementById('ia-keyboard-modal'),
    keyboardModalClose: document.getElementById('ia-keyboard-modal-close'),
    keyboardHelpBtn: document.getElementById('ia-keyboard-help-btn'),
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
    const { titulo, mensaje, solucion, severidad, ml_anomaly_detected, ml_insights_cards, score, confianza } = data;

    console.log('[IA-CARD] Aplicando datos:', {
      ml_anomaly_detected,
      ml_insights_cards_length: ml_insights_cards?.length,
      ml_insights_cards,
      data_completo: data
    });

    elements.card.dataset.severity = severidad;
    if (elements.icon) elements.icon.textContent = CONFIG.SEVERITY_ICONS[severidad];
    
    // Actualizar metadata
    if (elements.timestamp) elements.timestamp.textContent = new Date().toLocaleTimeString('es-CL');
    if (elements.confidence) elements.confidence.textContent = Math.round((confianza || 0.85) * 100);
    
    // Badge "Pro" siempre visible
    if (elements.mlBadge) elements.mlBadge.style.display = 'inline-flex';

    // Si hay hallazgos ML, mostrar resumen por severidad
    if (ml_insights_cards && ml_insights_cards.length > 0) {
      elements.mlHallazgos = ml_insights_cards;
      mostrarResumenSeveridad(ml_insights_cards);
      configurarNavegacion();
      
      // 🆕 SOLO mostrar vista dashboard en carga INICIAL (no en auto-refresh)
      // Si ya estás en vista detail, mantener ahí
      if (state.currentView !== 'detail') {
        mostrarVista('dashboard');
      } else {
        // Actualizar contadores en segundo plano sin cambiar vista
        actualizarContadoresSilencioso(ml_insights_cards);
      }
    } else {
      if (elements.noFindings) elements.noFindings.style.display = 'block';
      elements.mlNavigation.forEach(nav => nav.style.display = 'none');
    }

    elements.card.classList.add('is-visible');
  }

  // 🔄 Actualizar contadores silenciosamente (sin resetear vista)
  function actualizarContadoresSilencioso(hallazgos) {
    // Contar por severidad
    const counts = {
      critical: hallazgos.filter(h => h.ml_severity === 'critical').length,
      high: hallazgos.filter(h => h.ml_severity === 'high').length,
      medium: hallazgos.filter(h => h.ml_severity === 'medium').length,
      low: hallazgos.filter(h => h.ml_severity === 'low').length,
    };

    console.log('[IA-CARD] Actualización silenciosa - Conteo:', counts);

    // 🆕 Detectar si hay nuevos hallazgos críticos
    const criticalAntes = state.previousCounts.critical || 0;
    const criticalAhora = counts.critical;
    if (criticalAhora > criticalAntes) {
      const diff = criticalAhora - criticalAntes;
      mostrarNotificacionDiscreta(`🔴 ${diff} nueva(s) alerta(s) crítica(s) detectada(s)`);
    }

    // Actualizar SOLO los números en las cards (sin cambiar vista)
    const countElements = {
      critical: document.getElementById('count-critical'),
      high: document.getElementById('count-high'),
      medium: document.getElementById('count-medium'),
      low: document.getElementById('count-low')
    };

    Object.keys(counts).forEach(severity => {
      if (countElements[severity]) {
        // Añadir animación sutil si el número cambió
        const oldValue = parseInt(countElements[severity].textContent) || 0;
        const newValue = counts[severity];
        
        if (oldValue !== newValue) {
          countElements[severity].style.transition = 'transform 0.3s ease';
          countElements[severity].style.transform = 'scale(1.2)';
          countElements[severity].textContent = newValue;
          
          setTimeout(() => {
            countElements[severity].style.transform = 'scale(1)';
          }, 300);
        } else {
          countElements[severity].textContent = newValue;
        }
        
        // 🆕 Actualizar tendencias
        actualizarTendencia(severity, newValue, state.previousCounts[severity] || 0);
      }
    });

    // Guardar conteos actuales para próxima comparación
    state.previousCounts = { ...counts };

    // Si hay nuevos hallazgos en la severidad actual, actualizar filtrado
    if (state.currentFilter) {
      const newFilteredHallazgos = hallazgos.filter(h => h.ml_severity === state.currentFilter);
      
      // Solo actualizar si cambio la cantidad (nuevo hallazgo o se resolvió uno)
      if (newFilteredHallazgos.length !== state.filteredHallazgos.length) {
        console.log('[IA-CARD] Nuevos hallazgos detectados en severidad actual, actualizando...');
        state.filteredHallazgos = newFilteredHallazgos;
        
        // Actualizar contador de navegación
        elements.navTotal.forEach(el => el.textContent = newFilteredHallazgos.length);
        
        // Si el hallazgo actual ya no existe, volver al primero
        if (elements.currentHallazgoIndex >= newFilteredHallazgos.length) {
          mostrarHallazgoFiltrado(0);
        }
      }
    }
  }

  // 🆕 Actualizar indicadores de tendencia
  function actualizarTendencia(severity, valorActual, valorAnterior) {
    const trendElement = document.getElementById(`trend-${severity}`);
    if (!trendElement) return;

    const diff = valorActual - valorAnterior;
    
    if (diff === 0) {
      trendElement.style.opacity = '0';
      return;
    }

    const trendIcon = trendElement.querySelector('.trend-icon');
    const trendValue = trendElement.querySelector('.trend-value');
    
    if (diff > 0) {
      trendIcon.textContent = 'trending_up';
      trendIcon.className = 'material-symbols-outlined text-xs trend-icon text-red-500 dark:text-red-400';
      trendValue.textContent = `+${diff}`;
      trendValue.className = 'trend-value font-semibold text-red-600 dark:text-red-400';
    } else {
      trendIcon.textContent = 'trending_down';
      trendIcon.className = 'material-symbols-outlined text-xs trend-icon text-green-500 dark:text-green-400';
      trendValue.textContent = `${diff}`;
      trendValue.className = 'trend-value font-semibold text-green-600 dark:text-green-400';
    }
    
    trendElement.style.opacity = '1';
  }

  // 🆕 Mostrar notificación discreta tipo toast
  function mostrarNotificacionDiscreta(mensaje) {
    const toast = document.createElement('div');
    toast.className = 'ia-toast-notification fixed top-20 right-4 px-4 py-2.5 bg-red-500 text-white text-xs font-semibold rounded-lg shadow-2xl z-[9999] flex items-center gap-2 border-2 border-red-600';
    toast.innerHTML = `
      <span class="material-symbols-outlined text-sm animate-pulse">warning</span>
      <span>${mensaje}</span>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
    }, 5000);
  }

  // 📊 Mostrar resumen por severidad (Vista inicial)
  function mostrarResumenSeveridad(hallazgos) {
    // Contar por severidad
    const counts = {
      critical: hallazgos.filter(h => h.ml_severity === 'critical').length,
      high: hallazgos.filter(h => h.ml_severity === 'high').length,
      medium: hallazgos.filter(h => h.ml_severity === 'medium').length,
      low: hallazgos.filter(h => h.ml_severity === 'low').length,
    };

    console.log('[IA-CARD] Conteo por severidad:', counts);

    // Actualizar los contadores en cada card
    const countElements = {
      critical: document.getElementById('count-critical'),
      high: document.getElementById('count-high'),
      medium: document.getElementById('count-medium'),
      low: document.getElementById('count-low')
    };

    Object.keys(counts).forEach(severity => {
      if (countElements[severity]) {
        countElements[severity].textContent = counts[severity];
        
        // 🆕 Actualizar tendencias (primera carga = sin cambios)
        actualizarTendencia(severity, counts[severity], state.previousCounts[severity] || counts[severity]);
      }
    });

    // Guardar conteos para futuras comparaciones
    if (!state.previousCounts.critical) {
      state.previousCounts = { ...counts };
    }

    // Ocultar "no findings" si hay hallazgos
    const totalHallazgos = Object.values(counts).reduce((a, b) => a + b, 0);
    if (elements.noFindings) {
      elements.noFindings.classList.toggle('hidden', totalHallazgos > 0);
    }

    // Generar mensaje contextual dinámico
    actualizarMensajeContextual(counts);

    // Mostrar vista dashboard
    mostrarVista('dashboard');
  }

  // 💬 Actualizar mensaje contextual según hallazgos con datos enriquecidos
  function actualizarMensajeContextual(counts) {
    if (!elements.dashboardContextTitle || !elements.dashboardContextMessage) return;

    const totalHallazgos = Object.values(counts).reduce((a, b) => a + b, 0);

    if (totalHallazgos === 0) {
      // 🆕 Mensaje contextualizado por módulo cuando no hay problemas
      const moduloNombre = obtenerNombreModuloFiltrado();
      if (moduloNombre) {
        elements.dashboardContextTitle.innerHTML = `<span class="material-symbols-outlined text-green-500 dark:text-green-400 text-lg align-middle mr-1">check_circle</span>${moduloNombre}: Sistema saludable`;
        elements.dashboardContextMessage.textContent = `No se detectaron problemas en ${moduloNombre}. Todo está operando normalmente.`;
      } else {
        elements.dashboardContextTitle.innerHTML = '<span class="material-symbols-outlined text-green-500 dark:text-green-400 text-lg align-middle mr-1">check_circle</span>Sistema saludable';
        elements.dashboardContextMessage.textContent = 'No se detectaron problemas en este momento. El inventario está operando normalmente y todos los indicadores están en rangos óptimos.';
      }
      return;
    }

    // Obtener contexto específico del primer hallazgo de mayor severidad
    let contextoEspecifico = '';
    let hallazgoMasPrioritario = null;
    
    if (elements.mlHallazgos && elements.mlHallazgos.length > 0) {
      // Buscar el hallazgo de mayor severidad
      const prioridadSeveridad = { critical: 0, high: 1, medium: 2, low: 3 };
      hallazgoMasPrioritario = elements.mlHallazgos.reduce((prev, current) => {
        const prevPrio = prioridadSeveridad[prev.ml_severity] ?? 99;
        const currPrio = prioridadSeveridad[current.ml_severity] ?? 99;
        return currPrio < prevPrio ? current : prev;
      });

      contextoEspecifico = generarContextoEspecifico(hallazgoMasPrioritario);
    }

    // 🆕 Enriquecer mensaje con datos del contexto_adicional si existe
    let datosAdicionales = '';
    if (hallazgoMasPrioritario && hallazgoMasPrioritario.contexto_adicional) {
      const ctx = hallazgoMasPrioritario.contexto_adicional;
      const detalles = [];
      
      if (ctx.eventos_totales) detalles.push(`${ctx.eventos_totales} eventos`);
      if (ctx.usuarios_activos) detalles.push(`${ctx.usuarios_activos} usuarios activos`);
      if (ctx.pico_actividad) detalles.push(`Pico: ${ctx.pico_actividad}`);
      
      if (detalles.length > 0) {
        datosAdicionales = ` (${detalles.join(', ')})`;
      }
    }

    // 🆕 Enriquecer con métricas si existen
    let metricasInfo = '';
    if (hallazgoMasPrioritario && hallazgoMasPrioritario.metricas) {
      const metr = hallazgoMasPrioritario.metricas;
      if (metr.desviacion) {
        metricasInfo = ` Desviación: ${metr.desviacion}`;
      } else if (metr.anomaly_score !== undefined) {
        const scorePercent = Math.round(metr.anomaly_score * 100);
        metricasInfo = ` Score de anomalía: ${scorePercent}%`;
      }
    }

    // 🆕 Obtener nombre del módulo filtrado para contextualizar mensajes
    const moduloNombre = obtenerNombreModuloFiltrado();
    const prefijo = moduloNombre ? `${moduloNombre}: ` : '';

    // Generar mensaje priorizado según severidad más alta con hallazgos
    if (counts.critical > 0) {
      elements.dashboardContextTitle.innerHTML = `<span class="material-symbols-outlined text-red-500 dark:text-red-400 text-lg align-middle mr-1 animate-pulse">warning</span>${prefijo}Atención urgente detectada`;
      
      if (contextoEspecifico) {
        elements.dashboardContextMessage.textContent = `${contextoEspecifico}${datosAdicionales}${metricasInfo} Se detectaron ${counts.critical} problema${counts.critical > 1 ? 's' : ''} crítico${counts.critical > 1 ? 's' : ''} que requieren acción inmediata. Haz click en la tarjeta roja para revisar y resolver.`;
      } else {
        elements.dashboardContextMessage.textContent = `Se detectaron ${counts.critical} problema${counts.critical > 1 ? 's' : ''} crítico${counts.critical > 1 ? 's' : ''} que requieren acción inmediata${datosAdicionales}. Haz click en la tarjeta roja para revisar y resolver.`;
      }
    } else if (counts.high > 0) {
      elements.dashboardContextTitle.innerHTML = `<span class="material-symbols-outlined text-orange-500 dark:text-orange-400 text-lg align-middle mr-1">error</span>${prefijo}Advertencias detectadas`;
      
      if (contextoEspecifico) {
        elements.dashboardContextMessage.textContent = `${contextoEspecifico}${datosAdicionales}${metricasInfo} Se detectaron ${counts.high} advertencia${counts.high > 1 ? 's' : ''} que deberían atenderse pronto. Haz click en la tarjeta naranja para más detalles.`;
      } else {
        elements.dashboardContextMessage.textContent = `Se detectaron ${counts.high} advertencia${counts.high > 1 ? 's' : ''} que deberían atenderse pronto${datosAdicionales}. Haz click en la tarjeta naranja para más detalles.`;
      }
    } else if (counts.medium > 0) {
      elements.dashboardContextTitle.innerHTML = `<span class="material-symbols-outlined text-blue-500 dark:text-blue-400 text-lg align-middle mr-1">lightbulb</span>${prefijo}Oportunidades de mejora`;
      
      if (contextoEspecifico) {
        elements.dashboardContextMessage.textContent = `${contextoEspecifico}${datosAdicionales}${metricasInfo} Encontramos ${counts.medium} oportunidad${counts.medium > 1 ? 'es' : ''} para optimizar. Haz click en la tarjeta azul para explorar.`;
      } else {
        elements.dashboardContextMessage.textContent = `Encontramos ${counts.medium} oportunidad${counts.medium > 1 ? 'es' : ''} para optimizar${datosAdicionales}. Haz click en la tarjeta azul para explorar.`;
      }
    } else {
      elements.dashboardContextTitle.innerHTML = `<span class="material-symbols-outlined text-green-500 dark:text-green-400 text-lg align-middle mr-1">info</span>${prefijo}Información disponible`;
      
      if (contextoEspecifico) {
        elements.dashboardContextMessage.textContent = `${contextoEspecifico}${datosAdicionales} ${counts.low} elemento${counts.low > 1 ? 's' : ''} informativo${counts.low > 1 ? 's' : ''} disponible${counts.low > 1 ? 's' : ''}. Haz click en la tarjeta verde para revisar.`;
      } else {
        elements.dashboardContextMessage.textContent = `${counts.low} elemento${counts.low > 1 ? 's' : ''} informativo${counts.low > 1 ? 's' : ''} disponible${counts.low > 1 ? 's' : ''}${datosAdicionales}. Haz click en la tarjeta verde para revisar.`;
      }
    }
  }

  // 🆕 Obtener nombre del módulo filtrado actual
  function obtenerNombreModuloFiltrado() {
    if (!state.filterModule) return '';
    
    const nombresModulos = {
      'dashboard': 'Dashboard',
      'inventario': 'Inventario',
      'ventas': 'Ventas',
      'movimientos': 'Movimientos',
      'alertas': 'Alertas',
      'auditoria': 'Auditoría'
    };
    
    return nombresModulos[state.filterModule] || '';
  }

  // Generar contexto específico basado en el hallazgo
  function generarContextoEspecifico(hallazgo) {
    if (!hallazgo) return '';

    const modulo = hallazgo.modulo;
    const titulo = (hallazgo.titulo || '').toLowerCase();
    const descripcion = (hallazgo.descripcion || '').toLowerCase();

    // Contextos específicos por tipo de hallazgo
    if (modulo === 'inventario') {
      if (titulo.includes('stock cero') || titulo.includes('agotado')) {
        const productoMatch = hallazgo.titulo.match(/"([^"]+)"/);
        const producto = productoMatch ? productoMatch[1] : 'un producto';
        return `⚠️ STOCK CRÍTICO: ${producto} está completamente agotado, lo que impide ventas inmediatas.`;
      } else if (titulo.includes('sobrecarga') || titulo.includes('sobrecapacidad')) {
        return `⚖️ SOBREPESO: Se detectó exceso de capacidad que podría comprometer la estructura.`;
      } else if (titulo.includes('stock bajo')) {
        return `📦 REPOSICIÓN: Productos alcanzaron el punto de reorden.`;
      }
    } else if (modulo === 'ventas') {
      if (titulo.includes('alta demanda') || titulo.includes('líder')) {
        const productoMatch = hallazgo.titulo.match(/"([^"]+)"/);
        const producto = productoMatch ? productoMatch[1] : 'un producto';
        return `🏆 TOP VENTAS: ${producto} está liderando el catálogo.`;
      } else if (titulo.includes('baja rotación') || titulo.includes('caída')) {
        return `📉 BAJA DEMANDA: Productos con rotación muy inferior al promedio.`;
      }
    } else if (modulo === 'movimientos') {
      if (titulo.includes('anomalía') || titulo.includes('sin justificar')) {
        return `🔍 ANOMALÍA: Movimientos sin documentación adecuada detectados.`;
      } else if (titulo.includes('inactividad')) {
        return `⏱️ SIN ACTIVIDAD: Sistema sin registrar movimientos por tiempo prolongado.`;
      }
    } else if (modulo === 'alertas') {
      if (titulo.includes('crítica')) {
        return `🚨 ALERTAS ACTIVAS: Múltiples alertas críticas requieren atención.`;
      }
    } else if (modulo === 'auditoria') {
      if (titulo.includes('patrón') || titulo.includes('anómala')) {
        return `🛡️ COMPORTAMIENTO ATÍPICO: Usuario con patrones irregulares detectados.`;
      }
    }

    // Contexto genérico si no se identifica uno específico
    return '';
  }

  // Enriquecer descripción con datos de auditoría en tiempo real
  async function enriquecerDescripcionConAuditoria(hallazgo) {
    let descripcion = hallazgo.descripcion || 'Sin detalles disponibles';
    
    // Solo enriquecer si hay datos de auditoría disponibles
    if (typeof window.state !== 'undefined' && window.state.logs) {
      const logs = window.state.logs;
      const modulo = hallazgo.modulo;
      const ultimaHora = new Date(Date.now() - 60 * 60 * 1000);

      // Contar eventos relacionados en la última hora
      let eventosRelacionados = 0;
      let usuariosUnicos = new Set();
      
      // Mapeo de módulos a tipos de eventos de auditoría
      const moduloATipoEvento = {
        'inventario': ['movimientos_inventario', 'alertas_stock'],
        'ventas': ['ventas', 'detalle_ventas'],
        'movimientos': ['movimientos_inventario', 'retiros_programados', 'retiros_fuera_de_horario'],
        'alertas': ['alertas_sistema', 'alertas_stock', 'errores_criticos'],
        'auditoria': ['login_logout_usuarios', 'gestion_usuarios', 'modificacion_datos']
      };

      const tiposRelevantes = moduloATipoEvento[modulo] || [];

      // Analizar logs recientes
      logs.forEach(log => {
        const logDate = new Date(log.timestamp);
        if (logDate >= ultimaHora && tiposRelevantes.includes(log.tipo_evento)) {
          eventosRelacionados++;
          if (log.usuario && log.usuario !== 'Sistema') {
            usuariosUnicos.add(log.usuario);
          }
        }
      });

      // Enriquecer descripción con insights de comportamiento
      if (eventosRelacionados > 0) {
        const insights = [];
        
        if (eventosRelacionados >= 10) {
          insights.push(`Alta actividad detectada: ${eventosRelacionados} eventos en la última hora`);
        } else if (eventosRelacionados >= 5) {
          insights.push(`Actividad moderada: ${eventosRelacionados} eventos registrados`);
        }

        if (usuariosUnicos.size > 1) {
          insights.push(`${usuariosUnicos.size} usuarios involucrados: ${Array.from(usuariosUnicos).slice(0, 3).join(', ')}${usuariosUnicos.size > 3 ? '...' : ''}`);
        } else if (usuariosUnicos.size === 1) {
          insights.push(`Usuario responsable: ${Array.from(usuariosUnicos)[0]}`);
        }

        if (insights.length > 0) {
          descripcion += ` | 📊 ${insights.join('. ')}.`;
        }
      }

      // Insights específicos por módulo
      if (modulo === 'auditoria') {
        const loginEvents = logs.filter(log => 
          log.tipo_evento === 'login_logout_usuarios' && 
          new Date(log.timestamp) >= ultimaHora
        );
        
        if (loginEvents.length > 0) {
          const logins = loginEvents.filter(e => 
            (e.detalle || '').toLowerCase().includes('inic') || 
            (e.detalle || '').toLowerCase().includes('login')
          ).length;
          const logouts = loginEvents.filter(e => 
            (e.detalle || '').toLowerCase().includes('cerr') || 
            (e.detalle || '').toLowerCase().includes('logout')
          ).length;
          
          if (logins > logouts + 2) {
            descripcion += ` ⚠️ Patrón irregular: ${logins} inicios vs ${logouts} cierres de sesión.`;
          }
        }
      } else if (modulo === 'inventario') {
        const stockAlerts = logs.filter(log => 
          log.tipo_evento === 'alertas_stock' && 
          new Date(log.timestamp) >= ultimaHora
        );
        
        if (stockAlerts.length >= 3) {
          descripcion += ` 🚨 ${stockAlerts.length} alertas de stock generadas recientemente.`;
        }
      }
    }

    return descripcion;
  }

  // 🔄 Cambiar entre vistas (Dashboard ↔ Detalle)
  function mostrarVista(vista) {
    state.currentView = vista;
    
    // Ocultar todas las vistas
    if (elements.dashboardView) elements.dashboardView.classList.add('hidden');
    if (elements.detailView) elements.detailView.classList.add('hidden');
    
    // Mostrar la vista seleccionada
    if (vista === 'dashboard') {
      if (elements.dashboardView) elements.dashboardView.classList.remove('hidden');
      elements.mlNavigation.forEach(nav => nav.style.display = 'none');
    } else if (vista === 'detail') {
      if (elements.detailView) elements.detailView.classList.remove('hidden');
      elements.mlNavigation.forEach(nav => nav.style.display = 'flex');
      // Resetear pestañas a Contexto al entrar al detalle
      activarPestana('contexto');
    }
  }

  // 🎯 Filtrar y mostrar hallazgos por severidad
  function filtrarPorSeveridad(severity) {
    state.currentFilter = severity;
    
    // Filtrar por severidad Y por módulo si hay filtro activo
    let hallazgosFiltrados = elements.mlHallazgos.filter(h => h.ml_severity === severity);
    
    // Aplicar filtro de módulo si está activo
    if (state.filterModule) {
      hallazgosFiltrados = hallazgosFiltrados.filter(h => h.modulo === state.filterModule);
    }
    
    state.filteredHallazgos = hallazgosFiltrados;
    
    console.log(`[IA-CARD] Filtrando por ${severity}${state.filterModule ? ' en módulo ' + state.filterModule : ''}:`, state.filteredHallazgos.length, 'hallazgos');
    
    if (state.filteredHallazgos.length > 0) {
      // Actualizar breadcrumb
      const labels = { critical: 'Crítico', high: 'Advertencia', medium: 'Oportunidad', low: 'Información' };
      if (elements.breadcrumbSeverity) {
        elements.breadcrumbSeverity.textContent = labels[severity] || severity;
      }
      
      mostrarVista('detail');
      mostrarHallazgoFiltrado(0);
    } else {
      // Si no hay hallazgos con esos filtros, mostrar mensaje
      console.warn(`[IA-CARD] No se encontraron hallazgos con severidad ${severity}${state.filterModule ? ' en módulo ' + state.filterModule : ''}`);
    }
  }

  // 📄 Mostrar hallazgo del carrusel filtrado
  function mostrarHallazgoFiltrado(index) {
    const hallazgo = state.filteredHallazgos[index];
    if (!hallazgo) return;
    
    elements.currentHallazgoIndex = index;
    mostrarHallazgo(hallazgo, index, state.filteredHallazgos.length);
  }

  // Activar pestaña específica
  function activarPestana(tabName) {
    elements.tabs.forEach(tab => {
      const isActive = tab.dataset.tab === tabName;
      if (isActive) {
        tab.classList.add('ia-pro-tab-active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
        tab.classList.remove('border-transparent', 'text-gray-600', 'dark:text-white/60');
        tab.setAttribute('aria-selected', 'true');
      } else {
        tab.classList.remove('ia-pro-tab-active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
        tab.classList.add('border-transparent', 'text-gray-600', 'dark:text-white/60');
        tab.setAttribute('aria-selected', 'false');
      }
    });

    elements.panels.forEach(panel => {
      if (panel.id === `panel-${tabName}`) {
        panel.style.display = 'block';
        panel.classList.add('ia-pro-panel-active');
      } else {
        panel.style.display = 'none';
        panel.classList.remove('ia-pro-panel-active');
      }
    });
  }

  // 🎯 Mostrar hallazgo específico con datos enriquecidos
  async function mostrarHallazgo(hallazgo, index, total) {
    if (!hallazgo) return;

    console.log('[IA-CARD] Mostrando hallazgo:', hallazgo);

    // Actualizar título
    if (elements.title) elements.title.textContent = hallazgo.titulo || 'Hallazgo detectado';

    // Generar descripción enriquecida con datos de audit trail
    const descripcionEnriquecida = await enriquecerDescripcionConAuditoria(hallazgo);

    // ========== PESTAÑA 1: CONTEXTO ==========
    if (elements.message) elements.message.textContent = descripcionEnriquecida;

    // 🆕 Renderizar contexto adicional si existe
    if (hallazgo.contexto_adicional && elements.timestamp) {
      const ctx = hallazgo.contexto_adicional;
      
      // Timestamp de detección
      if (elements.timestamp) {
        elements.timestamp.textContent = ctx.timestamp_deteccion || 'Ahora';
      }
      
      // Módulo afectado con más detalles
      if (elements.moduloText) {
        const moduloInfo = [
          CONFIG.MODULE_LABELS[hallazgo.modulo] || hallazgo.modulo,
          ctx.periodo_analizado ? `(${ctx.periodo_analizado})` : ''
        ].filter(Boolean).join(' ');
        elements.moduloText.textContent = moduloInfo;
      }

      // Datos adicionales en mensaje (si hay espacio en UI)
      if (ctx.eventos_totales || ctx.pico_actividad) {
        const contextDetails = [];
        if (ctx.eventos_totales) contextDetails.push(`${ctx.eventos_totales} eventos`);
        if (ctx.eventos_por_hora) contextDetails.push(`${ctx.eventos_por_hora} eventos/hora`);
        if (ctx.pico_actividad) contextDetails.push(`Pico: ${ctx.pico_actividad}`);
        
        // Agregar al mensaje si hay contenedor adicional
        const additionalContext = document.querySelector('[data-context-details]');
        if (additionalContext && contextDetails.length > 0) {
          additionalContext.innerHTML = contextDetails.map(detail => 
            `<span class="text-xs text-gray-600 dark:text-white/60">${detail}</span>`
          ).join(' • ');
        }
      }
    }

    // Mostrar módulo afectado con navegación
    if (elements.moduleContainer && hallazgo.modulo) {
      elements.moduleContainer.style.display = 'block';
      const moduleBtn = elements.moduleContainer.querySelector('button');
      
      if (elements.moduleIcon) elements.moduleIcon.textContent = CONFIG.MODULE_ICONS[hallazgo.modulo] || 'dashboard';
      if (elements.moduleName) elements.moduleName.textContent = CONFIG.MODULE_LABELS[hallazgo.modulo] || hallazgo.modulo;
      
      // Hacer clickeable el badge de módulo
      if (moduleBtn) {
        moduleBtn.onclick = (e) => {
          e.preventDefault();
          const route = CONFIG.MODULE_ROUTES[hallazgo.modulo];
          if (route) {
            console.log('[IA-CARD] Navegando a:', route);
            window.location.href = route;
          }
        };
      }
    } else if (elements.moduleContainer) {
      elements.moduleContainer.style.display = 'none';
    }

    // ========== PESTAÑA 2: DIAGNÓSTICO ==========
    
    // 🆕 Renderizar métricas enriquecidas si existen
    if (hallazgo.metricas) {
      const metr = hallazgo.metricas;
      
      // Actualizar métricas específicas
      if (elements.metric1) {
        elements.metric1.textContent = metr.promedio_usuario 
          ? `Promedio: ${metr.promedio_usuario} eventos` 
          : calcularMetricasReales(hallazgo).metric1;
      }
      
      if (elements.metric2) {
        elements.metric2.textContent = metr.desviacion || calcularMetricasReales(hallazgo).metric2;
      }
      
      if (elements.metric3) {
        elements.metric3.textContent = metr.evento_principal || calcularMetricasReales(hallazgo).metric3;
      }

      // Mostrar tipo de eventos si existe
      if (metr.tipo_eventos && Object.keys(metr.tipo_eventos).length > 0) {
        const tipoEventosContainer = document.querySelector('[data-tipo-eventos]');
        if (tipoEventosContainer) {
          const topEvents = Object.entries(metr.tipo_eventos)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 3);
          
          tipoEventosContainer.innerHTML = topEvents.map(([tipo, count]) => 
            `<div class="flex justify-between items-center px-3 py-2 bg-gray-50 dark:bg-neutral-800 rounded">
              <span class="text-xs text-gray-700 dark:text-white/80">${tipo}</span>
              <span class="text-xs font-bold text-gray-900 dark:text-white">${count}</span>
            </div>`
          ).join('');
        }
      }

      // Score de anomalía ML
      if (elements.mlScore && metr.anomaly_score !== undefined) {
        const scorePercent = Math.round(metr.anomaly_score * 100);
        elements.mlScore.textContent = `${scorePercent}%`;
        
        // Barra de progreso visual
        const scoreBar = document.querySelector('[data-ml-score-bar]');
        if (scoreBar) {
          scoreBar.style.width = `${scorePercent}%`;
          scoreBar.style.backgroundColor = scorePercent > 70 ? '#ef4444' : scorePercent > 40 ? '#f59e0b' : '#10b981';
        }
      }
    } else {
      // Fallback a métricas calculadas
      const metrics = calcularMetricasReales(hallazgo);
      if (elements.metric1) elements.metric1.textContent = metrics.metric1;
      if (elements.metric2) elements.metric2.textContent = metrics.metric2;
      if (elements.metric3) elements.metric3.textContent = metrics.metric3;
    }

    // Actualizar análisis de impacto
    if (elements.impactAnalysis) {
      elements.impactAnalysis.textContent = `${hallazgo.descripcion || 'Evaluando impacto...'} Este evento podría afectar la operación del módulo ${CONFIG.MODULE_LABELS[hallazgo.modulo] || hallazgo.modulo}.`;
    }

    // Mostrar severidad con barra de progreso
    if (elements.severityDetail && hallazgo.ml_severity) {
      elements.severityDetail.style.display = 'block';
      const severityConfig = CONFIG.SEVERITY_CONFIG[hallazgo.ml_severity.toLowerCase()] || CONFIG.SEVERITY_CONFIG.medium;
      
      if (elements.severityText) {
        elements.severityText.textContent = severityConfig.label;
        elements.severityText.style.backgroundColor = `${severityConfig.color}20`;
        elements.severityText.style.color = severityConfig.color;
        elements.severityText.style.borderColor = `${severityConfig.color}40`;
      }
      
      if (elements.severityBadge) {
        elements.severityBadge.textContent = severityConfig.label;
        elements.severityBadge.style.backgroundColor = `${severityConfig.color}20`;
        elements.severityBadge.style.color = severityConfig.color;
        elements.severityBadge.style.borderColor = `${severityConfig.color}40`;
      }
      
      if (elements.severityBar) {
        elements.severityBar.style.backgroundColor = severityConfig.color;
        elements.severityBar.style.width = severityConfig.width;
      }
    } else if (elements.severityDetail) {
      elements.severityDetail.style.display = 'none';
    }

    // ========== PESTAÑA 3: RESOLUCIÓN ==========
    
    // 🆕 Usar pasos_accion enriquecidos si existen
    if (hallazgo.pasos_accion && Array.isArray(hallazgo.pasos_accion) && hallazgo.pasos_accion.length > 0) {
      if (elements.actionSteps) {
        elements.actionSteps.innerHTML = hallazgo.pasos_accion.map((paso) => {
          const hasRoute = paso.ruta && paso.ruta !== null;
          const urgenciaColor = paso.urgencia === 'alta' ? 'red' : paso.urgencia === 'media' ? 'orange' : 'blue';
          const urgenciaBadge = paso.urgencia 
            ? `<span class="text-[10px] px-2 py-0.5 rounded bg-${urgenciaColor}-100 dark:bg-${urgenciaColor}-500/20 text-${urgenciaColor}-600 dark:text-${urgenciaColor}-400 font-medium">${paso.urgencia.toUpperCase()}</span>`
            : '';
          
          const stepHTML = hasRoute 
            ? `<a href="${paso.ruta}" class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all cursor-pointer group">
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center text-xs font-bold">${paso.orden}</div>
                <div class="flex-1">
                  <p class="text-xs text-gray-700 dark:text-white/90 leading-relaxed">${paso.texto}</p>
                  ${urgenciaBadge}
                </div>
                <span class="material-symbols-outlined text-blue-500 dark:text-blue-400 text-base opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
              </a>`
            : `<div class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700">
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center text-xs font-bold">${paso.orden}</div>
                <div class="flex-1">
                  <p class="text-xs text-gray-700 dark:text-white/90 leading-relaxed">${paso.texto}</p>
                  ${urgenciaBadge}
                </div>
              </div>`;
          return stepHTML;
        }).join('');
      }
      
      // Actualizar solution text con resumen
      if (elements.solution) {
        elements.solution.textContent = hallazgo.plan_accion || 'Plan de acción definido en pasos siguientes.';
      }
    } else if (hallazgo.plan_accion) {
      // Fallback: generar pasos desde plan_accion (lógica antigua)
      if (elements.solution) {
        elements.solution.textContent = hallazgo.plan_accion;
      }
      
      if (elements.actionSteps) {
        const steps = generarPasosAccion(hallazgo.plan_accion, hallazgo);
        elements.actionSteps.innerHTML = steps.map((step, idx) => {
          const hasRoute = step.route && step.route !== null;
          const stepHTML = hasRoute 
            ? `<a href="${step.route}" class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-all cursor-pointer group">
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center text-xs font-bold">${idx + 1}</div>
                <p class="flex-1 text-xs text-gray-700 dark:text-white/90 leading-relaxed">${step.text}</p>
                <span class="material-symbols-outlined text-blue-500 dark:text-blue-400 text-base opacity-0 group-hover:opacity-100 transition-opacity">arrow_forward</span>
              </a>`
            : `<div class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700">
                <div class="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 text-white flex items-center justify-center text-xs font-bold">${idx + 1}</div>
                <p class="text-xs text-gray-700 dark:text-white/90 leading-relaxed">${step.text}</p>
              </div>`;
          return stepHTML;
        }).join('');
      }
    } else {
      if (elements.solution) elements.solution.textContent = 'Sin acciones sugeridas';
    }

    // Actualizar contador de navegación (múltiples ubicaciones)
    const currentIndex = index !== undefined ? index + 1 : 1;
    const totalCount = total !== undefined ? total : elements.mlHallazgos.length;
    
    elements.navCurrent.forEach(el => el.textContent = currentIndex);
    elements.navTotal.forEach(el => el.textContent = totalCount);

    // Actualizar estado de botones de navegación
    elements.navPrev.forEach(btn => btn.disabled = index === 0);
    elements.navNext.forEach(btn => btn.disabled = index === (total - 1));
  }

  // Calcular métricas reales basadas en el hallazgo
  function calcularMetricasReales(hallazgo) {
    const metrics = {
      metric1: '--',
      metric2: '--',
      metric3: '--'
    };

    if (!hallazgo) return metrics;

    const modulo = hallazgo.modulo;
    const severity = hallazgo.ml_severity;
    const descripcion = (hallazgo.descripcion || '').toLowerCase();
    const titulo = (hallazgo.titulo || '').toLowerCase();

    // Extraer números del texto usando regex
    const extractNumber = (text) => {
      const match = text.match(/(\d+(?:\.\d+)?)/);
      return match ? parseFloat(match[1]) : null;
    };

    // Métrica 1: Frecuencia/Cantidad
    const cantidad = extractNumber(descripcion) || extractNumber(titulo);
    if (cantidad !== null) {
      if (modulo === 'inventario' && titulo.includes('stock')) {
        metrics.metric1 = `${cantidad.toFixed(0)}u`;
      } else if (modulo === 'ventas') {
        metrics.metric1 = `${cantidad.toFixed(0)} unid.`;
      } else if (titulo.includes('hora') || titulo.includes('inactividad')) {
        metrics.metric1 = `${cantidad.toFixed(1)}h`;
      } else {
        metrics.metric1 = cantidad.toFixed(0);
      }
    } else {
      // Métrica por defecto según módulo
      if (modulo === 'dashboard') metrics.metric1 = 'Hoy';
      else if (modulo === 'inventario') metrics.metric1 = 'Stock';
      else if (modulo === 'ventas') metrics.metric1 = '48h';
      else if (modulo === 'movimientos') metrics.metric1 = 'Actual';
      else metrics.metric1 = 'N/A';
    }

    // Métrica 2: Impacto/Porcentaje
    const severityImpact = {
      critical: { percent: '95%', label: 'Crítico' },
      high: { percent: '75%', label: 'Alto' },
      medium: { percent: '50%', label: 'Medio' },
      low: { percent: '25%', label: 'Bajo' }
    };
    
    const impact = severityImpact[severity] || severityImpact.medium;
    
    // Buscar porcentajes explícitos en el texto
    const percentMatch = descripcion.match(/(\d+(?:\.\d+)?)\s*%/);
    if (percentMatch) {
      metrics.metric2 = `${parseFloat(percentMatch[1]).toFixed(0)}%`;
    } else {
      metrics.metric2 = impact.percent;
    }

    // Métrica 3: Estado/Categoría
    if (severity === 'critical') {
      metrics.metric3 = 'Urgente';
    } else if (severity === 'high') {
      metrics.metric3 = 'Atención';
    } else if (severity === 'medium') {
      metrics.metric3 = 'Revisar';
    } else {
      metrics.metric3 = 'Info';
    }

    // Ajustes contextuales por módulo
    if (modulo === 'inventario') {
      if (titulo.includes('agotado') || titulo.includes('stock cero')) {
        metrics.metric3 = 'Sin Stock';
      } else if (titulo.includes('sobrecarga') || titulo.includes('sobrecapacidad')) {
        metrics.metric3 = 'Exceso';
      } else if (titulo.includes('bajo')) {
        metrics.metric3 = 'Reorden';
      }
    } else if (modulo === 'ventas') {
      if (titulo.includes('alta demanda') || titulo.includes('líder')) {
        metrics.metric3 = 'Top';
      } else if (titulo.includes('baja rotación') || titulo.includes('caída')) {
        metrics.metric3 = 'Bajo';
      }
    } else if (modulo === 'movimientos') {
      if (titulo.includes('anomalía') || titulo.includes('sin justificar')) {
        metrics.metric3 = 'Revisar';
      } else if (titulo.includes('inactividad')) {
        metrics.metric3 = 'Parado';
      }
    }

    return metrics;
  }

  // Generar pasos de acción desde el plan con enlaces reales
  function generarPasosAccion(planAccion, hallazgo) {
    if (!planAccion) return [{ text: 'Procesando plan de acción...', route: null }];
    
    // Dividir por puntos o frases
    const sentences = planAccion.split(/\.|;/).filter(s => s.trim().length > 10).map(s => s.trim());
    
    // Si no hay pasos claros, generar pasos contextuales basados en el módulo
    if (sentences.length === 0 || sentences.length === 1) {
      return generarPasosContextuales(hallazgo, planAccion);
    }
    
    // Convertir cada paso en objeto con ruta potencial
    return sentences.slice(0, 5).map(step => {
      const route = detectarRutaEnPaso(step, hallazgo);
      return { text: step, route };
    });
  }

  // Generar pasos contextuales basados en el tipo de hallazgo
  function generarPasosContextuales(hallazgo, planOriginal) {
    const modulo = hallazgo.modulo;
    const severity = hallazgo.ml_severity;
    const steps = [];

    // Paso 1: Navegación al módulo
    steps.push({
      text: `Abrir módulo de ${CONFIG.MODULE_LABELS[modulo] || modulo}`,
      route: CONFIG.MODULE_ROUTES[modulo]
    });

    // Paso 2: Plan original o acción específica
    if (planOriginal && planOriginal.trim()) {
      steps.push({
        text: planOriginal.trim(),
        route: null
      });
    } else {
      steps.push({
        text: `Revisar ${severity === 'critical' ? 'urgentemente' : ''} los detalles del evento`,
        route: null
      });
    }

    // Paso 3: Acción específica por módulo
    if (modulo === 'inventario') {
      steps.push({
        text: 'Verificar niveles de stock y configurar alertas',
        route: '/inventario'
      });
    } else if (modulo === 'ventas') {
      steps.push({
        text: 'Analizar tendencias y patrones de venta',
        route: '/ventas'
      });
    } else if (modulo === 'movimientos') {
      steps.push({
        text: 'Revisar historial y justificar movimientos',
        route: '/movimientos'
      });
    } else if (modulo === 'alertas') {
      steps.push({
        text: 'Resolver alertas pendientes y configurar notificaciones',
        route: '/alertas'
      });
    } else if (modulo === 'auditoria') {
      steps.push({
        text: 'Revisar registros de auditoría y patrones de usuarios',
        route: '/auditoria'
      });
    }

    // Paso 4: Monitoreo continuo
    if (severity === 'critical' || severity === 'high') {
      steps.push({
        text: 'Documentar acciones tomadas y monitorear resultados',
        route: null
      });
    }

    return steps;
  }

  // Detectar rutas en el texto del paso
  function detectarRutaEnPaso(texto, hallazgo) {
    const textoLower = texto.toLowerCase();
    
    // Buscar palabras clave que indiquen navegación
    if (textoLower.includes('inventario') || textoLower.includes('stock')) {
      return '/inventario';
    } else if (textoLower.includes('venta') || textoLower.includes('ventas')) {
      return '/ventas';
    } else if (textoLower.includes('movimiento') || textoLower.includes('retiro')) {
      return '/movimientos';
    } else if (textoLower.includes('alerta')) {
      return '/alertas';
    } else if (textoLower.includes('auditor') || textoLower.includes('usuario')) {
      return '/auditoria';
    } else if (textoLower.includes('dashboard') || textoLower.includes('panel')) {
      return '/dashboard';
    }
    
    // Si no se detecta una ruta específica, usar la del módulo del hallazgo
    return null;
  }

  // 🎮 Configurar navegación
  function configurarNavegacion() {
    // Botón: Detail → Dashboard
    if (elements.btnBackToDashboard) {
      elements.btnBackToDashboard.addEventListener('click', () => {
        mostrarVista('dashboard');
      });
    }

    // Configurar clicks en cards de severidad (Dashboard → Detail)
    elements.severityCards.forEach(card => {
      card.addEventListener('click', () => {
        const severity = card.dataset.severityFilter;
        filtrarPorSeveridad(severity);
      });
    });

    // Configurar todos los botones prev
    elements.navPrev.forEach(btn => {
      btn.onclick = () => {
        const newIndex = Math.max(0, elements.currentHallazgoIndex - 1);
        mostrarHallazgoFiltrado(newIndex);
      };
    });

    // Configurar todos los botones next
    elements.navNext.forEach(btn => {
      btn.onclick = () => {
        const newIndex = Math.min(state.filteredHallazgos.length - 1, elements.currentHallazgoIndex + 1);
        mostrarHallazgoFiltrado(newIndex);
      };
    });

    // 🆕 Configurar filtros
    if (elements.filterModule) {
      elements.filterModule.addEventListener('change', (e) => {
        state.filterModule = e.target.value;
        aplicarFiltros();
      });
    }

    if (elements.clearFilters) {
      elements.clearFilters.addEventListener('click', () => {
        state.filterModule = '';
        if (elements.filterModule) elements.filterModule.value = '';
        aplicarFiltros();
      });
    }

    // Navegación con teclado
    elements.card.addEventListener('keydown', (e) => {
      if (state.currentView !== 'detail') return;
      
      if (e.key === 'ArrowLeft' && elements.currentHallazgoIndex > 0) {
        e.preventDefault();
        mostrarHallazgoFiltrado(elements.currentHallazgoIndex - 1);
      } else if (e.key === 'ArrowRight' && elements.currentHallazgoIndex < state.filteredHallazgos.length - 1) {
        e.preventDefault();
        mostrarHallazgoFiltrado(elements.currentHallazgoIndex + 1);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        if (state.currentView === 'detail') {
          mostrarVista('dashboard');
        }
      }
    });

    // 🆕 Keyboard shortcuts globales
    document.addEventListener('keydown', (e) => {
      // Question mark (?) para mostrar ayuda
      if (e.key === '?' || (e.shiftKey && e.key === '?')) {
        e.preventDefault();
        mostrarModalKeyboard();
      }

      // ESC para cerrar modal
      if (e.key === 'Escape' && elements.keyboardModal && !elements.keyboardModal.classList.contains('hidden')) {
        cerrarModalKeyboard();
      }
    });

    // 🆕 Configurar modal de atajos
    if (elements.keyboardHelpBtn) {
      elements.keyboardHelpBtn.addEventListener('click', (e) => {
        e.preventDefault();
        mostrarModalKeyboard();
      });
    }

    if (elements.keyboardModalClose) {
      elements.keyboardModalClose.addEventListener('click', cerrarModalKeyboard);
    }

    if (elements.keyboardModal) {
      elements.keyboardModal.addEventListener('click', (e) => {
        if (e.target === elements.keyboardModal) {
          cerrarModalKeyboard();
        }
      });
    }
  }

  // 🆕 Aplicar filtros por módulo
  function aplicarFiltros() {
    let hallazgosFiltrados = [...elements.mlHallazgos];

    // Filtrar por módulo
    if (state.filterModule) {
      hallazgosFiltrados = hallazgosFiltrados.filter(h => h.modulo === state.filterModule);
    }

    // Actualizar contadores visibles
    const countsFiltered = {
      critical: hallazgosFiltrados.filter(h => h.ml_severity === 'critical').length,
      high: hallazgosFiltrados.filter(h => h.ml_severity === 'high').length,
      medium: hallazgosFiltrados.filter(h => h.ml_severity === 'medium').length,
      low: hallazgosFiltrados.filter(h => h.ml_severity === 'low').length,
    };

    // Actualizar contadores
    Object.keys(countsFiltered).forEach(severity => {
      const el = document.getElementById(`count-${severity}`);
      if (el) el.textContent = countsFiltered[severity];
    });

    // Mostrar/ocultar "no findings"
    const total = Object.values(countsFiltered).reduce((a, b) => a + b, 0);
    if (elements.noFindings) {
      elements.noFindings.classList.toggle('hidden', total > 0);
    }

    // 🆕 Actualizar mensaje contextual con los conteos filtrados
    actualizarMensajeContextual(countsFiltered);
  }

  // 🆕 Mostrar modal de keyboard shortcuts
  function mostrarModalKeyboard() {
    if (elements.keyboardModal) {
      elements.keyboardModal.classList.remove('hidden');
      elements.keyboardModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
  }

  // 🆕 Cerrar modal de keyboard shortcuts
  function cerrarModalKeyboard() {
    if (elements.keyboardModal) {
      elements.keyboardModal.classList.add('hidden');
      elements.keyboardModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    }
  }

  // 🎨 Sistema de pestañas
  function configurarPestanas() {
    elements.tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const targetTab = tab.dataset.tab;
        
        // Actualizar tabs activas
        elements.tabs.forEach(t => {
          t.classList.remove('ia-pro-tab-active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
          t.classList.add('border-transparent', 'text-gray-600', 'dark:text-white/60');
          t.setAttribute('aria-selected', 'false');
        });
        
        tab.classList.add('ia-pro-tab-active', 'border-blue-500', 'text-blue-600', 'dark:text-blue-400');
        tab.classList.remove('border-transparent', 'text-gray-600', 'dark:text-white/60');
        tab.setAttribute('aria-selected', 'true');
        
        // Mostrar panel correspondiente
        elements.panels.forEach(panel => {
          if (panel.id === `panel-${targetTab}`) {
            panel.style.display = 'block';
            panel.classList.add('ia-pro-panel-active');
            
            // Animación de entrada
            panel.style.opacity = '0';
            panel.style.transform = 'translateY(10px)';
            setTimeout(() => {
              panel.style.transition = 'all 0.3s ease';
              panel.style.opacity = '1';
              panel.style.transform = 'translateY(0)';
            }, 10);
          } else {
            panel.style.display = 'none';
            panel.classList.remove('ia-pro-panel-active');
          }
        });
      });
    });
  }

  // 📡 Cargar recomendaciones
  async function cargarRecomendacion(contexto, { silent = false } = {}) {
    const url = `/api/recomendacion/${contexto}`;
    const requestId = ++state.requestId;

    // 🔄 Mostrar indicador discreto en actualizaciones silenciosas
    const silentIndicator = document.getElementById('silent-update-indicator');
    
    if (!silent) {
      setStatus('loading');
    } else if (silentIndicator) {
      silentIndicator.classList.remove('hidden');
    }

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
      
      // ✅ Ocultar indicador después de actualizar
      if (silent && silentIndicator) {
        setTimeout(() => {
          silentIndicator.classList.add('hidden');
        }, 1000);
      }
    } catch (err) {
      console.error('[IA] Error al cargar recomendación:', err);
      
      // Ocultar indicador en error
      if (silentIndicator) silentIndicator.classList.add('hidden');
      
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

  // ⏰ Auto-actualización inteligente (no invasiva)
  function iniciarAutoActualizacion(contexto) {
    if (state.timer) clearInterval(state.timer);
    
    // 🔄 Actualizar cada 2 minutos (más espaciado para mejor UX)
    state.timer = setInterval(() => {
      console.log('[IA-CARD] Auto-actualización en segundo plano...');
      
      // 🔕 Solo actualizar si el usuario NO está interactuando activamente
      // (ej: no ha movido el mouse en los últimos 5 segundos)
      const timeSinceLastActivity = Date.now() - (state.lastActivityTime || 0);
      
      if (timeSinceLastActivity > 5000 || state.currentView === 'dashboard') {
        cargarRecomendacion(contexto, { silent: true });
      } else {
        console.log('[IA-CARD] Usuario activo, posponiendo actualización...');
      }
    }, 120000); // 2 minutos en vez de 1
  }

  // 👁️ Tracking de actividad del usuario
  function trackearActividadUsuario() {
    const updateActivity = () => {
      state.lastActivityTime = Date.now();
    };
    
    // Trackear interacciones relevantes
    auditoriaCard.addEventListener('mousemove', updateActivity);
    auditoriaCard.addEventListener('click', updateActivity);
    auditoriaCard.addEventListener('scroll', updateActivity);
    
    // Trackear clicks en pestañas y navegación
    elements.tabs.forEach(tab => tab.addEventListener('click', updateActivity));
    elements.navPrev.forEach(btn => btn.addEventListener('click', updateActivity));
    elements.navNext.forEach(btn => btn.addEventListener('click', updateActivity));
  }

  // 🚀 Inicialización
  function inicializarAuditoria() {
    if (obtenerContexto() !== 'auditoria') return;

    // 👁️ Inicializar tracking de actividad
    trackearActividadUsuario();

    // Mostrar vista dashboard al cargar la página
    mostrarVista('dashboard');

    // Inicializar sistema de pestañas
    configurarPestanas();

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

  console.log('[IA-CARD-PRO] Sistema de pestañas inicializado correctamente');
})();