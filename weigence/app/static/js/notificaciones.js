document.addEventListener('DOMContentLoaded', () => {
  const notificationButton = document.getElementById('notification-button');
  const notificationPanel = document.getElementById('notification-panel');
  const closeNotificationPanel = document.getElementById('close-notification-panel');
  const notificationBackdrop = document.getElementById('notification-backdrop');

  if (!notificationButton || !notificationPanel) return;

  // --- Abrir panel ---
  notificationButton.addEventListener('click', () => {
    notificationPanel.classList.remove('translate-x-full');
    notificationBackdrop.classList.remove('opacity-0', 'pointer-events-none');
  });

  // --- Cerrar panel ---
  [closeNotificationPanel, notificationBackdrop].forEach(el => {
    el?.addEventListener('click', () => {
      notificationPanel.classList.add('translate-x-full');
      notificationBackdrop.classList.add('opacity-0', 'pointer-events-none');
    });
  });

  // --- Manejo interno de notificaciones ---
  notificationPanel.addEventListener('click', e => {
    const item = e.target.closest('.notif-item');
    if (!item) return;

    // Si hace clic en el botón "Descartar"
    if (e.target.classList.contains('notif-discard')) {
      e.stopPropagation();
      item.classList.add('opacity-0', 'translate-x-2');
      setTimeout(() => item.remove(), 250);
      return;
    }

    // Si hace clic en la notificación y tiene detalle oculto
    const detalle = item.querySelector('.notif-detalle');
    if (detalle) {
      const isHidden = detalle.classList.contains('hidden');
      document.querySelectorAll('.notif-detalle').forEach(d => d.classList.add('hidden'));
      if (isHidden) detalle.classList.remove('hidden');
    }

    // Si no hay detalle, crear un botón "Descartar" dinámico
    if (!detalle) {
      let temp = item.querySelector('.temp-discard');
      if (!temp) {
        temp = document.createElement('div');
        temp.className = 'temp-discard mt-2 flex justify-end';
        temp.innerHTML = `
          <button class="notif-discard text-xs text-gray-500 hover:text-red-500 transition" aria-label="Descartar notificación">
            Descartar
          </button>`;
        item.appendChild(temp);
      } else {
        temp.remove();
      }
    }
  });

  // Marcar todas como leídas
  document.getElementById('mark-all-read')?.addEventListener('click', () => {
    document.querySelectorAll('.notif-item').forEach(item => {
      item.classList.add('opacity-0');
      setTimeout(() => item.remove(), 250);
    });
  });
});
