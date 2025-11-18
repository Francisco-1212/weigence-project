document.addEventListener('DOMContentLoaded', () => {
  const notificationButton = document.getElementById('notification-button');
  const notificationPanel  = document.getElementById('notification-panel');
  const closeBtn           = document.getElementById('close-notification-panel');
  const backdrop           = document.getElementById('notification-backdrop');

  // precarga para evitar cachear
  fetch("/api/notificaciones", { cache: "no-store" }).catch(()=>{});

  if (!notificationButton || !notificationPanel) return;

  // Abrir
  notificationButton.addEventListener('click', () => {
    notificationPanel.classList.remove('translate-x-full');
    backdrop.classList.remove('opacity-0', 'pointer-events-none');
  });

  // Cerrar
  [closeBtn, backdrop].forEach(el => {
    el?.addEventListener('click', () => {
      notificationPanel.classList.add('translate-x-full');
      backdrop.classList.add('opacity-0', 'pointer-events-none');
    });
  });

  // Clicks dentro del panel
  notificationPanel.addEventListener('click', e => {
    const item = e.target.closest('.notif-item');
    if (!item) return;

    // Descartar individual
    if (e.target.classList.contains('notif-discard')) {
      e.stopPropagation();
      const id = item.dataset.id;
      // Optimista: ocultar primero
      item.classList.add('opacity-0', 'translate-x-2');
      setTimeout(() => item.remove(), 250);

      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

      fetch(`/api/descartar_alerta/${id}`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      }).then(r => r.json()).then(j => {
        if (!j.success) console.error('Error al descartar:', j.error);
      }).catch(err => console.error('Fallo conexión:', err));

      return;
    }

    // Toggle detalle
    const detalle = item.querySelector('.notif-detalle');
    if (detalle) {
      const isHidden = detalle.classList.contains('hidden');
      document.querySelectorAll('.notif-detalle').forEach(d => d.classList.add('hidden'));
      if (isHidden) detalle.classList.remove('hidden');
    } else {
      // Botón Descartar temporal si no hay detalle
      let temp = item.querySelector('.temp-discard');
      if (!temp) {
        temp = document.createElement('div');
        temp.className = 'temp-discard mt-2 flex justify-end';
        temp.innerHTML = `
          <button class="notif-discard text-xs text-gray-500 hover:text-red-500 transition"
                  aria-label="Descartar notificación">Descartar</button>`;
        item.appendChild(temp);
      } else {
        temp.remove();
      }
    }
  });

  // Descartar todas
  document.getElementById('mark-all-read')?.addEventListener('click', () => {
    const items = Array.from(document.querySelectorAll('.notif-item'));
    // Optimista: limpiar UI
    items.forEach(it => { it.classList.add('opacity-0'); setTimeout(() => it.remove(), 200); });
    // Enviar una por una (simple y robusto)
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    items.forEach(it => {
      const id = it.dataset.id;
      fetch(`/api/descartar_alerta/${id}`, { 
        method: 'POST', 
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        } 
      })
        .catch(()=>{});
    });
  });
});
