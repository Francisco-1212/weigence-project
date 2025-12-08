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
    // Actualizar badge
    actualizarBadgeNotificaciones();
  });
  
  // Función para actualizar el badge de notificaciones
  window.actualizarBadgeNotificaciones = function() {
    fetch('/api/notificaciones', { cache: 'no-store' })
      .then(r => r.json())
      .then(data => {
        const count = data.length || 0;
        const badge = document.querySelector('.badge-count');
        const badgeNotif = document.querySelector('.badge-notif');
        
        if (count > 0) {
          if (badge) {
            badge.textContent = count;
            badge.classList.remove('hidden');
          }
          if (badgeNotif) {
            badgeNotif.textContent = count;
          }
        } else {
          if (badge) badge.classList.add('hidden');
          if (badgeNotif) badgeNotif.textContent = '0';
        }
      })
      .catch(err => console.error('Error actualizando badge:', err));
  };
  
  // Función para recargar el contenido del panel sin recargar toda la página
  window.recargarPanelNotificaciones = function() {
    const panel = document.getElementById('notification-panel');
    const panelAbierto = panel && !panel.classList.contains('translate-x-full');
    
    // Actualizar badge siempre
    actualizarBadgeNotificaciones();
    
    // SOLO recargar contenido si el panel está ABIERTO (para evitar parpadeos)
    if (!panelAbierto) return;
    
    // Si el panel está abierto, recargar su contenido
    if (panelAbierto) {
      fetch('/api/notificaciones', { cache: 'no-store' })
        .then(r => r.json())
        .then(data => {
          // Buscar el contenedor de notificaciones
          const container = document.querySelector('.space-y-2');
          if (!container) return;
          
          // Si no hay notificaciones
          if (!data || data.length === 0) {
            container.innerHTML = '<div class="text-center py-8 text-gray-500"><p>No hay notificaciones</p></div>';
            return;
          }
          
          // Recrear notificaciones
          const htmlNotifs = data.map(notif => {
            const colorMap = {
              'rojo': 'bg-red-100 border-red-300 text-red-800',
              'amarillo': 'bg-yellow-100 border-yellow-300 text-yellow-800',
              'verde': 'bg-green-100 border-green-300 text-green-800',
              'azul': 'bg-blue-100 border-blue-300 text-blue-800'
            };
            const colorClass = colorMap[notif.tipo_color] || 'bg-gray-100 border-gray-300 text-gray-800';
            
            let html = `<div class="notif-item border-l-4 p-3 rounded ${colorClass} cursor-pointer hover:shadow-md transition" data-id="${notif.id}">`;
            html += `<div class="flex items-start gap-2">`;
            html += `<span class="text-lg">⚠️</span>`;
            html += `<div class="flex-1"><div class="font-semibold">${notif.titulo}</div>`;
            if (notif.descripcion) html += `<div class="text-sm mt-1">${notif.descripcion}</div>`;
            if (notif.fecha_formateada) html += `<div class="text-xs opacity-75 mt-1">${notif.fecha_formateada}</div>`;
            html += `</div><button class="notif-discard text-red-500 hover:text-red-700 font-bold" aria-label="Descartar">✕</button></div>`;
            if (notif.detalle) {
              html += `<div class="notif-detalle hidden mt-2 text-sm border-t pt-2">${notif.detalle}`;
              if (notif.enlace) html += `<a href="${notif.enlace}" class="text-blue-600 hover:underline ml-2">Ver más</a>`;
              html += `</div>`;
            }
            html += `</div>`;
            return html;
          }).join('');
          
          container.innerHTML = htmlNotifs;
        })
        .catch(err => console.error('Error recargando panel:', err));
    }
  };
  
  // Actualizar badge cada 15 segundos
  setInterval(actualizarBadgeNotificaciones, 15000);
  
  // Recargar panel cada 30 segundos
  setInterval(recargarPanelNotificaciones, 30000);
});
