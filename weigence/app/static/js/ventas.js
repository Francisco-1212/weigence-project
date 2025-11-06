// ===========================================================
// Sistema Weigence - Ventas.js (Paginación y Filtros)
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
    // Forzar paginación inicial después de que todo el DOM esté listo
    setTimeout(() => this.applyPagination(), 0);
    console.info("Ventas: paginación inicializada");
  },

  cacheDOM() {
    this.pageSel = document.getElementById('ventasPageSize');
    this.pagePrev = document.getElementById('ventasPrevPage');
    this.pageNext = document.getElementById('ventasNextPage');
    this.pageStats = document.getElementById('ventasPageStats');
    this.rows = Array.from(document.querySelectorAll('.venta-row'));
  },

  bindEvents() {
    this.pageSel?.addEventListener('change', () => {
      this.state.pageSize = parseInt(this.pageSel.value) || 10;
      this.state.page = 1;
      this.applyPagination();
    });
    this.pagePrev?.addEventListener('click', () => {
      if (this.state.page > 1) { this.state.page--; this.applyPagination(); }
    });
    this.pageNext?.addEventListener('click', () => {
      const total = this.state.filteredRows.length;
      const pages = Math.max(1, Math.ceil(total / this.state.pageSize));
      if (this.state.page < pages) { this.state.page++; this.applyPagination(); }
    });
  },

  refreshRows() {
    this.state.rows = Array.from(document.querySelectorAll('.venta-row'));
    this.state.filteredRows = [...this.state.rows];
    // Oculta todas las filas fuera de la primera página al cargar
    this.state.page = 1;
    this.applyPagination();
  },

  applyPagination() {
    const total = this.state.filteredRows.length;
    const size = this.state.pageSize;
    const pages = Math.max(1, Math.ceil(total / size));
    if (this.state.page > pages) this.state.page = pages;
    const start = (this.state.page - 1) * size;
    const end = Math.min(start + size, total);

    // Oculta todas las filas
    this.state.rows.forEach(r => {
      r.style.display = 'none';
    });
    // Muestra solo las filas de la página actual
    for (let i = start; i < end; i++) {
      if (this.state.filteredRows[i]) {
        this.state.filteredRows[i].style.display = '';
      }
    }

    if (this.pageStats) this.pageStats.textContent = total ? `${start+1}–${end} de ${total}` : '0–0 de 0';
  }
};

document.addEventListener('DOMContentLoaded', () => Ventas.init());
