document.addEventListener('DOMContentLoaded', function() {
  const movimientos = window.MOVIMIENTOS || [];
  const items = document.querySelectorAll('.timeline-item');
  const detalle = document.getElementById('detalle-contextual');

  items.forEach((item, idx) => {
    item.setAttribute('draggable', 'true');
    item.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', idx);
      detalle.classList.add('ring-4', 'ring-primary-400', 'dark:ring-primary-600', 'scale-[1.02]');
    });
    item.addEventListener('dragend', () => {
      detalle.classList.remove('ring-4', 'ring-primary-400', 'dark:ring-primary-600', 'scale-[1.02]');
    });
  });

  // Muestra detalles de un movimiento en el panel derecho
  window.mostrarDetalleMovimiento = function (event) {
    event.preventDefault();
    const idx = event.dataTransfer.getData('text/plain');
    const mov = movimientos[idx];
    detalle.classList.remove('ring-4', 'ring-primary-400', 'dark:ring-primary-600', 'scale-[1.02]');

    if (!mov) {
      detalle.innerHTML = `
        <div class="flex flex-col items-center justify-center py-10 text-neutral-400">
          <span class="material-symbols-outlined text-6xl mb-3">error_outline</span>
          <p class="text-sm font-medium">No se pudo cargar el detalle del movimiento.</p>
        </div>`;
      return;
    }

    detalle.innerHTML = `
      <div class="p-6 text-left animate-fadeIn">
        <h3 class="text-lg font-bold mb-3 flex items-center gap-2 text-neutral-900 dark:text-neutral-100">
          <span class="material-symbols-outlined text-primary-600 dark:text-primary-400">list_alt</span>
          Detalle del Movimiento
        </h3>
        <div class="space-y-1 text-sm">
          <p><b>Producto:</b> ${mov.producto}</p>
          <p><b>Estantería:</b> ${mov.ubicacion}</p>
          <p><b>Usuario:</b> ${mov.rut_usuario || 'Desconocido'} / ${mov.usuario_nombre || 'Sin nombre'}</p>
          <p><b>Tipo:</b> ${mov.tipo_evento}</p>
          <p><b>Cantidad:</b> ${mov.cantidad} kg</p>
          <p><b>Fecha y hora:</b> ${mov.timestamp}</p>
          <p><b>Observación:</b> ${mov.observacion || 'Sin observación'}</p>
        </div>
      </div>`;
  };
});
