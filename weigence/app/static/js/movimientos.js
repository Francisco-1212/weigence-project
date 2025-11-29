/**
 * Movimientos - Filtro de fechas
 */

document.addEventListener('DOMContentLoaded', () => {
  const filtroFechaBtns = document.querySelectorAll('.filtro-fecha-btn');
  const movimientosRows = document.querySelectorAll('.timeline-item');

  if (filtroFechaBtns.length > 0) {
    filtroFechaBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const rango = btn.dataset.rango;
        aplicarFiltroFecha(rango);
        
        // Actualizar estilo activo
        filtroFechaBtns.forEach(b => b.classList.remove('filtro-activo'));
        btn.classList.add('filtro-activo');
      });
    });
    
    // Inicializar con "Hoy" por defecto
    filtroFechaBtns[0]?.classList.add('filtro-activo');
    aplicarFiltroFecha('hoy');
  }

  function aplicarFiltroFecha(rango) {
    const ahora = new Date();
    let fechaInicio;

    switch(rango) {
      case 'hoy':
        fechaInicio = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
        break;
      case 'semana':
        fechaInicio = new Date(ahora);
        fechaInicio.setDate(ahora.getDate() - 7);
        break;
      case 'mes':
        fechaInicio = new Date(ahora);
        fechaInicio.setMonth(ahora.getMonth() - 1);
        break;
      default:
        fechaInicio = null;
    }

    // Filtrar filas por fecha
    let visibles = 0;
    if (fechaInicio) {
      movimientosRows.forEach(row => {
        const fechaTexto = row.dataset.fecha;
        if (fechaTexto) {
          const fechaMovimiento = new Date(fechaTexto);
          if (fechaMovimiento >= fechaInicio) {
            row.style.display = '';
            visibles++;
          } else {
            row.style.display = 'none';
          }
        }
      });
    } else {
      // Mostrar todo
      movimientosRows.forEach(row => {
        row.style.display = '';
        visibles++;
      });
    }

    // Actualizar contador si existe
    const contador = document.getElementById('movimientos-count');
    if (contador) {
      contador.textContent = visibles;
    }
  }
});
