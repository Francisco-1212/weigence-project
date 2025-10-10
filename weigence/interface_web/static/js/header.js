const notificationButton = document.getElementById('notification-button');
const notificationPanel = document.getElementById('notification-panel');
const closeNotificationPanel = document.getElementById('close-notification-panel');
const notificationBackdrop = document.getElementById('notification-backdrop');

notificationButton.addEventListener('click', () => {
  notificationPanel.classList.remove('translate-x-full');
  notificationBackdrop.classList.remove('opacity-0','pointer-events-none');
});

closeNotificationPanel.addEventListener('click', () => {
  notificationPanel.classList.add('translate-x-full');
  notificationBackdrop.classList.add('opacity-0','pointer-events-none');
});

notificationBackdrop.addEventListener('click', () => {
  notificationPanel.classList.add('translate-x-full');
  notificationBackdrop.classList.add('opacity-0','pointer-events-none');
});

// Delegación de eventos para toggle de detalle y botón descartar
notificationPanel.addEventListener('click', e => {
  // Evento descartar: si se hizo clic en el botón descartar
  if (e.target.classList.contains('notif-discard')) {
    e.stopPropagation();
    const item = e.target.closest('.notif-item');
    if (item) item.remove();
    return;
  }

  // Evento toggle detalle: si hizo clic en alguna notificación
  const item = e.target.closest('.notif-item');
  if (!item) return;

  const detalle = item.querySelector('.notif-detalle');
  if (detalle) detalle.classList.toggle('hidden');
});


