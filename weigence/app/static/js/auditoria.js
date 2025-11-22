// ===============================================================
//  AUDITORÍA · TERMINAL + LIVE TRAIL
// ===============================================================
(() => {
  const API_LOGS = "/api/auditoria/logs";
  const API_LIVE = "/api/auditoria/live-trail";
  const API_EXPORT = "/api/auditoria/export";
  const API_RECALIBRAR = "/api/auditoria/recalibrar";

  const REFRESH_INTERVAL = 10000; // 10 segundos para actualización casi en tiempo real

  // -----------------------------------------------------------
  //  ELEMENTOS
  // -----------------------------------------------------------
  const el = {
    terminal: document.getElementById("audit-terminal-output"),
    search: document.getElementById("audit-search"),
    runQuery: document.getElementById("audit-exec-query"),
    filters: document.getElementById("audit-active-filters"),
    logStream: document.getElementById("audit-log-stream"),
    empty: document.getElementById("audit-log-empty"),
    streamStatus: document.getElementById("audit-stream-status"),
    lastUpdated: document.getElementById("audit-last-updated"),
    mem: document.getElementById("audit-mem-usage"),
    cpu: document.getElementById("audit-cpu-usage"),
    latency: document.getElementById("audit-latency"),
    exportCsv: document.getElementById("audit-export-csv"),
    exportCsvFooter: document.getElementById("audit-export-csv-footer"),
    exportZip: document.getElementById("audit-export-zip"),
    exportPdf: document.getElementById("audit-export-pdf"),
    filterUser: document.getElementById("audit-filter-user"),
    currentUserDisplay: document.getElementById("current-user-display"),
    activeUsers: document.getElementById("audit-active-users"),
    activeUserCount: document.getElementById("active-user-count"),
    clearFilters: document.getElementById("audit-clear-filters"),
    filterToday: document.getElementById("audit-filter-today"),
    filterWeek: document.getElementById("audit-filter-week"),
    filterMonth: document.getElementById("audit-filter-month"),
  };
  
  let state = {
    filtros: {},
    logs: [],
    currentUser: null,
    renderedLogIds: new Set(), // IDs de logs ya renderizados
    horasRango: 24, // Horas hacia atrás para cargar logs (por defecto 24h = hoy)
    filtroTemporalActivo: false, // Indica si se aplicó un filtro temporal explícito
  };

  // ===========================================================
  //  NORMALIZADORES & CATEGORÍAS
  // ===========================================================
  const CATEGORIAS = {
    login_logout_usuarios: { sigla: "AUTH", color: "#3b82f6", nombre: "Autenticación" },
    ventas: { sigla: "VENTA", color: "#10b981", nombre: "Ventas" },
    detalle_ventas: { sigla: "PROD", color: "#06b6d4", nombre: "Productos" },
    movimientos_inventario: { sigla: "INVT", color: "#f59e0b", nombre: "Inventario" },
    retiros_programados: { sigla: "RETIRO", color: "#f59e0b", nombre: "Retiros" },
    retiros_fuera_de_horario: { sigla: "RETIRO", color: "#ef4444", nombre: "Retiros" },
    errores_criticos: { sigla: "ERR", color: "#dc2626", nombre: "Errores" },
    alertas_sistema: { sigla: "ALRT", color: "#ef4444", nombre: "Alertas" },
    alertas_stock: { sigla: "STOCK", color: "#f59e0b", nombre: "Stock" },
    otros: { sigla: "INFO", color: "#6b7280", nombre: "Otros" }
  };

  const sev = {
    info: { label: "INFO", class: "text-green-400" },
    warning: { label: "WARN", class: "text-yellow-400" },
    critical: { label: "CRIT", class: "text-red-500" },
    error: { label: "CRIT", class: "text-red-500" },
  };

  function normalize(entry) {
    let fechaFormateada = "";
    let hora = "";
    
    try {
      // El backend envía timestamps en UTC, convertir a hora local de Chile
      const timestampUTC = new Date(entry.timestamp);
      
      // Convertir a timezone de Chile (UTC-3 o UTC-4 según DST)
      const formatter = new Intl.DateTimeFormat('es-CL', {
        timeZone: 'America/Santiago',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
      
      const dateFormatter = new Intl.DateTimeFormat('es-CL', {
        timeZone: 'America/Santiago',
        day: '2-digit',
        month: '2-digit',
        year: '2-digit'
      });
      
      hora = formatter.format(timestampUTC);
      fechaFormateada = dateFormatter.format(timestampUTC);
    } catch (e) {
      // Fallback
      fechaFormateada = entry.fecha || entry.timestamp.slice(0, 10);
      hora = entry.hora || entry.timestamp.slice(11, 19);
    }
    
    const nivel = (entry.severidad || "info").toLowerCase();
    const preset = sev[nivel] || sev.info;

    return {
      id: entry.id,
      fecha: fechaFormateada,
      hora: hora,
      timestamp: entry.timestamp,
      mensaje: entry.mensaje,
      detalle: entry.detalle || entry.mensaje,
      usuario: entry.usuario || 'Sistema',
      rut: entry.rut || 'N/A',
      producto: entry.producto,
      estante: entry.estante,
      tipo_evento: entry.tipo_evento,
      nivel: preset.label,
      nivelClass: preset.class,
    };
  }

  // ===========================================================
  //  TERMINAL SUPERIOR
  // ===========================================================
  function pushTerminal(msg) {
      if (!el.terminal) return;
      const p = document.createElement("p");
      p.textContent = msg;
      el.terminal.appendChild(p);
      el.terminal.scrollTop = el.terminal.scrollHeight;
  }

  // ===========================================================
  //  LIVE AUDIT TRAIL - TERMINAL MEJORADA
  // ===========================================================
  function logColor(level) {
    const l = level.toUpperCase();
    if (l === "INFO")  return "#10b981"; // verde
    if (l === "WARN")  return "#f59e0b"; // amarillo
    if (l === "CRIT")  return "#ef4444"; // rojo
    return "#94a3b8"; // gris
  }

  function getCategoriaInfo(tipo) {
    return CATEGORIAS[tipo] || CATEGORIAS['otros'];
  }

  function formatearMensajeRico(log) {
    // Usar el detalle completo que viene del backend
    const usuario = log.usuario || 'Sistema';
    const rut = log.rut && log.rut !== 'N/A' && log.rut !== 'Sistema' ? log.rut : null;
    const producto = log.producto || '';
    const estante = log.estante || '';
    const detalles = log.detalle || log.mensaje || '';
    
    let resultado = '';
    // Usuario con estilo badge simple (sin RUT inline)
    const usuarioMarcado = `<span class="user-highlight">${usuario}</span>`;
    
    switch(log.tipo_evento) {
      case 'login_logout_usuarios':
        // Detectar si es login o logout basándose en el detalle
        const esLogout = detalles.toLowerCase().includes('cerr') || 
                         detalles.toLowerCase().includes('salió') || 
                         detalles.toLowerCase().includes('logout');
        const esLogin = detalles.toLowerCase().includes('inic') || 
                        detalles.toLowerCase().includes('login') ||
                        detalles.toLowerCase().includes('ingres');
        
        if (esLogout) {
          resultado = `<span style="color: #ef4444;">🚪</span> ${usuarioMarcado} <span style="color: #f87171;">cerró sesión</span>`;
        } else if (esLogin) {
          resultado = `<span style="color: #10b981;">🔓</span> ${usuarioMarcado} <span style="color: #34d399;">inició sesión</span>`;
        } else if (detalles) {
          resultado = detalles.replace(usuario, usuarioMarcado);
        } else {
          resultado = `${usuarioMarcado} - Autenticación`;
        }
        break;
        
      case 'ventas':
        // Usar detalle completo del backend con ícono de venta
        resultado = detalles ? `<span style="color: #10b981;">💰</span> ${detalles.replace(usuario, usuarioMarcado)}` : `<span style="color: #10b981;">💰</span> ${usuarioMarcado} - Venta`;
        break;
        
      case 'detalle_ventas':
        const cantMatch = detalles.match(/(\d+)u/);
        const cant = cantMatch ? cantMatch[1] : '';
        resultado = `<span style="color: #06b6d4;">📦</span> ${cant}u ${producto || 'producto'}`;
        break;
      
      case 'movimientos_inventario':
      case 'retiros_programados':
      case 'retiros_fuera_de_horario':
        // Usar detalle completo del backend si existe
        resultado = detalles ? detalles.replace(usuario, usuarioMarcado) : `${usuarioMarcado} - ${producto || 'Movimiento'} ${estante ? '@' + estante : ''}`;
        break;
        
      case 'alertas_sistema':
      case 'alertas_stock':
        // Hacer más descriptivas las alertas mostrando el detalle completo
        if (detalles) {
          // Si es alerta de stock, mostrar producto y detalles
          if (producto && (detalles.toLowerCase().includes('stock') || detalles.toLowerCase().includes('bajo') || detalles.toLowerCase().includes('agotado'))) {
            resultado = `⚠️ ${producto}: ${detalles}`;
          } else {
            resultado = `⚠️ ${detalles}${estante ? ' @' + estante : ''}`;
          }
        } else {
          resultado = `⚠️ ALERTA${producto ? ' - ' + producto : ''}${estante ? ' @' + estante : ''}`;
        }
        break;
        
      case 'errores_criticos':
        resultado = `❌ ${detalles.substring(0, 50)}`;
        break;
        
      default:
        resultado = detalles ? detalles.replace(usuario, usuarioMarcado) : usuarioMarcado;
    }
    
    // Truncar a 90 caracteres máximo (sin contar tags HTML)
    const textoSinHTML = resultado.replace(/<[^>]*>/g, '');
    if (textoSinHTML.length > 90) {
      const diferencia = resultado.length - textoSinHTML.length;
      resultado = resultado.substring(0, 87 + diferencia) + '...';
    }
    
    return resultado.trim();
  }

  function renderLogs() {
    const cont = el.logStream;
    if (!cont) return;

    if (!state.logs.length) {
      el.empty.classList.remove("hidden");
      updateStats({ info: 0, warn: 0, crit: 0 });
      state.renderedLogIds.clear();
      cont.innerHTML = "";
      return;
    }

    el.empty.classList.add("hidden");

    // Calcular estadísticas
    const stats = { info: 0, warn: 0, crit: 0 };
    state.logs.forEach(log => {
      const nivel = log.nivel.toLowerCase();
      if (nivel === 'info') stats.info++;
      else if (nivel === 'warn') stats.warn++;
      else if (nivel === 'crit') stats.crit++;
    });
    updateStats(stats);

    // Ordenar: más recientes al final (orden cronológico ascendente)
    const ordered = [...state.logs].sort((a, b) => {
      const timeA = new Date(a.timestamp || 0).getTime();
      const timeB = new Date(b.timestamp || 0).getTime();
      return timeA - timeB; // Ascendente: más antiguos primero, más nuevos al final
    });

    // Detectar si el usuario está en el fondo (para mantener scroll automático)
    const isAtBottom = cont.scrollHeight - cont.scrollTop - cont.clientHeight < 100;

    // Detectar logs nuevos
    const nuevosLogIds = new Set();
    let cantidadNuevos = 0;
    ordered.forEach(log => {
      const logId = `${log.timestamp}_${log.tipo_evento}_${log.detalle.substring(0, 20)}`;
      if (!state.renderedLogIds.has(logId)) {
        nuevosLogIds.add(logId);
        state.renderedLogIds.add(logId);
        cantidadNuevos++;
      }
    });

    // Mostrar notificación de nuevos eventos (solo si hay más de 2 nuevos)
    if (cantidadNuevos > 2) {
      showNotification(`${cantidadNuevos} nuevos eventos`, "info");
      
      // Parpadeo en el indicador de estado
      if (el.streamStatus) {
        el.streamStatus.style.animation = 'none';
        setTimeout(() => {
          el.streamStatus.style.animation = 'pulse-glow 2s ease-in-out infinite';
        }, 100);
      }
    }

    // Reconstruir todo el contenedor para mantener orden correcto
    cont.innerHTML = "";

    // Variable para rastrear la última fecha mostrada
    let lastDate = null;
    const hoy = new Date().toLocaleDateString('es-CL', { timeZone: 'America/Santiago' });

    // Renderizar todos los logs
    ordered.forEach((log, index) => {
      const logId = `${log.timestamp}_${log.tipo_evento}_${log.detalle.substring(0, 20)}`;
      const esNuevo = nuevosLogIds.has(logId);
      
      // Obtener fecha del log
      const logDate = new Date(log.timestamp).toLocaleDateString('es-CL', { timeZone: 'America/Santiago' });
      
      // Insertar separador de fecha si es diferente a la anterior
      if (logDate !== lastDate) {
        const separator = document.createElement("div");
        separator.className = "date-separator";
        separator.style.cssText = `
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 0px;
          margin: 0px;
          height: 20px;
          font-family: 'Roboto', sans-serif;
          font-size: 9px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.3px;
        `;
        
        const dateLabel = logDate === hoy ? 'HOY' : logDate;
        const dateColor = logDate === hoy ? '#3b82f6' : '#6b7280';
        
        separator.innerHTML = `
          <div style="flex: 1; height: 1px; background: ${dateColor}20;"></div>
          <span style="color: ${dateColor};">${dateLabel}</span>
          <div style="flex: 1; height: 1px; background: ${dateColor}20;"></div>
        `;
        
        cont.appendChild(separator);
        lastDate = logDate;
      }
      
      const categoria = getCategoriaInfo(log.tipo_evento);
      const severidadColor = logColor(log.nivel);
      
      // Ajustar color del badge según tipo específico de evento
      let badgeColor = categoria.color;
      let borderColor = categoria.color;
      let badgeText = categoria.sigla;
      
      // LOGIN/LOGOUT: Colores distintivos
      if (log.tipo_evento === 'login_logout_usuarios') {
        const detalles = log.detalle || log.mensaje || '';
        const esLogout = detalles.toLowerCase().includes('cerr') || 
                         detalles.toLowerCase().includes('salió') || 
                         detalles.toLowerCase().includes('logout');
        const esLogin = detalles.toLowerCase().includes('inic') || 
                        detalles.toLowerCase().includes('login') ||
                        detalles.toLowerCase().includes('ingres');
        
        if (esLogout) {
          badgeColor = '#ef4444'; // rojo para logout
          borderColor = '#ef4444';
          badgeText = 'OUT';
        } else if (esLogin) {
          badgeColor = '#10b981'; // verde para login
          borderColor = '#10b981';
          badgeText = 'IN';
        }
      }
      // GESTIÓN DE USUARIOS: Colores según acción
      else if (log.tipo_evento === 'gestion_usuarios' || log.tipo_evento === 'modificacion_datos') {
        const detalles = log.detalle || log.mensaje || '';
        if (detalles.toLowerCase().includes('cre')) {
          badgeColor = '#10b981'; // verde para crear
          borderColor = '#10b981';
        } else if (detalles.toLowerCase().includes('elimin')) {
          badgeColor = '#ef4444'; // rojo para eliminar
          borderColor = '#ef4444';
        } else if (detalles.toLowerCase().includes('edit')) {
          badgeColor = '#3b82f6'; // azul para editar
          borderColor = '#3b82f6';
        }
      }
      // ALERTAS DE STOCK: Color según severidad
      else if (log.tipo_evento === 'alertas_stock') {
        if (log.nivel === 'CRIT') {
          badgeColor = '#ef4444'; // rojo
          borderColor = '#ef4444';
        } else if (log.nivel === 'WARN') {
          badgeColor = '#f59e0b'; // amarillo
          borderColor = '#f59e0b';
        }
      }
      // RETIROS FUERA DE HORARIO: Color rojo
      else if (log.tipo_evento === 'retiros_fuera_de_horario') {
        badgeColor = '#ef4444';
        borderColor = '#ef4444';
      }
      
      // Mensaje con formato HTML enriquecido
      const msg = formatearMensajeRico(log);

      const line = document.createElement("div");
      line.className = "log-entry bg-black/[0.04] dark:bg-white/[0.05] text-slate-950 dark:text-gray-100 hover:bg-blue-500/10 dark:hover:bg-blue-500/12 transition-all duration-150";
      
      line.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        margin-bottom: 2px;
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 13.5px;
        line-height: 1.5;
        cursor: pointer;
        border-left: 3px solid ${borderColor};
        border-radius: 4px;
        ${esNuevo ? 'opacity: 0; transform: translateY(10px); transition: opacity 0.5s ease-out, transform 0.5s ease-out;' : ''}
      `;
      
      line.innerHTML = `
        <span class="text-slate-800 dark:text-gray-200" style="min-width: 70px; flex-shrink: 0; font-size: 13px; font-weight: 700; font-family: 'Roboto Mono', 'Consolas', monospace; letter-spacing: -0.3px;">${log.hora}</span>
        <span style="
          background: ${badgeColor}15; 
          color: ${badgeColor}; 
          border: 1.5px solid ${badgeColor};
          padding: 5px 10px;
          border-radius: 4px;
          font-size: 10.5px;
          font-weight: 800;
          min-width: 52px;
          text-align: center;
          flex-shrink: 0;
          letter-spacing: 0.8px;
          font-family: 'Roboto Mono', 'Consolas', monospace;
          text-transform: uppercase;
        ">${badgeText}</span>
        <span class="text-slate-900 dark:text-gray-50" style="flex: 1; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; letter-spacing: -0.1px;">${msg}</span>
      `;

      line.onmouseenter = () => {
        line.style.borderLeftWidth = '4px';
        line.style.transform = 'translateX(4px) scale(1.01)';
        line.style.boxShadow = '0 4px 16px rgba(0,0,0,0.15)';
        line.style.background = 'rgba(59, 130, 246, 0.08)';
      };
      
      line.onmouseleave = () => {
        line.style.borderLeftWidth = '3px';
        line.style.transform = 'translateX(0) scale(1)';
        line.style.boxShadow = 'none';
        line.style.background = '';
      };

      line.onclick = (e) => {
        // Prevenir propagación
        e.stopPropagation();
        
        console.log('🖱️ Click en log:', {
          tipo: log.tipo_evento,
          usuario: log.usuario,
          hora: log.hora,
          detalle: log.detalle
        });
        
        // Efecto ripple al hacer clic
        const ripple = document.createElement("span");
        ripple.style.cssText = `
          position: absolute;
          border-radius: 50%;
          background: rgba(59, 130, 246, 0.4);
          width: 20px;
          height: 20px;
          margin-left: -10px;
          margin-top: -10px;
          animation: ripple 0.6s;
          pointer-events: none;
        `;
        const rect = line.getBoundingClientRect();
        ripple.style.left = e.clientX - rect.left + 'px';
        ripple.style.top = e.clientY - rect.top + 'px';
        line.style.position = 'relative';
        line.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
        
        // Mostrar el modal con los detalles
        try {
          mostrarDetalleLog(log);
        } catch (error) {
          console.error('❌ Error mostrando detalle del log:', error);
          showNotification('Error al mostrar detalles', 'error');
        }
      };

      cont.appendChild(line); // Insertar al final para que los más recientes queden abajo
      
      // Activar animación fade-in solo para mensajes nuevos
      if (esNuevo) {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            line.style.opacity = '1';
            line.style.transform = 'translateY(0)';
          });
        });
      }
    });

    // Auto-scroll: Siempre mantener el scroll al fondo para mostrar los más recientes
    requestAnimationFrame(() => {
      cont.scrollTop = cont.scrollHeight;
    });
  }

  function updateStats(stats) {
    const statInfo = document.getElementById('stat-info');
    const statWarn = document.getElementById('stat-warn');
    const statCrit = document.getElementById('stat-crit');
    
    if (statInfo) statInfo.textContent = stats.info;
    if (statWarn) statWarn.textContent = stats.warn;
    if (statCrit) statCrit.textContent = stats.crit;
  }

  function mostrarDetalleLog(log) {
    console.log('📋 Mostrando detalle de log:', log);
    
    const categoria = getCategoriaInfo(log.tipo_evento);
    const severidadColor = logColor(log.nivel);
    
    const modal = document.createElement("div");
    modal.className = "fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4";
    modal.style.animation = "fadeIn 0.2s ease-out";
    
    modal.innerHTML = `
      <div class="bg-gradient-to-br from-white to-neutral-50 dark:from-gray-900 dark:to-gray-800 border-2 border-neutral-300 dark:border-gray-700 rounded-xl max-w-3xl w-full p-8 space-y-5 shadow-2xl" style="animation: slideUp 0.3s ease-out;">
        <div class="flex items-center justify-between border-b border-neutral-300 dark:border-gray-700 pb-4">
          <div class="flex items-center gap-4">
            <div style="
              background: ${categoria.color}20; 
              color: ${categoria.color}; 
              border: 2px solid ${categoria.color};
              padding: 8px 12px;
              border-radius: 6px;
              font-size: 11px;
              font-weight: 700;
              letter-spacing: 1px;
            ">${categoria.sigla}</div>
            <div>
              <h3 class="text-neutral-900 dark:text-white font-bold text-xl">${categoria.nombre}</h3>
              <p class="text-neutral-600 dark:text-gray-400 text-sm font-mono">${log.fecha} · ${log.hora}</p>
            </div>
          </div>
          <button class="close-modal-btn text-neutral-600 dark:text-gray-400 hover:text-neutral-900 dark:hover:text-white transition-colors text-2xl font-bold">
            ✕
          </button>
        </div>
        
        <div class="grid grid-cols-2 gap-4">
          <div class="${log.rut && log.rut !== 'N/A' && log.rut !== 'Sistema' ? '' : 'col-span-2'}">
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Usuario</p>
            <p class="text-neutral-900 dark:text-white bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 font-semibold text-base">${log.usuario}</p>
          </div>
          
          ${log.rut && log.rut !== 'N/A' && log.rut !== 'Sistema' ? `
          <div>
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">RUT</p>
            <p class="text-blue-600 dark:text-blue-400 bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 font-mono text-base font-bold">${log.rut}</p>
          </div>
          ` : ''}
          
          <div>
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Nivel</p>
            <div style="
              background: ${severidadColor}20; 
              color: ${severidadColor}; 
              border: 2px solid ${severidadColor};
              padding: 10px;
              border-radius: 8px;
              font-weight: 700;
              text-align: center;
              font-size: 14px;
            ">${log.nivel}</div>
          </div>
          
          ${log.producto ? `
            <div class="col-span-2">
              <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Producto</p>
              <p class="text-green-600 dark:text-green-400 bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 font-semibold text-base">${log.producto}</p>
            </div>
          ` : ''}
          
          ${log.estante ? `
            <div class="col-span-2">
              <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Ubicación/Estante</p>
              <p class="text-purple-600 dark:text-purple-400 bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 font-semibold text-base">${log.estante}</p>
            </div>
          ` : ''}
          
          <div class="col-span-2">
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Detalles del Evento</p>
            <p class="text-neutral-900 dark:text-white bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-4 font-mono text-sm leading-relaxed">${log.detalle || log.mensaje}</p>
          </div>
          
          <div>
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">Tipo de Evento</p>
            <p class="text-neutral-800 dark:text-gray-300 bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 text-sm">${log.tipo_evento}</p>
          </div>
          
          <div>
            <p class="text-neutral-600 dark:text-gray-400 text-xs uppercase tracking-wider mb-2 font-semibold">ID Evento</p>
            <p class="text-neutral-500 dark:text-gray-500 bg-neutral-100 dark:bg-gray-800 border border-neutral-300 dark:border-gray-700 rounded-lg p-3 font-mono text-xs">#${log.id}</p>
          </div>
        </div>
        
        <button class="close-modal-btn w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-bold text-base transition-all transform hover:scale-[1.02] active:scale-[0.98]">
          CERRAR
        </button>
      </div>
    `;
    
    // Agregar animaciones CSS si no existen
    if (!document.getElementById('modal-animations')) {
      const style = document.createElement('style');
      style.id = 'modal-animations';
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from { 
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to { 
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    // Event listeners para cerrar el modal
    const closeButtons = modal.querySelectorAll('.close-modal-btn');
    closeButtons.forEach(btn => {
      btn.onclick = (e) => {
        e.stopPropagation();
        modal.style.animation = "fadeOut 0.2s ease-in";
        setTimeout(() => modal.remove(), 200);
      };
    });
    
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.style.animation = "fadeOut 0.2s ease-in";
        setTimeout(() => modal.remove(), 200);
      }
    });
    
    // Agregar animación de fadeOut
    if (!document.getElementById('fadeout-animation')) {
      const style = document.createElement('style');
      style.id = 'fadeout-animation';
      style.textContent = `
        @keyframes fadeOut {
          from { opacity: 1; }
          to { opacity: 0; }
        }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
    console.log('✅ Modal de detalles creado y agregado al DOM');
  }

  // ===========================================================
  //  CARGA DE LOGS CON FEEDBACK MEJORADO
  // ===========================================================
  async function loadLogs() {
    // Indicador de carga
    if (el.streamStatus) {
      el.streamStatus.classList.remove('bg-green-500');
      el.streamStatus.classList.add('bg-yellow-500');
    }
    if (el.lastUpdated) {
      el.lastUpdated.textContent = "Sincronizando...";
    }

    const params = new URLSearchParams(state.filtros);
    params.set('horas', state.horasRango);
    
    // Ajustar el límite según el rango temporal
    // Más días = más eventos posibles
    let limit = 200; // Default para 24h
    if (state.horasRango >= 720) limit = 1000; // Mes: 1000 eventos
    else if (state.horasRango >= 168) limit = 500; // Semana: 500 eventos
    params.set('limit', limit);
    
    const url = `${API_LOGS}?${params.toString()}`;

    try {
      const startTime = Date.now();
      const res = await fetch(url);
      
      if (!res.ok) {
        console.error(`Error HTTP ${res.status}: ${res.statusText}`);
        if (el.streamStatus) {
          el.streamStatus.classList.remove('bg-yellow-500', 'bg-green-500');
          el.streamStatus.classList.add('bg-red-500');
        }
        if (el.lastUpdated) {
          el.lastUpdated.textContent = `Error ${res.status}`;
        }
        return;
      }
      
      const data = await res.json();
      const loadTime = Date.now() - startTime;

      if (!data.ok) {
        console.error("Error en backend:", data.error || "Error desconocido");
        if (el.streamStatus) {
          el.streamStatus.classList.remove('bg-yellow-500', 'bg-green-500');
          el.streamStatus.classList.add('bg-red-500');
        }
        if (el.lastUpdated) {
          el.lastUpdated.textContent = data.error ? `Error: ${data.error.substring(0, 30)}...` : "Error backend";
        }
        
        // Mostrar logs vacíos si hay error
        state.logs = [];
        renderLogs();
        return;
      }

      state.logs = data.logs.map(normalize);

      // Actualizar métricas del sistema
      if (data.meta?.system) {
        if (el.mem) el.mem.textContent = data.meta.system.mem || "--";
        if (el.cpu) el.cpu.textContent = data.meta.system.cpu || "--";
        if (el.latency) el.latency.textContent = `${loadTime}ms`;
      }

      // Actualizar contador de usuarios activos
      detectCurrentUser();
      updateActiveUserCount();

      // Actualizar estado
      if (el.streamStatus) {
        el.streamStatus.classList.remove('bg-yellow-500');
        el.streamStatus.classList.add('bg-green-500');
      }
      
      const now = new Date();
      if (el.lastUpdated) {
        el.lastUpdated.textContent = `${now.toLocaleTimeString('es-CL')}`;
      }

      renderLogs();

    } catch (err) {
      console.error("Fallo conexión backend:", err);
      
      if (el.streamStatus) {
        el.streamStatus.classList.remove('bg-yellow-500', 'bg-green-500');
        el.streamStatus.classList.add('bg-red-500');
      }
      if (el.lastUpdated) {
        el.lastUpdated.textContent = "Error de conexión";
      }
    }
  }

  // Notificaciones toast con animación mejorada
  function showNotification(message, type = "info") {
    const colors = {
      success: "bg-green-500",
      error: "bg-red-500",
      info: "bg-blue-500",
      warning: "bg-yellow-500"
    };

    const icons = {
      success: "check_circle",
      error: "error",
      info: "info",
      warning: "warning"
    };

    const toast = document.createElement("div");
    toast.className = `fixed bottom-4 right-4 ${colors[type]} text-white px-5 py-3 rounded-lg shadow-2xl z-50 text-sm font-medium flex items-center gap-3`;
    toast.style.animation = "slideInRight 0.4s cubic-bezier(0.4, 0, 0.2, 1)";
    toast.innerHTML = `
      <span class="material-symbols-outlined text-xl">${icons[type]}</span>
      <span>${message}</span>
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = "slideOutRight 0.3s ease-in";
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // ===========================================================
  //  FILTROS INTELIGENTES
  // ===========================================================
  function parseSearchQuery(query) {
    const filtros = {};
    
    // Parsear formato: key:value key2:value2
    const regex = /(\w+):([^\s]+)/g;
    let match;
    
    while ((match = regex.exec(query)) !== null) {
      filtros[match[1]] = match[2];
    }
    
    return filtros;
  }

  function applySearch() {
    const q = el.search.value.trim();
    
    if (q) {
      const parsedFilters = parseSearchQuery(q);
      state.filtros = parsedFilters; // Reemplazar completamente los filtros
    } else {
      state.filtros = {};
    }

    // Limpiar IDs renderizados para re-renderizar con nuevos filtros
    state.renderedLogIds.clear();
    el.logStream.innerHTML = "";

    renderFilterChips();
    loadLogs();
    
    // Feedback visual
    el.search.classList.add('border-green-400');
    setTimeout(() => el.search.classList.remove('border-green-400'), 500);
  }

  function renderFilterChips() {
    const box = el.filters;
    if (!box) return;

    box.innerHTML = "";

    // Mostrar chip de rango temporal si se aplicó un filtro explícito
    if (state.filtroTemporalActivo) {
      const rangoChip = document.createElement("span");
      rangoChip.className =
        "inline-flex items-center gap-1.5 px-2.5 py-1 bg-purple-500/20 border border-purple-500/40 text-purple-600 dark:text-purple-400 text-xs rounded-full hover:bg-purple-500/30 transition-colors";
      
      let rangoTexto = '';
      if (state.horasRango === 24) rangoTexto = 'Hoy (últimas 24h)';
      else if (state.horasRango === 168) rangoTexto = 'Últimos 7 días';
      else if (state.horasRango === 720) rangoTexto = 'Últimos 30 días';
      else rangoTexto = `Últimas ${state.horasRango}h`;
      
      rangoChip.innerHTML = `
        <span class="material-symbols-outlined text-xs">schedule</span>
        <span class="font-semibold">Rango</span>
        <span class="opacity-80">:</span>
        <span>${rangoTexto}</span>
        <button class="material-symbols-outlined text-xs text-purple-600 dark:text-purple-400 hover:text-white transition-colors rango-clear-btn">close</button>
      `;

      rangoChip.querySelector(".rango-clear-btn").onclick = () => {
        state.horasRango = 24; // Volver a default
        state.filtroTemporalActivo = false; // Desactivar filtro temporal
        state.renderedLogIds.clear();
        el.logStream.innerHTML = "";
        renderFilterChips();
        loadLogs();
        showNotification("Filtro temporal eliminado", "info");
      };

      box.appendChild(rangoChip);
    }

    // Mostrar chips de filtros normales
    Object.entries(state.filtros).forEach(([k, v]) => {
      if (!v) return;
      
      const chip = document.createElement("span");
      chip.className =
        "inline-flex items-center gap-1.5 px-2.5 py-1 bg-primary/20 border border-primary/40 text-primary text-xs rounded-full hover:bg-primary/30 transition-colors";

      chip.innerHTML = `
        <span class="font-semibold">${k}</span>
        <span class="opacity-80">:</span>
        <span>${v}</span>
        <button class="material-symbols-outlined text-xs text-primary hover:text-white transition-colors">close</button>
      `;

      chip.querySelector("button").onclick = () => {
        delete state.filtros[k];
        state.renderedLogIds.clear(); // Limpiar IDs para re-renderizar
        el.logStream.innerHTML = ""; // Limpiar contenedor
        renderFilterChips();
        loadLogs();
      };

      box.appendChild(chip);
    });
  }

  // ===========================================================
  //  EXPORTACIONES
  // ===========================================================
  async function exportFormato(formato) {
    pushTerminal(`Exportando en formato ${formato}…`);

    const payload = {
      formato,
      filtros: state.filtros,
      limit: 600,
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    const res = await fetch(API_EXPORT, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify(payload),
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `auditoria.${formato}`;
    a.click();

    URL.revokeObjectURL(url);
  }

  // ===========================================================
  //  FILTROS TEMPORALES (Conectados a botones del header)
  // ===========================================================
  function filtrarHoy() {
    state.filtros = {}; // Limpiar otros filtros
    state.horasRango = 24; // Últimas 24 horas
    state.filtroTemporalActivo = true; // Marcar como filtro activo
    state.renderedLogIds.clear();
    el.logStream.innerHTML = "";
    renderFilterChips();
    loadLogs().then(() => {
      // Auto-scroll al final (eventos más recientes) para HOY
      setTimeout(() => {
        if (el.logStream) {
          el.logStream.scrollTop = el.logStream.scrollHeight;
        }
      }, 150);
    });
    showNotification("📅 Mostrando eventos de hoy (últimas 24h)", "info");
  }
  
  function filtrarSemana() {
    state.filtros = {}; // Limpiar otros filtros
    state.horasRango = 168; // 7 días = 168 horas
    state.filtroTemporalActivo = true; // Marcar como filtro activo
    state.renderedLogIds.clear();
    el.logStream.innerHTML = "";
    renderFilterChips();
    loadLogs().then(() => {
      // Auto-scroll al inicio (eventos más antiguos) para SEMANA
      setTimeout(() => {
        if (el.logStream) {
          el.logStream.scrollTop = 0;
          showNotification("📜 Mostrando desde el evento más antiguo de la semana", "success");
        }
      }, 150);
    });
    showNotification("📅 Cargando eventos de los últimos 7 días...", "info");
  }
  
  function filtrarMes() {
    state.filtros = {}; // Limpiar otros filtros
    state.horasRango = 720; // 30 días = 720 horas
    state.filtroTemporalActivo = true; // Marcar como filtro activo
    state.renderedLogIds.clear();
    el.logStream.innerHTML = "";
    renderFilterChips();
    loadLogs().then(() => {
      // Auto-scroll al inicio (eventos más antiguos) para MES
      setTimeout(() => {
        if (el.logStream) {
          el.logStream.scrollTop = 0;
          showNotification("📜 Mostrando desde el evento más antiguo del mes", "success");
        }
      }, 150);
    });
    showNotification("📅 Cargando eventos del último mes...", "info");
  }
  
  // Conectar botones del header con funciones de filtrado
  function conectarBotonesHeaderFiltros() {
    const botonesHeader = document.querySelectorAll('.filtro-fecha-btn');
    
    if (!botonesHeader.length) {
      console.warn('⚠️ No se encontraron botones de filtro de fecha en el header');
      return;
    }
    
    botonesHeader.forEach(btn => {
      // Evitar listeners duplicados
      if (btn.dataset.listenerAdded === 'true') return;
      btn.dataset.listenerAdded = 'true';
      
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const rango = btn.getAttribute('data-rango');
        
        // Remover clase activa de todos los botones
        botonesHeader.forEach(b => {
          b.classList.remove('bg-primary', 'text-white');
          b.classList.add('text-neutral-700', 'dark:text-neutral-300');
        });
        
        // Activar el botón clickeado
        btn.classList.add('bg-primary', 'text-white');
        btn.classList.remove('text-neutral-700', 'dark:text-neutral-300');
        
        // Ejecutar filtro correspondiente
        if (rango === 'hoy') {
          filtrarHoy();
        } else if (rango === 'semana') {
          filtrarSemana();
        } else if (rango === 'mes') {
          filtrarMes();
        }
      });
    });
  }

  // ===========================================================
  //  USUARIOS ACTIVOS - FILTRO POR USUARIO ACTUAL
  // ===========================================================
  function detectCurrentUser() {
    // Primero intentar obtener de la sesión del backend (meta tag)
    const userFromMeta = document.querySelector('meta[name="current-user"]')?.getAttribute('content');
    if (userFromMeta && userFromMeta !== 'None') {
      state.currentUser = userFromMeta;
      if (el.currentUserDisplay) {
        el.currentUserDisplay.textContent = userFromMeta.split(' ')[0];
      }
      return;
    }
    
    // Buscar el evento de login más reciente en la tabla auditoria_eventos
    const loginLogs = state.logs.filter(log => 
      log.tipo_evento === 'login_logout_usuarios'
    ).sort((a, b) => {
      const timeA = new Date(a.timestamp || 0).getTime();
      const timeB = new Date(b.timestamp || 0).getTime();
      return timeB - timeA; // Más recientes primero
    });
    
    // Buscar el login más reciente sin un logout posterior
    for (let log of loginLogs) {
      const esLogin = log.detalle.toLowerCase().includes('inició') || 
                     log.detalle.toLowerCase().includes('inicio');
      if (esLogin && log.usuario && log.usuario !== 'Sistema') {
        state.currentUser = log.usuario;
        if (el.currentUserDisplay) {
          el.currentUserDisplay.textContent = log.usuario.split(' ')[0];
        }
        return;
      }
    }
    
    // Si no se encontró login, intentar de cualquier evento reciente
    const eventosRecientes = state.logs.filter(log => 
      log.usuario && log.usuario !== 'Sistema'
    ).sort((a, b) => {
      const timeA = new Date(a.timestamp || 0).getTime();
      const timeB = new Date(b.timestamp || 0).getTime();
      return timeB - timeA;
    });
    
    if (eventosRecientes.length > 0) {
      state.currentUser = eventosRecientes[0].usuario;
      if (el.currentUserDisplay) {
        el.currentUserDisplay.textContent = eventosRecientes[0].usuario.split(' ')[0];
      }
      return;
    }
    
    // Si no se encontró ningún usuario, limpiar
    state.currentUser = null;
    if (el.currentUserDisplay) {
      el.currentUserDisplay.textContent = 'Mi usuario';
    }
  }

  function updateActiveUserCount() {
    // Contar usuarios que hicieron login en los últimos 30 minutos
    const ahora = Date.now();
    const treintaMin = 30 * 60 * 1000;
    
    const usuariosActivos = new Set();
    
    // IMPORTANTE: Agregar el usuario actual de la sesión primero
    if (state.currentUser && state.currentUser !== 'Sistema') {
      usuariosActivos.add(state.currentUser);
    }
    
    state.logs.forEach(log => {
      if (log.tipo_evento !== 'login_logout_usuarios') return;
      
      const timestamp = new Date(log.timestamp).getTime();
      const esReciente = ahora - timestamp < treintaMin;
      const esLogin = log.detalle.toLowerCase().includes('inició') || 
                     log.detalle.toLowerCase().includes('inicio');
      
      if (esReciente && esLogin && log.usuario && log.usuario !== 'Sistema') {
        usuariosActivos.add(log.usuario);
      }
    });
    
    if (el.activeUserCount) {
      el.activeUserCount.textContent = usuariosActivos.size;
    }
  }

  function filtrarPorUsuarioActual() {
    if (!state.currentUser) {
      showNotification("No se detectó usuario actual", "warning");
      return;
    }
    
    // Aplicar filtro de usuario sin tocar el input
    state.filtros = { usuario: state.currentUser };
    
    // Limpiar y re-renderizar
    state.renderedLogIds.clear();
    el.logStream.innerHTML = "";
    
    renderFilterChips();
    loadLogs();
    
    showNotification(`Mostrando eventos de ${state.currentUser}`, "success");
  }

  async function mostrarUsuariosActivos() {
    const ahora = Date.now();
    const treintaMin = 30 * 60 * 1000;
    const usuariosActivos = new Map();
    
    // IMPORTANTE: Agregar el usuario actual de la sesión primero
    if (state.currentUser && state.currentUser !== 'Sistema') {
      usuariosActivos.set(state.currentUser, {
        nombre: state.currentUser,
        ultimoLogin: new Date().toISOString(),
        hora: new Date().toLocaleTimeString('es-CL', { 
          timeZone: 'America/Santiago',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        })
      });
    }
    
    // Agregar otros usuarios que hicieron login recientemente
    state.logs.forEach(log => {
      if (log.tipo_evento !== 'login_logout_usuarios') return;
      
      const timestamp = new Date(log.timestamp).getTime();
      const esReciente = ahora - timestamp < treintaMin;
      const esLogin = log.detalle.toLowerCase().includes('inició') || 
                     log.detalle.toLowerCase().includes('inicio');
      
      if (esReciente && esLogin && log.usuario && log.usuario !== 'Sistema') {
        if (!usuariosActivos.has(log.usuario)) {
          usuariosActivos.set(log.usuario, {
            nombre: log.usuario,
            ultimoLogin: log.timestamp,
            hora: log.hora
          });
        }
      }
    });
    
    // Obtener TODOS los usuarios del sistema desde la base de datos
    let todosLosUsuariosSistema = [];
    try {
      const response = await fetch('/api/usuarios');
      const data = await response.json();
      console.log('📊 Respuesta /api/usuarios:', data);
      if (data.success && data.data) {
        todosLosUsuariosSistema = data.data;
      }
    } catch (error) {
      console.error('❌ Error obteniendo usuarios del sistema:', error);
    }
    
    // Clasificar usuarios por estado (activo/desconectado)
    const usuariosDesconectados = todosLosUsuariosSistema
      .filter(u => !usuariosActivos.has(u.nombre))
      .map(u => {
        // Buscar la última actividad de este usuario en los logs
        let ultimaActividad = null;
        let hora = 'Sin actividad registrada';
        
        for (const log of state.logs) {
          if (log.usuario === u.nombre) {
            if (!ultimaActividad || new Date(log.timestamp) > ultimaActividad) {
              ultimaActividad = new Date(log.timestamp);
              hora = log.hora;
            }
          }
        }
        
        return {
          nombre: u.nombre,
          ts: ultimaActividad || new Date(u.fecha_registro || Date.now()),
          hora: hora,
          rol: u.rol
        };
      })
      .sort((a, b) => b.ts - a.ts); // Ordenar por más reciente primero
    
    // Modal informativo - sin filtrado automático
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4';
    modal.innerHTML = `
      <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-md w-full max-h-[80vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4 sticky top-0 bg-white dark:bg-gray-800 pb-2 z-10">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">
            <span class="material-symbols-outlined text-green-500 align-middle">group</span>
            Usuarios del Sistema
          </h3>
          <button class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 modal-close-btn">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        
        <!-- Usuarios Activos -->
        <div class="mb-4">
          <h4 class="text-sm font-semibold text-green-600 dark:text-green-400 mb-2 flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Activos (últimos 30 min) · ${usuariosActivos.size}
          </h4>
          <div class="space-y-2">
            ${usuariosActivos.size === 0 ? 
              '<p class="text-gray-500 dark:text-gray-400 text-center py-4 text-sm">No hay usuarios activos</p>' :
              Array.from(usuariosActivos.values()).map(u => `
                <div class="usuario-card cursor-pointer flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800 hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors" data-usuario="${u.nombre}">
                  <div>
                    <p class="font-semibold text-gray-900 dark:text-white">${u.nombre}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">Último login: ${u.hora}</p>
                  </div>
                  <span class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
                </div>
              `).join('')
            }
          </div>
        </div>
        
        <!-- Usuarios Desconectados (Colapsable) -->
        <div>
          <button id="toggle-desconectados" class="w-full flex items-center justify-between text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2 hover:text-gray-900 dark:hover:text-gray-200 transition-colors">
            <span class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full bg-gray-400"></span>
              Desconectados · ${usuariosDesconectados.length}
            </span>
            <span class="material-symbols-outlined transform transition-transform" id="toggle-icon">
              expand_more
            </span>
          </button>
          <div id="lista-desconectados" class="space-y-2 hidden">
            ${usuariosDesconectados.length === 0 ? 
              '<p class="text-gray-500 dark:text-gray-400 text-center py-4 text-sm">Todos los usuarios están activos</p>' :
              usuariosDesconectados.map(u => `
                <div class="usuario-card cursor-pointer flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors" data-usuario="${u.nombre}">
                  <div>
                    <p class="font-semibold text-gray-900 dark:text-white">${u.nombre}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">Última actividad: ${u.hora}</p>
                  </div>
                  <span class="w-3 h-3 rounded-full bg-gray-400"></span>
                </div>
              `).join('')
            }
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Agregar event listeners a todas las tarjetas de usuario para filtrar
    const usuarioCards = modal.querySelectorAll('.usuario-card');
    usuarioCards.forEach(card => {
      card.onclick = () => {
        const nombreUsuario = card.getAttribute('data-usuario');
        if (nombreUsuario) {
          // Aplicar filtro de usuario
          state.filtros = { usuario: nombreUsuario };
          
          // Limpiar y re-renderizar
          state.renderedLogIds.clear();
          el.logStream.innerHTML = "";
          
          renderFilterChips();
          loadLogs();
          
          // Cerrar modal
          modal.remove();
          
          // Mostrar notificación
          showNotification(`Mostrando eventos de ${nombreUsuario}`, "success");
        }
      };
      
      // Efecto hover visual
      card.onmouseenter = () => {
        card.style.transform = 'scale(1.02)';
        card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
      };
      card.onmouseleave = () => {
        card.style.transform = 'scale(1)';
        card.style.boxShadow = 'none';
      };
    });
    
    // Toggle para usuarios desconectados
    const toggleBtn = modal.querySelector('#toggle-desconectados');
    const listaDesconectados = modal.querySelector('#lista-desconectados');
    const toggleIcon = modal.querySelector('#toggle-icon');
    
    if (toggleBtn && listaDesconectados && toggleIcon) {
      toggleBtn.onclick = () => {
        const isHidden = listaDesconectados.classList.contains('hidden');
        if (isHidden) {
          listaDesconectados.classList.remove('hidden');
          toggleIcon.style.transform = 'rotate(180deg)';
        } else {
          listaDesconectados.classList.add('hidden');
          toggleIcon.style.transform = 'rotate(0deg)';
        }
      };
    }
    
    // Cerrar modal
    const closeBtn = modal.querySelector('.modal-close-btn');
    if (closeBtn) {
      closeBtn.onclick = () => modal.remove();
    }
    modal.onclick = (e) => { 
      if (e.target === modal) modal.remove(); 
    };
  }



  // ===========================================================
  //  RECALIBRAR (DEPRECADO - mantenido para compatibilidad)
  // ===========================================================
  async function recalibrarSensores() {
    pushTerminal("Enviando secuencia de recalibración…");

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    const res = await fetch(API_RECALIBRAR, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({ detalle: "Recalibración solicitada desde UI" }),
    });

    const data = await res.json();
    pushTerminal(data.mensaje || "Recalibrado.");
    loadLogs();
  }

  // ===========================================================
  //  EVENTOS
  // ===========================================================
  if (el.runQuery) el.runQuery.onclick = applySearch;
  if (el.search) {
    el.search.onkeydown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        applySearch();
      }
    };
    
    // Agregar tooltip con ejemplos
    el.search.onfocus = () => {
      el.search.placeholder = "Ej: usuario:Francisco tipo_evento:ventas";
    };
    
    el.search.onblur = () => {
      if (!el.search.value) {
        el.search.placeholder = "usuario:nombre rut:12345678-9 tipo_evento:ventas";
      }
    };
  }

  if (el.clearFilters)
    el.clearFilters.onclick = () => {
      state.filtros = {};
      state.horasRango = 24; // Resetear a default
      state.filtroTemporalActivo = false; // Desactivar filtro temporal
      if (el.search) {
        el.search.value = "";
      }
      state.renderedLogIds.clear(); // Limpiar IDs para re-renderizar
      el.logStream.innerHTML = ""; // Limpiar contenedor
      renderFilterChips();
      loadLogs();
      showNotification("Filtros eliminados", "info");
    };

  if (el.exportCsv) el.exportCsv.onclick = () => exportFormato("csv");
  if (el.exportCsvFooter) el.exportCsvFooter.onclick = () => exportFormato("csv");
  if (el.exportZip) el.exportZip.onclick = () => exportFormato("zip");
  if (el.exportPdf) el.exportPdf.onclick = () => exportFormato("pdf");
  if (el.filterUser) el.filterUser.onclick = filtrarPorUsuarioActual;
  if (el.activeUsers) el.activeUsers.onclick = mostrarUsuariosActivos;
  if (el.filterToday) el.filterToday.onclick = filtrarHoy;
  if (el.filterWeek) el.filterWeek.onclick = filtrarSemana;
  if (el.filterMonth) el.filterMonth.onclick = filtrarMes;

  if (el.recalibrate) el.recalibrate.onclick = recalibrarSensores;

  // ===========================================================
  //  ARRANQUE
  // ===========================================================
  
  // Prevenir inicialización múltiple
  if (window.auditoriaInitialized) {
    console.warn('⚠️ Sistema de auditoría ya inicializado, evitando duplicados');
    return;
  }
  window.auditoriaInitialized = true;
  
  loadLogs();
  conectarBotonesHeaderFiltros(); // Conectar botones del header
  
  // Scroll inicial al fondo después de cargar
  setTimeout(() => {
    if (el.logStream) {
      el.logStream.scrollTop = el.logStream.scrollHeight;
    }
  }, 200);
  
  setInterval(loadLogs, REFRESH_INTERVAL);
  
  // Atajos de teclado para mejor UX (solo una vez)
  const handleKeydown = (e) => {
    // Ctrl+F o Cmd+F: Focus en buscador
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
      e.preventDefault();
      if (el.search) {
        el.search.focus();
        el.search.select();
      }
    }
    
    // Ctrl+L o Cmd+L: Limpiar filtros
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
      e.preventDefault();
      if (el.clearFilters) {
        el.clearFilters.click();
      }
    }
    
    // ESC: Limpiar buscador
    if (e.key === 'Escape' && el.search === document.activeElement) {
      el.search.value = '';
      el.search.blur();
    }
  };
  
  document.addEventListener('keydown', handleKeydown);
  
  console.log('🚀 Sistema de auditoría inicializado correctamente');
  console.log('💡 Atajos de teclado:');
  console.log('   - Ctrl+F: Focus en buscador');
  console.log('   - Ctrl+L: Limpiar filtros');
  console.log('   - ESC: Limpiar buscador');
  console.log('   - Enter: Buscar');
})();
