// ===========================================================
// Sistema Weigence - Ventas.js (Paginación)
// Basado en la lógica de Inventario.js
// ===========================================================

const Ventas = {
  state: {
    page: 1,
    pageSize: 10,
    rows: [],
    filteredRows: []
  },

  init() {
    this.cacheDOM();
    this.refreshRows();
    this.bindEvents();
    // Aplicar paginación inicial
    this.applyPagination();
    console.info("✅ Ventas: paginación inicializada correctamente");
  },

  cacheDOM() {
    this.pageSel = document.getElementById('ventasPageSize');
    this.pagePrev = document.getElementById('ventasPrevPage');
    this.pageNext = document.getElementById('ventasNextPage');
    this.pageStats = document.getElementById('ventasPageStats');
    this.table = document.getElementById('ventasTable');
  },

  bindEvents() {
    // Cambio de tamaño de página
    this.pageSel?.addEventListener('change', () => {
      this.state.pageSize = parseInt(this.pageSel.value) || 10;
      this.state.page = 1;
      this.applyPagination();
    });

    // Botón página anterior
    this.pagePrev?.addEventListener('click', () => {
      if (this.state.page > 1) {
        this.state.page--;
        this.applyPagination();
      }
    });

    // Botón página siguiente
    this.pageNext?.addEventListener('click', () => {
      const total = this.state.filteredRows.length;
      const pages = Math.max(1, Math.ceil(total / this.state.pageSize));
      if (this.state.page < pages) {
        this.state.page++;
        this.applyPagination();
      }
    });
  },

  refreshRows() {
    // Actualiza la lista de filas desde el DOM
    this.state.rows = Array.from(document.querySelectorAll('.venta-row'));
    this.state.filteredRows = [...this.state.rows];
    console.log(`📊 Total de ventas cargadas: ${this.state.rows.length}`);
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

    // Mostrar solo las filas de la página actual
    for (let i = start; i < end; i++) {
      if (this.state.filteredRows[i]) {
        this.state.filteredRows[i].style.display = '';
      }
    }

    // Actualizar estadísticas de paginación
    if (this.pageStats) {
      this.pageStats.textContent = total ? `${start + 1}–${end} de ${total}` : '0–0 de 0';
    }

    // Actualizar estado de botones de navegación
    if (this.pagePrev) {
      this.pagePrev.disabled = this.state.page === 1;
      this.pagePrev.style.opacity = this.state.page === 1 ? '0.5' : '1';
      this.pagePrev.style.cursor = this.state.page === 1 ? 'not-allowed' : 'pointer';
    }

    if (this.pageNext) {
      this.pageNext.disabled = this.state.page >= pages;
      this.pageNext.style.opacity = this.state.page >= pages ? '0.5' : '1';
      this.pageNext.style.cursor = this.state.page >= pages ? 'not-allowed' : 'pointer';
    }

    console.log(`📄 Página ${this.state.page}/${pages} - Mostrando ${start + 1} a ${end} de ${total}`);
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  Ventas.init();
});
