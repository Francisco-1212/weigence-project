// ===============================================================
//  MÓDULO: AUDIT FILTERS
//  Lógica de filtrado y búsqueda de logs
// ===============================================================

import { state, resetState, setHorasRango } from './audit-state.js';

/**
 * Parsea query de búsqueda con formato key:value
 * @param {string} query - Query a parsear
 * @returns {Object} Filtros parseados
 */
export function parseSearchQuery(query) {
  const filtros = {};
  
  // Parsear formato: key:value key2:value2
  const regex = /(\w+):([^\s]+)/g;
  let match;
  
  while ((match = regex.exec(query)) !== null) {
    filtros[match[1]] = match[2];
  }
  
  return filtros;
}

/**
 * Renderiza chips de filtros activos
 */
export function renderFilterChips() {
  const box = document.getElementById("audit-active-filters");
  if (!box) return;

  box.innerHTML = "";

  // Chip de rango temporal
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
      state.horasRango = 24;
      state.filtroTemporalActivo = false;
      state.renderedLogIds.clear();
      
      const logStream = document.getElementById("audit-log-stream");
      if (logStream) logStream.innerHTML = "";
      
      renderFilterChips();
      // Trigger reload (se debe llamar desde el módulo principal)
      window.dispatchEvent(new CustomEvent('audit:reload'));
    };

    box.appendChild(rangoChip);
  }

  // Chips de filtros normales
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
      state.renderedLogIds.clear();
      
      const logStream = document.getElementById("audit-log-stream");
      if (logStream) logStream.innerHTML = "";
      
      renderFilterChips();
      window.dispatchEvent(new CustomEvent('audit:reload'));
    };

    box.appendChild(chip);
  });
}

/**
 * Filtra por HOY (últimas 24h)
 */
export function filtrarHoy() {
  state.filtros = {};
  setHorasRango(24);
  state.renderedLogIds.clear();
  
  const logStream = document.getElementById("audit-log-stream");
  if (logStream) logStream.innerHTML = "";
  
  renderFilterChips();
  
  return new Promise((resolve) => {
    window.addEventListener('audit:loaded', () => {
      setTimeout(() => {
        if (logStream) {
          logStream.scrollTop = logStream.scrollHeight;
        }
        resolve();
      }, 150);
    }, { once: true });
    
    window.dispatchEvent(new CustomEvent('audit:reload'));
  });
}

/**
 * Filtra por SEMANA (últimos 7 días)
 */
export function filtrarSemana() {
  state.filtros = {};
  setHorasRango(168); // 7 días
  state.renderedLogIds.clear();
  
  const logStream = document.getElementById("audit-log-stream");
  if (logStream) logStream.innerHTML = "";
  
  renderFilterChips();
  
  return new Promise((resolve) => {
    window.addEventListener('audit:loaded', () => {
      setTimeout(() => {
        if (logStream) {
          logStream.scrollTop = 0;
        }
        resolve();
      }, 150);
    }, { once: true });
    
    window.dispatchEvent(new CustomEvent('audit:reload'));
  });
}

/**
 * Filtra por MES (últimos 30 días)
 */
export function filtrarMes() {
  state.filtros = {};
  setHorasRango(720); // 30 días
  state.renderedLogIds.clear();
  
  const logStream = document.getElementById("audit-log-stream");
  if (logStream) logStream.innerHTML = "";
  
  renderFilterChips();
  
  return new Promise((resolve) => {
    window.addEventListener('audit:loaded', () => {
      setTimeout(() => {
        if (logStream) {
          logStream.scrollTop = 0;
        }
        resolve();
      }, 150);
    }, { once: true });
    
    window.dispatchEvent(new CustomEvent('audit:reload'));
  });
}

/**
 * Limpia todos los filtros
 */
export function limpiarFiltros() {
  resetState();
  state.renderedLogIds.clear();
  
  const logStream = document.getElementById("audit-log-stream");
  if (logStream) logStream.innerHTML = "";
  
  const searchInput = document.getElementById("audit-search");
  if (searchInput) searchInput.value = "";
  
  renderFilterChips();
  window.dispatchEvent(new CustomEvent('audit:reload'));
}

/**
 * Filtra por usuario específico
 */
export function filtrarPorUsuario(usuario) {
  state.filtros = { usuario };
  state.renderedLogIds.clear();
  
  const logStream = document.getElementById("audit-log-stream");
  if (logStream) logStream.innerHTML = "";
  
  renderFilterChips();
  window.dispatchEvent(new CustomEvent('audit:reload'));
}
