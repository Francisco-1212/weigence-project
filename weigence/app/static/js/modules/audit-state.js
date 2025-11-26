// ===============================================================
//  MÓDULO: AUDIT STATE
//  Gestión centralizada del estado de la auditoría
// ===============================================================

/**
 * Estado global de la aplicación de auditoría
 */
export const state = {
  filtros: {},
  logs: [],
  currentUser: null,
  renderedLogIds: new Set(),
  horasRango: 24,  // Horas hacia atrás (default: 24h = hoy)
  filtroTemporalActivo: false,  // Indica si se aplicó filtro temporal explícito
};

/**
 * Normaliza un log entrante desde la API
 */
export function normalize(entry) {
  const SEVERIDADES = {
    info: { label: "INFO", class: "text-green-400" },
    warning: { label: "WARN", class: "text-yellow-400" },
    critical: { label: "CRIT", class: "text-red-500" },
    error: { label: "CRIT", class: "text-red-500" }
  };

  let fechaFormateada = "";
  let hora = "";
  
  try {
    // Backend envía timestamps UTC, convertir a hora local Chile
    const timestampUTC = new Date(entry.timestamp);
    
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
  const preset = SEVERIDADES[nivel] || SEVERIDADES.info;

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

/**
 * Reinicia el estado a valores por defecto
 */
export function resetState() {
  state.filtros = {};
  state.horasRango = 24;
  state.filtroTemporalActivo = false;
  state.renderedLogIds.clear();
}

/**
 * Actualiza filtros del estado
 */
export function setFiltros(filtros) {
  state.filtros = { ...filtros };
}

/**
 * Agrega un filtro individual
 */
export function addFiltro(key, value) {
  state.filtros[key] = value;
}

/**
 * Elimina un filtro individual
 */
export function removeFiltro(key) {
  delete state.filtros[key];
}

/**
 * Actualiza rango temporal
 */
export function setHorasRango(horas) {
  state.horasRango = horas;
  state.filtroTemporalActivo = true;
}

/**
 * Actualiza logs normalizados
 */
export function setLogs(logs) {
  state.logs = logs.map(normalize);
}

/**
 * Detecta usuario actual de la sesión
 */
export function detectCurrentUser() {
  // Primero intentar obtener de meta tag (sesión backend)
  const userFromMeta = document.querySelector('meta[name="current-user"]')?.getAttribute('content');
  if (userFromMeta && userFromMeta !== 'None') {
    state.currentUser = userFromMeta;
    const userDisplay = document.getElementById("current-user-display");
    if (userDisplay) {
      userDisplay.textContent = userFromMeta.split(' ')[0];
    }
    return;
  }
  
  // Buscar el evento de login más reciente
  const loginLogs = state.logs.filter(log => 
    log.tipo_evento === 'login_logout_usuarios'
  ).sort((a, b) => {
    const timeA = new Date(a.timestamp || 0).getTime();
    const timeB = new Date(b.timestamp || 0).getTime();
    return timeB - timeA;
  });
  
  // Buscar el login más reciente sin logout posterior
  for (let log of loginLogs) {
    const esLogin = log.detalle.toLowerCase().includes('inició') || 
                   log.detalle.toLowerCase().includes('inicio');
    if (esLogin && log.usuario && log.usuario !== 'Sistema') {
      state.currentUser = log.usuario;
      const userDisplay = document.getElementById("current-user-display");
      if (userDisplay) {
        userDisplay.textContent = log.usuario.split(' ')[0];
      }
      return;
    }
  }
  
  // Si no se encontró login, buscar en eventos recientes
  const eventosRecientes = state.logs.filter(log => 
    log.usuario && log.usuario !== 'Sistema'
  ).sort((a, b) => {
    const timeA = new Date(a.timestamp || 0).getTime();
    const timeB = new Date(b.timestamp || 0).getTime();
    return timeB - timeA;
  });
  
  if (eventosRecientes.length > 0) {
    state.currentUser = eventosRecientes[0].usuario;
    const userDisplay = document.getElementById("current-user-display");
    if (userDisplay) {
      userDisplay.textContent = eventosRecientes[0].usuario.split(' ')[0];
    }
    return;
  }
  
  // Si no se encontró ningún usuario
  state.currentUser = null;
  const userDisplay = document.getElementById("current-user-display");
  if (userDisplay) {
    userDisplay.textContent = 'Mi usuario';
  }
}

/**
 * Actualiza contador de usuarios activos
 */
export function updateActiveUserCount() {
  const ahora = Date.now();
  const treintaMin = 30 * 60 * 1000;
  const usuariosActivos = new Set();
  
  // Usuario actual
  if (state.currentUser && state.currentUser !== 'Sistema') {
    usuariosActivos.add(state.currentUser);
  }
  
  // Usuarios con login reciente
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
  
  // Actualizar contador en UI
  const countEl = document.getElementById("active-user-count");
  if (countEl) {
    countEl.textContent = usuariosActivos.size;
  }
}

/**
 * Calcula estadísticas de logs por severidad
 */
export function calcularEstadisticas() {
  const stats = { info: 0, warn: 0, crit: 0 };
  
  state.logs.forEach(log => {
    const nivel = log.nivel.toLowerCase();
    if (nivel === 'info') stats.info++;
    else if (nivel === 'warn') stats.warn++;
    else if (nivel === 'crit') stats.crit++;
  });
  
  return stats;
}

/**
 * Genera ID único para un log (para tracking de renderizado)
 */
export function generarLogId(log) {
  return `${log.timestamp}_${log.tipo_evento}_${log.detalle.substring(0, 20)}`;
}

/**
 * Marca logs como renderizados
 */
export function marcarLogsRenderizados(logs) {
  logs.forEach(log => {
    const logId = generarLogId(log);
    state.renderedLogIds.add(logId);
  });
}

/**
 * Detecta logs nuevos no renderizados
 */
export function detectarLogsNuevos(logs) {
  const nuevos = [];
  const nuevosIds = new Set();
  
  logs.forEach(log => {
    const logId = generarLogId(log);
    if (!state.renderedLogIds.has(logId)) {
      nuevos.push(log);
      nuevosIds.add(logId);
    }
  });
  
  return { nuevos, nuevosIds };
}

export default state;
