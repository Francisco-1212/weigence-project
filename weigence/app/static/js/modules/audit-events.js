// ===============================================================
//  MÓDULO: AUDIT EVENTS
//  Registro y manejo de event listeners
// ===============================================================

import { parseSearchQuery, renderFilterChips, filtrarHoy, filtrarSemana, filtrarMes, limpiarFiltros, filtrarPorUsuario } from './audit-filters.js';
import { exportLogs } from './audit-api.js';
import { pushTerminal, showNotification } from './audit-render.js';
import { state } from './audit-state.js';

/**
 * Elementos del DOM
 */
const el = {
  terminal: null,
  search: null,
  runQuery: null,
  filters: null,
  logStream: null,
  empty: null,
  streamStatus: null,
  lastUpdated: null,
  mem: null,
  cpu: null,
  latency: null,
  exportCsv: null,
  exportCsvFooter: null,
  exportZip: null,
  exportPdf: null,
  filterUser: null,
  currentUserDisplay: null,
  activeUsers: null,
  activeUserCount: null,
  clearFilters: null,
  filterToday: null,
  filterWeek: null,
  filterMonth: null,
};

/**
 * Inicializa referencias a elementos del DOM
 */
export function initElements() {
  el.terminal = document.getElementById("audit-terminal-output");
  el.search = document.getElementById("audit-search");
  el.runQuery = document.getElementById("audit-exec-query");
  el.filters = document.getElementById("audit-active-filters");
  el.logStream = document.getElementById("audit-log-stream");
  el.empty = document.getElementById("audit-log-empty");
  el.streamStatus = document.getElementById("audit-stream-status");
  el.lastUpdated = document.getElementById("audit-last-updated");
  el.mem = document.getElementById("audit-mem-usage");
  el.cpu = document.getElementById("audit-cpu-usage");
  el.latency = document.getElementById("audit-latency");
  el.exportCsv = document.getElementById("audit-export-csv");
  el.exportCsvFooter = document.getElementById("audit-export-csv-footer");
  el.exportZip = document.getElementById("audit-export-zip");
  el.exportPdf = document.getElementById("audit-export-pdf");
  el.filterUser = document.getElementById("audit-filter-user");
  el.currentUserDisplay = document.getElementById("current-user-display");
  el.activeUsers = document.getElementById("audit-active-users");
  el.activeUserCount = document.getElementById("active-user-count");
  el.clearFilters = document.getElementById("audit-clear-filters");
  el.filterToday = document.getElementById("audit-filter-today");
  el.filterWeek = document.getElementById("audit-filter-week");
  el.filterMonth = document.getElementById("audit-filter-month");
  
  return el;
}

/**
 * Aplica búsqueda desde input
 */
function applySearch() {
  const q = el.search.value.trim();
  
  if (q) {
    const parsedFilters = parseSearchQuery(q);
    state.filtros = parsedFilters;
  } else {
    state.filtros = {};
  }

  state.renderedLogIds.clear();
  if (el.logStream) el.logStream.innerHTML = "";

  renderFilterChips();
  window.dispatchEvent(new CustomEvent('audit:reload'));
  
  // Feedback visual
  el.search.classList.add('border-green-400');
  setTimeout(() => el.search.classList.remove('border-green-400'), 500);
}

/**
 * Filtra por usuario actual de la sesión
 */
function filtrarPorUsuarioActual() {
  if (!state.currentUser || state.currentUser === 'Sistema') {
    showNotification("No se detectó usuario activo en la sesión", "warning");
    return;
  }
  
  filtrarPorUsuario(state.currentUser);
  showNotification(`Mostrando eventos de ${state.currentUser}`, "success");
}

/**
 * Muestra modal con usuarios activos
 */
async function mostrarUsuariosActivos() {
  // Esta función se mantendrá en el archivo principal por complejidad
  window.dispatchEvent(new CustomEvent('audit:showActiveUsers'));
}

/**
 * Maneja exportación de logs
 */
async function handleExport(formato) {
  try {
    pushTerminal(`Exportando en formato ${formato}…`);
    const blob = await exportLogs(formato, state.filtros);
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `auditoria.${formato}`;
    a.click();
    URL.revokeObjectURL(url);
    
    showNotification(`Exportación ${formato.toUpperCase()} completada`, "success");
  } catch (error) {
    showNotification(`Error al exportar: ${error.message}`, "error");
    console.error("Error en exportación:", error);
  }
}

/**
 * Registra todos los event listeners
 */
export function registerEventListeners() {
  // Búsqueda
  if (el.runQuery) {
    el.runQuery.onclick = applySearch;
  }
  
  if (el.search) {
    el.search.onkeydown = (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        applySearch();
      }
    };
    
    el.search.onfocus = () => {
      el.search.placeholder = "Ej: usuario:Francisco tipo_evento:ventas";
    };
    
    el.search.onblur = () => {
      if (!el.search.value) {
        el.search.placeholder = "usuario:nombre rut:12345678-9 tipo_evento:ventas";
      }
    };
  }

  // Filtros
  if (el.clearFilters) {
    el.clearFilters.onclick = () => {
      limpiarFiltros();
      showNotification("Filtros eliminados", "info");
    };
  }

  if (el.filterToday) {
    el.filterToday.onclick = () => {
      filtrarHoy();
      showNotification("📅 Mostrando eventos de hoy (últimas 24h)", "info");
    };
  }

  if (el.filterWeek) {
    el.filterWeek.onclick = () => {
      filtrarSemana();
      showNotification("📅 Cargando eventos de los últimos 7 días...", "info");
    };
  }

  if (el.filterMonth) {
    el.filterMonth.onclick = () => {
      filtrarMes();
      showNotification("📅 Cargando eventos de los últimos 30 días...", "info");
    };
  }

  // Exportaciones
  if (el.exportCsv) {
    el.exportCsv.onclick = () => handleExport("csv");
  }
  
  if (el.exportCsvFooter) {
    el.exportCsvFooter.onclick = () => handleExport("csv");
  }
  
  if (el.exportZip) {
    el.exportZip.onclick = () => handleExport("zip");
  }
  
  if (el.exportPdf) {
    el.exportPdf.onclick = () => handleExport("pdf");
  }

  // Usuario
  if (el.filterUser) {
    el.filterUser.onclick = filtrarPorUsuarioActual;
  }

  if (el.activeUsers) {
    el.activeUsers.onclick = mostrarUsuariosActivos;
  }
}

/**
 * Remueve todos los event listeners (cleanup)
 */
export function removeEventListeners() {
  // Implementación para cleanup si es necesario
  Object.keys(el).forEach(key => {
    if (el[key] && el[key].onclick) {
      el[key].onclick = null;
    }
  });
}

export { el };
