// ===========================================================
// Sistema Weigence - Alertas.js
// ===========================================================

const Alertas = {
  state: {
    page: 1,
    pageSize: 10,
    rows: [],
    filteredRows: [],
    alertaActual: null,
    filtrosActivos: {
      estado: '',
      tipo: '',
      fechaDesde: '',
      fechaHasta: ''
    }
  },

  init() {
    this.cacheDOM();
    this.refreshRows();
    this.bindEvents();
    this.bindFiltros();
    this.applyPagination();
    console.info("✅ Alertas: Sistema inicializado correctamente");
  },

  cacheDOM() {
    this.table = document.getElementById('alertasTable');
    this.modal = document.getElementById('modal-gestionar-alerta');
    this.alertasCounter = document.getElementById('alertas-counter');
    
    // Paginación
    this.pageSel = document.getElementById('alertasPageSize');
    this.pagePrev = document.getElementById('alertasPrevPage');
    this.pageNext = document.getElementById('alertasNextPage');
    this.pageStats = document.getElementById('alertasPageStats');
    
    // Elementos de filtros
    this.filtroEstado = document.getElementById('filtro-estado');
    this.filtroTipo = document.getElementById('filtro-tipo');
    this.filtroFechaDesde = document.getElementById('filtro-fecha-desde');
    this.filtroFechaHasta = document.getElementById('filtro-fecha-hasta');
    this.btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
    this.filtrosActivosContainer = document.getElementById('filtros-activos');
    this.filtrosActivosChips = document.getElementById('filtros-activos-chips');
    
    // Elementos del modal
    this.modalTitulo = document.getElementById('modal-titulo');
    this.modalDescripcion = document.getElementById('modal-descripcion');
    this.modalProducto = document.getElementById('modal-producto');
    this.modalUsuario = document.getElementById('modal-usuario');
    this.modalFecha = document.getElementById('modal-fecha');
    this.modalTipo = document.getElementById('modal-tipo');
    this.modalEstado = document.getElementById('modal-estado');
    
    // Botón exportar
    this.btnExportar = document.getElementById('btn-exportar-alertas');
  },

  bindEvents() {
    // Paginación
    this.pageSel?.addEventListener('change', () => {
      this.state.pageSize = parseInt(this.pageSel.value) || 10;
      this.state.page = 1;
      this.applyPagination();
    });

    this.pagePrev?.addEventListener('click', () => {
      if (this.state.page > 1) {
        this.state.page--;
        this.applyPagination();
      }
    });

    this.pageNext?.addEventListener('click', () => {
      const total = this.state.filteredRows.length;
      const pages = Math.max(1, Math.ceil(total / this.state.pageSize));
      if (this.state.page < pages) {
        this.state.page++;
        this.applyPagination();
      }
    });

    // Cerrar modal
    document.querySelectorAll('.close-modal-alerta').forEach(btn => {
      btn.addEventListener('click', () => this.cerrarModal());
    });

    // Cerrar al hacer click fuera
    this.modal?.addEventListener('click', (e) => {
      if (e.target === this.modal) {
        this.cerrarModal();
      }
    });

    // Cerrar con ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modal && !this.modal.classList.contains('hidden')) {
        this.cerrarModal();
      }
    });

    // Botón exportar
    this.btnExportar?.addEventListener('click', () => this.exportarAlertas());

    // Botones gestionar (delegación de eventos)
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn-gestionar-alerta');
      if (btn) {
        const alertaId = btn.dataset.alertaId;
        this.abrirModal(alertaId);
      }
    });
  },

  bindFiltros() {
    // Aplicar filtros al cambiar cualquier campo
    [this.filtroEstado, this.filtroTipo].forEach(select => {
      select?.addEventListener('change', () => {
        this.aplicarFiltros();
      });
    });

    [this.filtroFechaDesde, this.filtroFechaHasta].forEach(input => {
      input?.addEventListener('change', () => {
        this.aplicarFiltros();
      });
    });

    // Limpiar filtros
    this.btnLimpiarFiltros?.addEventListener('click', () => {
      this.limpiarFiltros();
    });
  },

  refreshRows() {
    this.state.rows = Array.from(document.querySelectorAll('.alerta-row'));
    this.state.filteredRows = [...this.state.rows];
    this.actualizarContador();
  },

  aplicarFiltros() {
    this.state.filtrosActivos = {
      estado: this.filtroEstado?.value || '',
      tipo: this.filtroTipo?.value || '',
      fechaDesde: this.filtroFechaDesde?.value || '',
      fechaHasta: this.filtroFechaHasta?.value || ''
    };

    this.state.filteredRows = this.state.rows.filter(row => {
      // Filtro por estado
      if (this.state.filtrosActivos.estado) {
        const estado = row.dataset.estado;
        if (estado !== this.state.filtrosActivos.estado) {
          return false;
        }
      }

      // Filtro por tipo
      if (this.state.filtrosActivos.tipo) {
        const tipo = row.dataset.tipo;
        if (tipo !== this.state.filtrosActivos.tipo) {
          return false;
        }
      }

      // Filtro por fecha desde
      if (this.state.filtrosActivos.fechaDesde) {
        const fecha = new Date(row.dataset.fecha);
        const fechaDesde = new Date(this.state.filtrosActivos.fechaDesde);
        if (fecha < fechaDesde) {
          return false;
        }
      }

      // Filtro por fecha hasta
      if (this.state.filtrosActivos.fechaHasta) {
        const fecha = new Date(row.dataset.fecha);
        const fechaHasta = new Date(this.state.filtrosActivos.fechaHasta);
        fechaHasta.setHours(23, 59, 59, 999);
        if (fecha > fechaHasta) {
          return false;
        }
      }

      return true;
    });

    this.actualizarContador();
    this.mostrarFiltrosActivos();
    this.actualizarEstadisticas();
    
    // Resetear a primera página y aplicar paginación
    this.state.page = 1;
    this.applyPagination();
  },

  limpiarFiltros() {
    // Limpiar inputs
    if (this.filtroEstado) this.filtroEstado.value = '';
    if (this.filtroTipo) this.filtroTipo.value = '';
    if (this.filtroFechaDesde) this.filtroFechaDesde.value = '';
    if (this.filtroFechaHasta) this.filtroFechaHasta.value = '';

    // Resetear estado
    this.state.filtrosActivos = {
      estado: '',
      tipo: '',
      fechaDesde: '',
      fechaHasta: ''
    };

    this.state.filteredRows = [...this.state.rows];

    // Ocultar chips de filtros activos
    if (this.filtrosActivosContainer) {
      this.filtrosActivosContainer.classList.add('hidden');
    }

    this.actualizarContador();
    this.actualizarEstadisticas();
    
    // Resetear a primera página y aplicar paginación
    this.state.page = 1;
    this.applyPagination();
  },

  mostrarFiltrosActivos() {
    if (!this.filtrosActivosChips || !this.filtrosActivosContainer) return;

    const chips = [];
    const filtros = this.state.filtrosActivos;

    // Chip de estado
    if (filtros.estado) {
      const estadoTexto = filtros.estado === 'pendiente' ? 'Pendiente' : 'Resuelto';
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
          <span class="material-symbols-outlined text-sm">toggle_on</span>
          ${estadoTexto}
        </span>
      `);
    }

    // Chip de tipo
    if (filtros.tipo) {
      const tipoTexto = filtros.tipo === 'rojo' ? '🔴 Rojo' : '🟡 Amarillo';
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
          <span class="material-symbols-outlined text-sm">label</span>
          ${tipoTexto}
        </span>
      `);
    }

    // Chip de fecha
    if (filtros.fechaDesde || filtros.fechaHasta) {
      let textoFecha = '';
      if (filtros.fechaDesde && filtros.fechaHasta) {
        textoFecha = `${filtros.fechaDesde} a ${filtros.fechaHasta}`;
      } else if (filtros.fechaDesde) {
        textoFecha = `Desde ${filtros.fechaDesde}`;
      } else {
        textoFecha = `Hasta ${filtros.fechaHasta}`;
      }
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
          <span class="material-symbols-outlined text-sm">calendar_today</span>
          ${textoFecha}
        </span>
      `);
    }

    if (chips.length > 0) {
      this.filtrosActivosChips.innerHTML = chips.join('');
      this.filtrosActivosContainer.classList.remove('hidden');
    } else {
      this.filtrosActivosContainer.classList.add('hidden');
    }
  },

  actualizarContador() {
    if (!this.alertasCounter) return;

    const total = this.state.filteredRows.length;
    const totalOriginal = this.state.rows.length;

    if (total === totalOriginal) {
      this.alertasCounter.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 mr-2 animate-pulse"></span>
        ${total} alertas
      `;
    } else {
      this.alertasCounter.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 mr-2 animate-pulse"></span>
        ${total} de ${totalOriginal} alertas
      `;
    }
  },

  actualizarEstadisticas() {
    const pendientes = this.state.filteredRows.filter(row => row.dataset.estado === 'pendiente').length;
    const resueltas = this.state.filteredRows.filter(row => row.dataset.estado === 'resuelto').length;
    const total = this.state.filteredRows.length;

    const totalEl = document.getElementById('total-alertas');
    const pendientesEl = document.getElementById('alertas-pendientes');
    const resueltasEl = document.getElementById('alertas-resueltas');

    if (totalEl) totalEl.textContent = total;
    if (pendientesEl) pendientesEl.textContent = pendientes;
    if (resueltasEl) resueltasEl.textContent = resueltas;
  },

  applyPagination() {
    const total = this.state.filteredRows.length;
    const size = this.state.pageSize;
    const pages = Math.max(1, Math.ceil(total / size));
    
    // Ajustar página si está fuera de rango
    if (this.state.page > pages) {
      this.state.page = pages;
    }
    
    const start = (this.state.page - 1) * size;
    const end = Math.min(start + size, total);

    // Ocultar todas las filas primero
    this.state.rows.forEach(row => {
      row.style.display = 'none';
    });

    // Manejar fila de "No hay alertas"
    const noAlertasRow = document.getElementById('noAlertasRow');
    
    if (total === 0) {
      if (noAlertasRow) {
        noAlertasRow.style.display = '';
        const mensajeCell = noAlertasRow.querySelector('td p');
        if (mensajeCell) {
          if (this.state.rows.length === 0) {
            mensajeCell.textContent = 'No hay alertas registradas';
          } else {
            mensajeCell.textContent = 'No se encontraron alertas con los filtros seleccionados';
          }
        }
      }
    } else {
      if (noAlertasRow) {
        noAlertasRow.style.display = 'none';
      }
      
      // Mostrar solo las filas de la página actual
      for (let i = start; i < end; i++) {
        if (this.state.filteredRows[i]) {
          this.state.filteredRows[i].style.display = '';
        }
      }
    }

    // Actualizar estadísticas de paginación
    if (this.pageStats) {
      this.pageStats.textContent = `${total > 0 ? start + 1 : 0}–${end} de ${total}`;
    }

    // Actualizar estado de botones de navegación
    if (this.pagePrev) {
      this.pagePrev.disabled = this.state.page === 1;
      this.pagePrev.classList.toggle('opacity-50', this.state.page === 1);
    }

    if (this.pageNext) {
      this.pageNext.disabled = this.state.page >= pages;
      this.pageNext.classList.toggle('opacity-50', this.state.page >= pages);
    }
  },

  abrirModal(alertaId) {
    const row = this.state.rows.find(r => r.dataset.id == alertaId);
    if (!row) {
      console.error('❌ Alerta no encontrada:', alertaId);
      return;
    }

    this.state.alertaActual = {
      id: alertaId,
      titulo: row.dataset.titulo,
      descripcion: row.dataset.descripcion,
      tipo: row.dataset.tipo,
      estado: row.dataset.estado,
      fecha: row.dataset.fecha,
      producto: row.dataset.producto,
      usuario: row.dataset.usuario
    };

    // Llenar modal
    this.modalTitulo.textContent = this.state.alertaActual.titulo;
    this.modalDescripcion.textContent = this.state.alertaActual.descripcion;
    this.modalProducto.textContent = this.state.alertaActual.producto;
    this.modalUsuario.textContent = this.state.alertaActual.usuario;
    
    // Formatear fecha
    const fecha = new Date(this.state.alertaActual.fecha);
    this.modalFecha.textContent = fecha.toLocaleDateString('es-CL', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });

    // Tipo con emoji
    const tipoTexto = this.state.alertaActual.tipo === 'rojo' ? '🔴 Crítico' : '🟡 Advertencia';
    this.modalTipo.textContent = tipoTexto;

    this.modalEstado.value = this.state.alertaActual.estado;

    if (this.modal) {
      this.modal.classList.remove('hidden');
    }
  },

  cerrarModal() {
    this.modal?.classList.add('hidden');
    this.state.alertaActual = null;
  },

  async guardarCambios() {
    if (!this.state.alertaActual) return;

    const nuevoEstado = this.modalEstado.value;
    const alertaId = this.state.alertaActual.id;

    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

      const response = await fetch(`/api/actualizar_alerta/${alertaId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
          estado: nuevoEstado
        })
      });

      const data = await response.json();

      if (data.success) {
        mostrarNotificacion('Alerta actualizada correctamente', 'success');
        
        // Actualizar la fila en el DOM
        const row = this.state.rows.find(r => r.dataset.id == alertaId);
        if (row) {
          row.dataset.estado = nuevoEstado;
          
          // Actualizar el badge de estado en la tabla
          const estadoBadge = row.querySelector('td:nth-child(5) span');
          if (estadoBadge) {
            estadoBadge.className = `inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-xs font-medium
              ${nuevoEstado === 'pendiente' 
                ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300'
                : 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'}`;
            
            const icon = nuevoEstado === 'pendiente' ? 'schedule' : 'check_circle';
            estadoBadge.innerHTML = `
              <span class="material-symbols-outlined text-sm">${icon}</span>
              ${nuevoEstado.charAt(0).toUpperCase() + nuevoEstado.slice(1)}
            `;
          }
        }

        this.actualizarEstadisticas();
        this.cerrarModal();
      } else {
        mostrarNotificacion(data.error || 'Error al actualizar la alerta', 'error');
      }
    } catch (error) {
      console.error('❌ Error al guardar cambios:', error);
      mostrarNotificacion('Error de conexión al actualizar la alerta', 'error');
    }
  },

  exportarAlertas() {
    try {
      const alertas = this.state.filteredRows;
      
      if (alertas.length === 0) {
        mostrarNotificacion('No hay alertas para exportar', 'warning');
        return;
      }

      // Preparar datos CSV
      const headers = ['ID', 'Título', 'Descripción', 'Producto', 'Usuario', 'Tipo', 'Estado', 'Fecha'];
      const rows = [];

      alertas.forEach(row => {
        const tipo = row.dataset.tipo === 'rojo' ? 'Crítico' : 'Advertencia';
        const estado = row.dataset.estado.charAt(0).toUpperCase() + row.dataset.estado.slice(1);
        const fecha = new Date(row.dataset.fecha).toLocaleDateString('es-CL');

        rows.push([
          row.dataset.id,
          row.dataset.titulo,
          row.dataset.descripcion,
          row.dataset.producto,
          row.dataset.usuario,
          tipo,
          estado,
          fecha
        ]);
      });

      // Generar CSV
      let csv = headers.join(',') + '\n';
      rows.forEach(row => {
        csv += row.map(cell => {
          const cellStr = String(cell);
          if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
            return '"' + cellStr.replace(/"/g, '""') + '"';
          }
          return cellStr;
        }).join(',') + '\n';
      });

      // Agregar resumen
      const pendientes = alertas.filter(r => r.dataset.estado === 'pendiente').length;
      const resueltas = alertas.filter(r => r.dataset.estado === 'resuelto').length;
      csv += '\n';
      csv += 'RESUMEN\n';
      csv += `Total de Alertas,${rows.length}\n`;
      csv += `Pendientes,${pendientes}\n`;
      csv += `Resueltas,${resueltas}\n`;

      // Descargar archivo
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const fecha = new Date().toISOString().split('T')[0];
      link.href = URL.createObjectURL(blob);
      link.download = `alertas_${fecha}.csv`;
      link.click();

      mostrarNotificacion(`Reporte exportado: ${rows.length} alertas`, 'success');
    } catch (error) {
      console.error('❌ Error al exportar reporte:', error);
      mostrarNotificacion('Error al exportar el reporte', 'error');
    }
  }
};

// ===========================================================
// Función de Notificación
// ===========================================================

function mostrarNotificacion(mensaje, tipo = 'info') {
  const notificacion = document.createElement('div');
  notificacion.className = `fixed top-4 right-4 z-[9999] px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-[400px]`;
  
  const estilos = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-amber-500 text-white',
    info: 'bg-blue-500 text-white'
  };
  
  const iconos = {
    success: 'check_circle',
    error: 'error',
    warning: 'warning',
    info: 'info'
  };
  
  notificacion.className += ` ${estilos[tipo] || estilos.info}`;
  
  notificacion.innerHTML = `
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined">${iconos[tipo] || iconos.info}</span>
      <span class="font-medium">${mensaje}</span>
    </div>
  `;
  
  document.body.appendChild(notificacion);
  
  setTimeout(() => {
    notificacion.style.transform = 'translateX(0)';
  }, 10);
  
  setTimeout(() => {
    notificacion.style.transform = 'translateX(400px)';
    setTimeout(() => {
      notificacion.remove();
    }, 300);
  }, 3000);
}

// ===========================================================
// Inicializar
// ===========================================================

document.addEventListener('DOMContentLoaded', () => {
  try {
    Alertas.init();
  } catch (error) {
    console.error('❌ Error al inicializar Alertas:', error);
  }
});
