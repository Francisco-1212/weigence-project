document.addEventListener('DOMContentLoaded', () => {
  const lastUpdateTimestampEl = document.getElementById('last-update-timestamp');
  const statusIconEl = document.getElementById('status-icon');
  const statusTextEl = document.getElementById('status-text');
  const systemStatusEl = document.getElementById('system-status');
  const activityIndicatorEl = document.getElementById('activity-indicator');
  const notificationsIndicatorEl = document.getElementById('notifications-indicator');
  const notificationsCountEl = document.getElementById('notifications-count');
  const btnRefresh = document.getElementById('btn-refresh');
  const btnShowHistory = document.getElementById('btn-show-history');
  const historyModal = document.getElementById('history-modal');
  const historyList = document.getElementById('history-list');
  const closeHistoryBtn = document.getElementById('close-history');

  const states = {
    online: { icon: 'check_circle', colorClass: 'text-green-500', text: 'Sistema en línea' },
    warning: { icon: 'warning', colorClass: 'text-yellow-500', text: 'Problemas de conexión' },
    offline: { icon: 'error', colorClass: 'text-red-500', text: 'Sistema desconectado' },
    syncing: { icon: 'sync', colorClass: 'text-primary-600 animate-spin', text: 'Sincronizando...' },
  };

  let lastUpdate = null;

  function updateStatus(stateKey) {
    const state = states[stateKey];
    if (!state) return;

    if (!statusIconEl || !statusTextEl || !systemStatusEl || !activityIndicatorEl) return;

    statusIconEl.textContent = state.icon;
    statusIconEl.className = `material-symbols-outlined ${state.colorClass}`;
    statusTextEl.textContent = state.text;
    statusTextEl.className = state.colorClass;

    systemStatusEl.classList.remove('hidden');
    activityIndicatorEl.classList.toggle('hidden', stateKey !== 'syncing');
  }

  function setLastUpdate(timestamp) {
    lastUpdate = new Date(timestamp);
    updateTimestampText();
  }

  function updateTimestampText() {
    if (!lastUpdate) {
      if (lastUpdateTimestampEl) lastUpdateTimestampEl.textContent = '--:--';
      return;
    }
    const now = new Date();
    const diffSec = Math.floor((now - lastUpdate) / 1000);
    if (diffSec < 60) lastUpdateTimestampEl.textContent = 'justo ahora';
    else if (diffSec < 3600) lastUpdateTimestampEl.textContent = `${Math.floor(diffSec / 60)} min(s) atrás`;
    else if (diffSec < 86400) lastUpdateTimestampEl.textContent = `${Math.floor(diffSec / 3600)} hora(s) atrás`;
    else lastUpdateTimestampEl.textContent = lastUpdate.toLocaleString();
  }

  function setNotificationsCount(count) {
    if (!notificationsIndicatorEl || !notificationsCountEl) return;
    if (count > 0) {
      notificationsCountEl.textContent = count;
      notificationsIndicatorEl.classList.remove('hidden');
    } else {
      notificationsIndicatorEl.classList.add('hidden');
    }
  }

async function fetchSystemStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) throw new Error('Error fetch status');
    const data = await res.json();

    // Forzar estado a online si el usuario está operativo
    const estado = (data.connection_state === 'online') ? 'online' : data.connection_state;

    setLastUpdate(data.last_update);
    updateStatus(estado);
    setNotificationsCount(data.important_events);
  } catch (error) {
    updateStatus('offline');
    setNotificationsCount(0);
    console.error(error);
  }
}


  async function fetchHistory() {
    try {
      const res = await fetch('/api/history');
      if (!res.ok) throw new Error('Error fetch history');
      const data = await res.json();
      if (historyList) {
        historyList.innerHTML = data.map(evt => `<li><strong>${new Date(evt.timestamp).toLocaleString()}:</strong> ${evt.message}</li>`).join('');
      }
    } catch (error) {
      if (historyList) {
        historyList.innerHTML = `<li class="text-red-500">Error cargando historial</li>`;
      }
      console.error(error);
    }
  }
  function updateTimestampText() {
  if (!lastUpdate) {
    lastUpdateTimestampEl.textContent = '--:--';
    return;
  }
  lastUpdateTimestampEl.textContent = lastUpdate.toLocaleString(undefined, {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  });
}


  async function manualRefresh() {
    updateStatus('syncing');
    try {
      const res = await fetch('/api/refresh', { method: 'POST' });
      if (!res.ok) throw new Error('Error refrescando');
      await fetchSystemStatus();
    } catch (err) {
      updateStatus('offline');
    }
  }

  if (btnRefresh) btnRefresh.addEventListener('click', manualRefresh);
  if (btnShowHistory) btnShowHistory.addEventListener('click', async () => {
    if (historyModal) historyModal.classList.remove('hidden');
    await fetchHistory();
  });
  if (closeHistoryBtn) closeHistoryBtn.addEventListener('click', () => {
    if (historyModal) historyModal.classList.add('hidden');
  });

  fetchSystemStatus();
  setInterval(fetchSystemStatus, 30000);
  setInterval(updateTimestampText, 10000);
});