// ===============================================================
//  AUDITORÍA · SISTEMA MODULARIZADO
//  Orquestador principal con arquitectura limpia
// ===============================================================

import { fetchLogs, fetchUsuarios } from './modules/audit-api.js';
import { 
  crearElementoLog, 
  crearSeparadorFecha, 
  updateStats, 
  showNotification,
  pushTerminal 
} from './modules/audit-render.js';
import { 
  state, 
  setLogs, 
  detectCurrentUser, 
  updateActiveUserCount,
  calcularEstadisticas,
  detectarLogsNuevos,
  marcarLogsRenderizados,
  generarLogId
} from './modules/audit-state.js';
import { renderFilterChips } from './modules/audit-filters.js';
import { initElements, registerEventListeners, el } from './modules/audit-events.js';

// Constantes
const REFRESH_INTERVAL = 10000; // 10 segundos

/**
 * Renderiza logs en el DOM
 */
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

  // Calcular y actualizar estadísticas
  const stats = calcularEstadisticas();
  updateStats(stats);

  // Ordenar cronológicamente (ascendente: antiguos primero)
  const ordered = [...state.logs].sort((a, b) => {
    const timeA = new Date(a.timestamp || 0).getTime();
    const timeB = new Date(b.timestamp || 0).getTime();
    return timeA - timeB;
  });

  // Detectar scroll position
  const isAtBottom = cont.scrollHeight - cont.scrollTop - cont.clientHeight < 100;

  // Detectar logs nuevos
  const { nuevos, nuevosIds } = detectarLogsNuevos(ordered);

  // Notificación de nuevos eventos
  if (nuevos.length > 2) {
    showNotification(`${nuevos.length} nuevos eventos`, "info");
    
    if (el.streamStatus) {
      el.streamStatus.style.animation = 'none';
      setTimeout(() => {
        el.streamStatus.style.animation = 'pulse-glow 2s ease-in-out infinite';
      }, 100);
    }
  }

  // Reconstruir contenedor
  cont.innerHTML = "";

  // Renderizar con separadores de fecha
  let lastDate = null;
  const hoy = new Date().toLocaleDateString('es-CL', { timeZone: 'America/Santiago' });

  ordered.forEach((log) => {
    const logId = generarLogId(log);
    const esNuevo = nuevosIds.has(logId);
    
    // Fecha del log
    const logDate = new Date(log.timestamp).toLocaleDateString('es-CL', { 
      timeZone: 'America/Santiago' 
    });
    
    // Insertar separador si cambió la fecha
    if (logDate !== lastDate) {
      cont.appendChild(crearSeparadorFecha(logDate));
      lastDate = logDate;
    }
    
    // Crear y agregar elemento de log
    const line = crearElementoLog(log, esNuevo);
    cont.appendChild(line);
    
    // Animación de entrada para nuevos
    if (esNuevo) {
      setTimeout(() => {
        line.style.opacity = '1';
        line.style.transform = 'translateY(0)';
      }, 50);
    }
  });

  // Marcar logs como renderizados
  marcarLogsRenderizados(ordered);

  // Auto-scroll si estaba al fondo
  if (isAtBottom) {
    setTimeout(() => {
      cont.scrollTop = cont.scrollHeight;
    }, 100);
  }
}

/**
 * Carga logs desde la API
 */
async function loadLogs() {
  // Indicador de carga
  if (el.streamStatus) {
    el.streamStatus.classList.remove('bg-green-500');
    el.streamStatus.classList.add('bg-yellow-500');
  }
  if (el.lastUpdated) {
    el.lastUpdated.textContent = "Sincronizando...";
  }

  try {
    const { logs, meta, loadTime } = await fetchLogs(state.filtros, state.horasRango);
    
    setLogs(logs);

    // Actualizar métricas del sistema
    if (meta?.system) {
      if (el.mem) el.mem.textContent = meta.system.mem || "--";
      if (el.cpu) el.cpu.textContent = meta.system.cpu || "--";
      if (el.latency) el.latency.textContent = `${loadTime}ms`;
    }

    // Actualizar usuarios
    detectCurrentUser();
    updateActiveUserCount();

    // Estado exitoso
    if (el.streamStatus) {
      el.streamStatus.classList.remove('bg-yellow-500');
      el.streamStatus.classList.add('bg-green-500');
    }
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-CL', {
      timeZone: 'America/Santiago',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
    
    if (el.lastUpdated) {
      el.lastUpdated.textContent = timeStr;
    }

    renderLogs();
    
    // Emitir evento de carga completada
    window.dispatchEvent(new CustomEvent('audit:loaded'));

  } catch (error) {
    console.error("Error cargando logs:", error);
    
    if (el.streamStatus) {
      el.streamStatus.classList.remove('bg-yellow-500', 'bg-green-500');
      el.streamStatus.classList.add('bg-red-500');
    }
    if (el.lastUpdated) {
      el.lastUpdated.textContent = error.message ? `Error: ${error.message.substring(0, 30)}...` : "Error de conexión";
    }
    
    // Mostrar logs vacíos en caso de error
    state.logs = [];
    renderLogs();
  }
}

/**
 * Muestra modal con usuarios activos y desconectados
 */
async function mostrarUsuariosActivos() {
  const ahora = Date.now();
  const treintaMin = 30 * 60 * 1000;
  const usuariosActivos = new Map();
  
  // Usuario actual de la sesión
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
  
  // Usuarios con login reciente
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
  
  // Obtener todos los usuarios del sistema
  let todosUsuarios = [];
  try {
    todosUsuarios = await fetchUsuarios();
  } catch (error) {
    console.error('Error obteniendo usuarios:', error);
  }
  
  // Usuarios desconectados
  const usuariosDesconectados = todosUsuarios
    .filter(u => !usuariosActivos.has(u.nombre))
    .map(u => {
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
    .sort((a, b) => b.ts - a.ts);

  // Crear modal
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
  
  // Event listeners para filtrar por usuario al hacer click
  const usuarioCards = modal.querySelectorAll('.usuario-card');
  usuarioCards.forEach(card => {
    card.onclick = () => {
      const nombreUsuario = card.getAttribute('data-usuario');
      if (nombreUsuario) {
        state.filtros = { usuario: nombreUsuario };
        state.renderedLogIds.clear();
        if (el.logStream) el.logStream.innerHTML = "";
        
        renderFilterChips();
        loadLogs();
        modal.remove();
        
        showNotification(`Mostrando eventos de ${nombreUsuario}`, "success");
      }
    };
    
    card.onmouseenter = () => {
      card.style.transform = 'scale(1.02)';
      card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    };
    card.onmouseleave = () => {
      card.style.transform = 'scale(1)';
      card.style.boxShadow = 'none';
    };
  });
  
  // Toggle para desconectados
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

/**
 * Inicializa el sistema de auditoría
 */
function init() {
  // Prevenir inicialización múltiple
  if (window.auditoriaInitialized) {
    console.warn('⚠️ Sistema de auditoría ya inicializado');
    return;
  }
  window.auditoriaInitialized = true;

  // Inicializar elementos del DOM
  initElements();

  // Registrar event listeners
  registerEventListeners();

  // Event listener para recargas
  window.addEventListener('audit:reload', loadLogs);
  
  // Event listener para mostrar usuarios activos
  window.addEventListener('audit:showActiveUsers', mostrarUsuariosActivos);

  // Carga inicial
  loadLogs();

  // Auto-refresh cada 10 segundos
  setInterval(loadLogs, REFRESH_INTERVAL);

  console.log('✅ Sistema de auditoría inicializado correctamente');
}

// Auto-inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
