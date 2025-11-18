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
  const historyErrorsList = document.getElementById('history-errors-list');
  const historyMovementsList = document.getElementById('history-movements-list');
  const btnTabErrors = document.getElementById('btn-tab-errors');
  const btnTabMovements = document.getElementById('btn-tab-movements');
  const closeHistoryBtn = document.getElementById('close-history');

  // Estados del sistema
  const states = {
    online: {
      icon: 'check_circle', colorClass: 'text-green-500',
      text: 'Sistema en línea', aria: 'El sistema está en línea y operativo.'
    },
    warning: {
      icon: 'warning', colorClass: 'text-yellow-500',
      // default warning text; when details are present we'll show a 'Ver más' link
      text: 'Sistema con fallas', aria: 'El sistema presenta fallas parciales.'
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
  function updateStatus(stateKey, details = []) {
    const state = states[stateKey];
    if (!state) return;
    statusIconEl.textContent = state.icon;
    statusIconEl.className = `material-symbols-outlined ${state.colorClass}`;

    // If warning and details exist, render a 'Ver más' link that opens the modal
    if (stateKey === 'warning' && Array.isArray(details) && details.length > 0) {
      statusTextEl.innerHTML = `${state.text} <a href="#" id="status-ver-mas" class="underline ml-2">Ver más</a>`;
      const verMas = document.getElementById('status-ver-mas');
      if (verMas) {
        verMas.addEventListener('click', (e) => {
          e.preventDefault();
          showStatusDetails(details);
        });
      }
      statusTextEl.className = 'text-yellow-500';
      statusTextEl.setAttribute('title', state.aria);
    } else {
      statusTextEl.textContent = state.text;
      statusTextEl.className = state.colorClass;
      statusTextEl.setAttribute('aria-live', 'polite');
      statusTextEl.setAttribute('title', state.aria);
    }

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
  const details = data.status_details || [];
  setLastUpdate(data.last_update);
  updateStatus(estado, details);
    } catch (error) {
      updateStatus('offline');
      console.error(error);
    }
  }

  // Renderiza historial de eventos en el modal
  async function fetchHistory() {
    if (!historyMovementsList) return;
    historyMovementsList.innerHTML = '<li class="text-gray-500 animate-pulse">Cargando...</li>';
    try {
      const res = await fetch('/api/history');
      if (!res.ok) throw new Error('Error obteniendo historial');
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        historyMovementsList.innerHTML = data.map(evt =>
          `<li><strong>${new Date(evt.timestamp).toLocaleString(undefined, {
            year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
          })}:</strong> ${evt.message}</li>`
        ).join('');
      } else {
        historyMovementsList.innerHTML = '<li class="text-gray-500">Sin eventos recientes.</li>';
      }
    } catch (error) {
      historyMovementsList.innerHTML = `<li class="text-red-500">Error cargando historial</li>`;
      console.error(error);
    }
  }

  // Realiza actualización manual de datos
  async function manualRefresh() {
    updateStatus('syncing');
    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      const res = await fetch('/api/refresh', { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      });
      if (!res.ok) throw new Error('Error refrescando');
      await fetchSystemStatus();
    } catch (err) {
      updateStatus('offline');
      console.error(err);
    }
  }  // Animación de apertura/cierre del modal historial
  function openHistoryModal(tab = 'movements') {
    if (!historyModal) return;
    // Show modal
    historyModal.classList.remove('hidden');
    historyModal.style.opacity = 0;
    setTimeout(() => {
      historyModal.style.transition = 'opacity 0.3s';
      historyModal.style.opacity = 1;
    }, 10);
    // Open requested tab
    if (tab === 'errors') {
      activateTab('errors');
    } else {
      activateTab('movements');
      fetchHistory();
    }
  }
  function closeHistoryModal() {
    if (!historyModal) return;
    historyModal.style.opacity = 0;
    setTimeout(() => {
      historyModal.classList.add('hidden');
    }, 300);
  }

  // Muestra detalles de estado en el modal de historial (reutiliza el modal existente)
  // Activa pestañas dentro del modal
  function activateTab(which) {
    if (which === 'errors') {
      if (historyErrorsList) historyErrorsList.classList.remove('hidden');
      if (historyMovementsList) historyMovementsList.classList.add('hidden');
      if (btnTabErrors) btnTabErrors.classList.add('bg-neutral-100');
      if (btnTabMovements) btnTabMovements.classList.remove('bg-neutral-100');
      // fetch errors from server to populate the list
      if (historyErrorsList) {
        historyErrorsList.innerHTML = '<li class="text-gray-500 animate-pulse">Cargando errores...</li>';
        fetch('/api/history_errors')
          .then(r => r.ok ? r.json() : [])
          .then(data => {
            if (Array.isArray(data) && data.length > 0) {
              historyErrorsList.innerHTML = data.map(e => `<li class="py-2 border-b border-neutral-100 dark:border-neutral-800"><div class=\"text-xs text-neutral-500\">${e.timestamp || ''}</div><div class=\"text-sm font-medium\">${e.message}</div></li>`).join('');
            } else {
              historyErrorsList.innerHTML = '<li class="text-gray-500">No hay errores registrados.</li>';
            }
          })
          .catch(err => {
            historyErrorsList.innerHTML = '<li class="text-red-500">Error cargando errores</li>';
            console.error(err)
          })
      }
    } else {
      if (historyErrorsList) historyErrorsList.classList.add('hidden');
      if (historyMovementsList) historyMovementsList.classList.remove('hidden');
      if (btnTabErrors) btnTabErrors.classList.remove('bg-neutral-100');
      if (btnTabMovements) btnTabMovements.classList.add('bg-neutral-100');
    }
  }

  function showStatusDetails(details) {
    // populate errors list
    if (!historyModal || !historyErrorsList) {
      alert(details.join('\n'))
      return
    }
    historyErrorsList.innerHTML = details.map(d => `<li>${typeof d === 'string' ? d : (d.message || JSON.stringify(d))}</li>`).join('');
    openHistoryModal('errors');
  }

  // Asociación de eventos
  if (btnRefresh) btnRefresh.addEventListener('click', manualRefresh);
  if (btnShowHistory) btnShowHistory.addEventListener('click', () => openHistoryModal('movements'));
  if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', closeHistoryModal);
  if (btnTabErrors) btnTabErrors.addEventListener('click', () => activateTab('errors'));
  if (btnTabMovements) btnTabMovements.addEventListener('click', () => { activateTab('movements'); fetchHistory(); });

  // Inicialización automática
  fetchSystemStatus();
  setInterval(fetchSystemStatus, 30000);   // Actualiza estado cada 30s
  setInterval(updateTimestampText, 10000); // Actualiza etiqueta cada 10s
});
