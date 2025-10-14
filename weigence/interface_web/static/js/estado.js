document.addEventListener('DOMContentLoaded', () => {
  // Elementos DOM principales
  const lastUpdateTimestampEl = document.getElementById('last-update-timestamp');
  const statusIconEl = document.getElementById('status-icon');
  const statusTextEl = document.getElementById('status-text');
  const systemStatusEl = document.getElementById('system-status');
  const activityIndicatorEl = document.getElementById('activity-indicator');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnShowHistory = document.getElementById('btn-show-history');
  const historyModal = document.getElementById('history-modal');
  const historyList = document.getElementById('history-list');
  const closeHistoryBtn = document.getElementById('close-history');

  // Estados del sistema
  const states = {
    online: {
      icon: 'check_circle', colorClass: 'text-green-500',
      text: 'Sistema en línea', aria: 'El sistema está en línea y operativo.'
    },
    warning: {
      icon: 'warning', colorClass: 'text-yellow-500',
      text: 'Problemas de conexión', aria: 'El sistema presenta problemas de conexión.'
    },
    offline: {
      icon: 'error', colorClass: 'text-red-500',
      text: 'Sistema desconectado', aria: 'El sistema está desconectado.'
    },
    syncing: {
      icon: 'sync', colorClass: 'text-primary-600 animate-spin',
      text: 'Sincronizando...', aria: 'Sincronizando datos; espere por favor.'
    },
  };

  let lastUpdate = null;

  // Actualiza la barra de estado visual y accesible
  function updateStatus(stateKey) {
    const state = states[stateKey];
    if (!state) return;
    statusIconEl.textContent = state.icon;
    statusIconEl.className = `material-symbols-outlined ${state.colorClass}`;
    statusTextEl.textContent = state.text;
    statusTextEl.className = state.colorClass;
    statusTextEl.setAttribute('aria-live', 'polite');
    statusTextEl.setAttribute('title', state.aria);

    // Actualiza ARIA del área de estado
    systemStatusEl.setAttribute('aria-label', state.aria);

    systemStatusEl.classList.remove('hidden');
    activityIndicatorEl.classList.toggle('hidden', stateKey !== 'syncing');
  }

  // Guarda timestamp y actualiza el texto de última actualización
  function setLastUpdate(timestamp) {
    lastUpdate = new Date(timestamp);
    updateTimestampText();
  }

  // Formatea el timestamp a formato amigable y local
function updateTimestampText() {
  if (!lastUpdate) {
    lastUpdateTimestampEl.textContent = '--:--';
    lastUpdateTimestampEl.setAttribute('title', 'Sin datos de actualización');
    return;
  }

  // Usa formato local del sistema y muestra fecha + hora completa
  const formatted = lastUpdate.toLocaleString('es-ES', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });

  lastUpdateTimestampEl.textContent = formatted;
  lastUpdateTimestampEl.setAttribute('title', `Actualizado el ${formatted}`);
}



  // Obtiene y actualiza el estado del sistema desde API
  async function fetchSystemStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error('Error obteniendo estado');
      const data = await res.json();
      // Prioriza 'online' si está operativo
      const estado = (data.connection_state === 'online') ? 'online' : data.connection_state;
      setLastUpdate(data.last_update);
      updateStatus(estado);
    } catch (error) {
      updateStatus('offline');
      console.error(error);
    }
  }

  // Renderiza historial de eventos en el modal
  async function fetchHistory() {
    historyList.innerHTML = '<li class="text-gray-500 animate-pulse">Cargando...</li>';
    try {
      const res = await fetch('/api/history');
      if (!res.ok) throw new Error('Error obteniendo historial');
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        historyList.innerHTML = data.map(evt =>
          `<li><strong>${new Date(evt.timestamp).toLocaleString(undefined, {
            year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
          })}:</strong> ${evt.message}</li>`
        ).join('');
      } else {
        historyList.innerHTML = '<li class="text-gray-500">Sin eventos recientes.</li>';
      }
    } catch (error) {
      historyList.innerHTML = `<li class="text-red-500">Error cargando historial</li>`;
      console.error(error);
    }
  }

  // Realiza actualización manual de datos
  async function manualRefresh() {
    updateStatus('syncing');
    try {
      const res = await fetch('/api/refresh', { method: 'POST' });
      if (!res.ok) throw new Error('Error refrescando');
      await fetchSystemStatus();
    } catch (err) {
      updateStatus('offline');
      console.error(err);
    }
  }

  // Animación de apertura/cierre del modal historial
  function showHistoryModal() {
    if (!historyModal) return;
    historyModal.classList.remove('hidden');
    historyModal.style.opacity = 0;
    setTimeout(() => {
      historyModal.style.transition = 'opacity 0.3s';
      historyModal.style.opacity = 1;
    }, 10);
    fetchHistory();
  }
  function closeHistoryModal() {
    if (!historyModal) return;
    historyModal.style.opacity = 0;
    setTimeout(() => {
      historyModal.classList.add('hidden');
    }, 300);
  }

  // Asociación de eventos
  if (btnRefresh) btnRefresh.addEventListener('click', manualRefresh);
  if (btnShowHistory) btnShowHistory.addEventListener('click', showHistoryModal);
  if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', closeHistoryModal);

  // Inicialización automática
  fetchSystemStatus();
  setInterval(fetchSystemStatus, 30000);   // Actualiza estado cada 30s
  setInterval(updateTimestampText, 10000); // Actualiza etiqueta cada 10s
});
