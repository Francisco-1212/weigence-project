// ===============================================================
//  MÓDULO: AUDIT RENDER
//  Templates HTML y funciones de renderizado del DOM
// ===============================================================

// Categorías de eventos con sus colores y siglas
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

// Severidades con sus clases CSS
const SEVERIDADES = {
  info: { label: "INFO", class: "text-green-400" },
  warning: { label: "WARN", class: "text-yellow-400" },
  critical: { label: "CRIT", class: "text-red-500" },
  error: { label: "CRIT", class: "text-red-500" }
};

/**
 * Obtiene información de categoría para un tipo de evento
 */
export function getCategoriaInfo(tipo) {
  return CATEGORIAS[tipo] || CATEGORIAS['otros'];
}

/**
 * Obtiene color para nivel de log
 */
export function logColor(level) {
  const l = level.toUpperCase();
  if (l === "INFO") return "#10b981"; // verde
  if (l === "WARN") return "#f59e0b"; // amarillo
  if (l === "CRIT") return "#ef4444"; // rojo
  return "#94a3b8"; // gris
}

/**
 * Formatea mensaje con HTML enriquecido según tipo de evento
 */
export function formatearMensajeRico(log) {
  const usuario = log.usuario || 'Sistema';
  const rut = log.rut && log.rut !== 'N/A' && log.rut !== 'Sistema' ? log.rut : null;
  const producto = log.producto || '';
  const estante = log.estante || '';
  const detalles = log.detalle || log.mensaje || '';
  
  let resultado = '';
  const usuarioMarcado = `<span class="audit-user-highlight">${usuario}</span>`;
  
  switch(log.tipo_evento) {
    case 'login_logout_usuarios':
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
      resultado = detalles ? detalles.replace(usuario, usuarioMarcado) : `${usuarioMarcado} - ${producto || 'Movimiento'} ${estante ? '@' + estante : ''}`;
      break;
      
    case 'alertas_sistema':
    case 'alertas_stock':
      if (detalles) {
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

/**
 * Crea elemento HTML para un log individual
 */
export function crearElementoLog(log, esNuevo = false) {
  const categoria = getCategoriaInfo(log.tipo_evento);
  const severidadColor = logColor(log.nivel);
  
  // Ajustar color del badge según tipo de evento
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
      badgeColor = '#ef4444';
      borderColor = '#ef4444';
      badgeText = 'OUT';
    } else if (esLogin) {
      badgeColor = '#10b981';
      borderColor = '#10b981';
      badgeText = 'IN';
    }
  }
  // GESTIÓN DE USUARIOS
  else if (log.tipo_evento === 'gestion_usuarios' || log.tipo_evento === 'modificacion_datos') {
    const detalles = log.detalle || log.mensaje || '';
    if (detalles.toLowerCase().includes('cre')) {
      badgeColor = '#10b981';
      borderColor = '#10b981';
    } else if (detalles.toLowerCase().includes('elimin')) {
      badgeColor = '#ef4444';
      borderColor = '#ef4444';
    } else if (detalles.toLowerCase().includes('edit')) {
      badgeColor = '#3b82f6';
      borderColor = '#3b82f6';
    }
  }
  // ALERTAS DE STOCK
  else if (log.tipo_evento === 'alertas_stock') {
    if (log.nivel === 'CRIT') {
      badgeColor = '#ef4444';
      borderColor = '#ef4444';
    } else if (log.nivel === 'WARN') {
      badgeColor = '#f59e0b';
      borderColor = '#f59e0b';
    }
  }
  // RETIROS FUERA DE HORARIO
  else if (log.tipo_evento === 'retiros_fuera_de_horario') {
    badgeColor = '#ef4444';
    borderColor = '#ef4444';
  }
  
  const msg = formatearMensajeRico(log);

  const line = document.createElement("div");
  line.className = "audit-log-entry bg-black/[0.04] dark:bg-white/[0.05] text-slate-950 dark:text-gray-100 hover:bg-blue-500/10 dark:hover:bg-blue-500/12 transition-all duration-150";
  
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

  // Eventos hover
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

  // Click para detalles (modal)
  line.onclick = () => {
    mostrarDetallesLog(log);
  };

  return line;
}

/**
 * Crea separador de fecha
 */
export function crearSeparadorFecha(fecha) {
  const hoy = new Date().toLocaleDateString('es-CL', { timeZone: 'America/Santiago' });
  const dateLabel = fecha === hoy ? 'HOY' : fecha;
  const dateColor = fecha === hoy ? '#3b82f6' : '#6b7280';
  
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
  
  separator.innerHTML = `
    <div style="flex: 1; height: 1px; background: ${dateColor}20;"></div>
    <span style="color: ${dateColor};">${dateLabel}</span>
    <div style="flex: 1; height: 1px; background: ${dateColor}20;"></div>
  `;
  
  return separator;
}

/**
 * Muestra modal con detalles completos del log
 */
export function mostrarDetallesLog(log) {
  // Implementación simplificada - se puede expandir según necesidades
  const details = `
🕐 ${log.hora} - ${log.fecha}
📋 ${log.tipo_evento}
⚠️ ${log.nivel}
👤 ${log.usuario}${log.rut && log.rut !== 'N/A' ? ` (${log.rut})` : ''}
${log.producto ? `📦 ${log.producto}` : ''}
${log.estante ? `📍 ${log.estante}` : ''}

📄 ${log.detalle || log.mensaje}
  `.trim();
  
  alert(details);
}

/**
 * Actualiza estadísticas de logs
 */
export function updateStats(stats) {
  const infoEl = document.querySelector('[data-stat-info]');
  const warnEl = document.querySelector('[data-stat-warn]');
  const critEl = document.querySelector('[data-stat-crit]');
  
  if (infoEl) infoEl.textContent = stats.info || 0;
  if (warnEl) warnEl.textContent = stats.warn || 0;
  if (critEl) critEl.textContent = stats.crit || 0;
}

/**
 * Muestra notificación temporal
 */
export function showNotification(message, type = "info") {
  // Implementación simplificada
  console.log(`[${type.toUpperCase()}] ${message}`);
  
  // TODO: Implementar sistema de toast/notificaciones visual
}

/**
 * Actualiza mensaje del terminal superior
 */
export function pushTerminal(msg) {
  const terminal = document.getElementById("audit-terminal-output");
  if (!terminal) return;
  
  const p = document.createElement("p");
  p.textContent = msg;
  terminal.appendChild(p);
  terminal.scrollTop = terminal.scrollHeight;
}

export { CATEGORIAS, SEVERIDADES };
