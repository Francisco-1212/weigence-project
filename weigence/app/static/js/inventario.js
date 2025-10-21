// ===========================================================
// Sistema Weigence - Inventario.js (Refactor Senior)
// ===========================================================

const Inventario = {
  state: {
    current: null,
    editMode: false,
    filters: { category: '', status: '', dateStart: '', dateEnd: '' },
    page: 1,
    pageSize: 10,
    rows: [],
    filteredRows: []
  },

  // -------------------- Inicialización --------------------
  init() {
    this.cacheDOM();
    this.bindEvents();
    this.setupDropdowns();
    this.setupDateRange();
    this.refreshRows();
    this.applyPagination();
    console.info("Inventario inicializado correctamente");
  },

  cacheDOM() {
    this.modal = document.getElementById('productModal');
    this.modalContent = document.getElementById('modalContent');
    this.modalTitle = document.getElementById('modalTitle');
    this.btnAdd = document.getElementById('addProductBtn');
    this.btnExport = document.getElementById('exportBtn');
    this.btnCloseTop = document.getElementById('closeModal');
    this.searchInput = document.getElementById('searchInput');
    this.pageSel = document.getElementById('pageSize');
    this.pagePrev = document.getElementById('prevPage');
    this.pageNext = document.getElementById('nextPage');
    this.pageStats = document.getElementById('pageStats');
    this.table = document.getElementById('productTable');
    this.rows = Array.from(document.querySelectorAll('.product-row'));
  },

  bindEvents() {
    // Búsqueda con debounce
    if (this.searchInput) {
      let timer;
      this.searchInput.addEventListener('input', () => {
        clearTimeout(timer);
        timer = setTimeout(() => this.filterAndPaginate(), 300);
      });
    }

    // Botones globales
    this.btnAdd?.addEventListener('click', () => this.showAddForm());
    this.btnExport?.addEventListener('click', () => this.exportVisible());
    this.btnCloseTop?.addEventListener('click', () => this.closeModal());

    // Cerrar con tecla ESC y clic fuera
    document.addEventListener('keydown', e => { if (e.key === 'Escape') this.closeModal(); });
    this.modal?.addEventListener('click', e => { if (e.target === this.modal) this.closeModal(); });

    // Delegación dentro del modal
    this.modalContent?.addEventListener('click', e => this.modalActions(e));
    this.modalContent?.addEventListener('submit', e => this.modalSubmits(e));

    // Botones "gestionar" en cada fila
    document.querySelectorAll('.gestionar-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const producto = JSON.parse(btn.dataset.producto || '{}');
        this.showDetails(producto);
      });
    });

    // Paginación
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

  // -------------------- Modal Actions --------------------
  modalActions(e) {
    const btn = e.target.closest('button');
    if (!btn) return;

    if (btn.classList.contains('btn-cerrar')) return this.closeModal();
    if (btn.classList.contains('btn-cancelar') || btn.classList.contains('btn-cancelar-add'))
      return this.state.current ? this.showDetails(this.state.current) : this.closeModal();
    if (btn.classList.contains('btn-editar')) return this.editProduct();
    if (btn.classList.contains('btn-eliminar') && this.state.current)
      return this.deleteProduct(this.state.current.idproducto);
  },

  modalSubmits(e) {
    e.preventDefault();
    if (e.target.id === 'addProductForm') return this.saveNew(e.target);
    if (e.target.id === 'editProductForm') return this.saveEdit(e.target);
  },

  // -------------------- CRUD --------------------
  showAddForm() {
    if (!this.modalContent) return;
    this.modalTitle.textContent = "Agregar Nuevo Producto";
    this.modalContent.innerHTML = this.templates.formAdd();
    this.modal.classList.remove('hidden');
  },

  saveNew(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    data.stock = parseInt(data.stock);
    data.peso = parseFloat(data.peso);
    data.precio_unitario = parseFloat(data.precio_unitario);

    const btn = form.querySelector('button[type="submit"]');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Guardando...';

    fetch('/api/productos/agregar', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify(data)
    })
    .then(r=>r.json())
    .then(res=>{
      if(res.success){
        console.info('Producto agregado', res);
        this.closeModal();
        location.reload();
      } else {
        console.error(res.error);
        btn.disabled = false;
        btn.innerHTML = originalHTML;
      }
    })
    .catch(err=>{
      console.error('Error al agregar producto', err);
      btn.disabled = false;
      btn.innerHTML = originalHTML;
    });
  },

  showDetails(producto) {
    this.state.current = producto;
    this.modalTitle.textContent = `Detalles: ${producto.nombre}`;
    this.modalContent.innerHTML = this.templates.details(producto);
    this.modal.classList.remove('hidden');
  },

  editProduct() {
    const p = this.state.current;
    if (!p) return;
    this.modalTitle.textContent = `Editar Producto: ${p.nombre}`;
    this.modalContent.innerHTML = this.templates.formEdit(p);
  },

  saveEdit(form) {
    const fd = new FormData(form);
    const updated = {
      ...this.state.current,
      nombre: fd.get('nombre'),
      categoria: fd.get('categoria'),
      stock: parseInt(fd.get('stock')),
      peso: parseFloat(fd.get('peso')),
      descripcion: fd.get('descripcion'),
      d_estante: fd.get('d_estante'),
      modificado_por: 'Usuario Actual',
      fecha_modificacion: new Date().toLocaleString()
    };

    console.info('Actualizando producto:', updated);
    setTimeout(() => {
      this.state.current = updated;
      this.showDetails(updated);
      console.info('Producto actualizado');
    }, 400);
  },

  deleteProduct(id) {
    if (!confirm(`Eliminar producto ID: ${id}?`)) return;
    console.info(`Producto ${id} eliminado (simulado)`);
    this.closeModal();
  },

  closeModal() {
    this.modal?.classList.add('hidden');
    this.state.editMode = false;
    this.state.current = null;
  },

// -------------------- Plantillas de HTML --------------------
  templates: {
    formAdd() {
      return `
      <form id="addProductForm" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Nombre *</label>
            <input type="text" name="nombre" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Categoría *</label>
            <select name="categoria" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
              <option value="">Seleccionar categoría</option>
              <option>Antiinflamatorio</option><option>Antibiótico</option>
              <option>Suplemento</option><option>Antihistamínico</option>
              <option>Broncodilatador</option><option>Analgésico</option>
              <option>Antidiabetico</option><option>Antihipertensivo</option>
              <option>Dermocosmética</option><option>Desinfectante</option>
              <option>Primeros Auxilios</option><option>Equipamiento</option>
              <option>Higiene</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Stock *</label>
            <input type="number" name="stock" min="0" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Peso Unitario (g) *</label>
            <input type="number" name="peso" min="0" step="0.01" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Precio Unitario *</label>
            <input type="number" name="precio_unitario" min="0" step="0.01" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Estante</label>
            <input type="text" name="d_estante" placeholder="Ej: A1, B2" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Descripción</label>
          <textarea name="descripcion" rows="3" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100"></textarea>
        </div>
        <div class="flex justify-end gap-3 pt-4 border-t border-neutral-700">
          <button type="button" class="btn-cancelar-add px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md text-white">Cancelar</button>
          <button type="submit" class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-white">
            <span class="flex items-center gap-2"><span class="material-symbols-outlined text-base">add</span>Guardar</span>
          </button>
        </div>
      </form>`;
    },
    details(p) {
      return `
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div class="bg-[var(--card-bg-dark)] p-4 rounded-lg">
          <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Información Básica</h4>
          <div class="space-y-2 text-neutral-100">
            <p><span class="font-medium">ID:</span> ${p.idproducto}</p>
            <p><span class="font-medium">Nombre:</span> ${p.nombre}</p>
            <p><span class="font-medium">Categoría:</span> ${p.categoria}</p>
            <p><span class="font-medium">Stock:</span> ${p.stock}</p>
            <p><span class="font-medium">Peso:</span> ${p.peso} g</p>
            <p><span class="font-medium">Estante:</span> ${p.d_estante || 'N/A'}</p>
            <p><span class="font-medium">Descripción:</span> ${p.descripcion || '—'}</p>
          </div>
        </div>
        <div class="bg-[var(--card-bg-dark)] p-4 rounded-lg">
          <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Auditoría</h4>
          <div class="space-y-2 text-neutral-100">
            <p><span class="font-medium">Fecha de Ingreso:</span> ${p.fecha_ingreso || 'N/A'}</p>
            <p><span class="font-medium">Ingresado por:</span> ${p.ingresado_por || 'N/A'}</p>
            <p><span class="font-medium">Modificado por:</span> ${p.modificado_por || 'N/A'}</p>
            <p><span class="font-medium">Fecha de Modificación:</span> ${p.fecha_modificacion || 'N/A'}</p>
          </div>
        </div>
      </div>
      <div class="flex justify-end gap-3">
        <button class="btn-cerrar px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md text-white">Cerrar</button>
        <button class="btn-eliminar px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md text-white">Eliminar</button>
        <button class="btn-editar px-4 py-2 bg-[var(--primary-color)] hover:bg-opacity-90 rounded-md text-white">Editar</button>
      </div>`;
    },

    formEdit(p) {
      return `
      <form id="editProductForm" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Nombre *</label>
            <input type="text" name="nombre" value="${p.nombre}" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Categoría *</label>
            <input type="text" name="categoria" value="${p.categoria}" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Stock *</label>
            <input type="number" name="stock" value="${p.stock}" min="0" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Peso (g) *</label>
            <input type="number" name="peso" value="${p.peso}" min="0" step="0.01" required class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Estante</label>
            <input type="text" name="d_estante" value="${p.d_estante || ''}" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Descripción</label>
          <textarea name="descripcion" rows="3" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">${p.descripcion || ''}</textarea>
        </div>
        <div class="flex justify-end gap-3 pt-4 border-t border-neutral-700">
          <button type="button" class="btn-cancelar px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-md text-white">Cancelar</button>
          <button type="submit" class="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-md text-white">Guardar</button>
        </div>
      </form>`;
    }
  },

  // -------------------- Filtros --------------------
  setupDropdowns() {
    const catBtn = document.getElementById('categoryBtn');
    const catDrop = document.getElementById('categoryDropdown');
    const catOptions = document.querySelectorAll('.category-option');
    const statBtn = document.getElementById('statusBtn');
    const statDrop = document.getElementById('statusDropdown');
    const statOptions = document.querySelectorAll('.status-option');

    catBtn?.addEventListener('click', e => {
      e.stopPropagation();
      catDrop?.classList.toggle('hidden');
      statDrop?.classList.add('hidden');
    });
    statBtn?.addEventListener('click', e => {
      e.stopPropagation();
      statDrop?.classList.toggle('hidden');
      catDrop?.classList.add('hidden');
    });

    catOptions.forEach(opt => {
      opt.addEventListener('click', () => {
        this.state.filters.category = opt.dataset.category || '';
        catBtn.querySelector('p').textContent = opt.textContent.trim();
        catDrop?.classList.add('hidden');
        this.filterAndPaginate();
      });
    });
    statOptions.forEach(opt => {
      opt.addEventListener('click', () => {
        this.state.filters.status = opt.dataset.status || '';
        statBtn.querySelector('p').textContent = opt.textContent.trim();
        statDrop?.classList.add('hidden');
        this.filterAndPaginate();
      });
    });

    document.addEventListener('click', () => {
      catDrop?.classList.add('hidden');
      statDrop?.classList.add('hidden');
      document.getElementById('dateRangeDropdown')?.classList.add('hidden');
    });
  },

  setupDateRange() {
    const btn = document.getElementById('dateRangeBtn');
    const drop = document.getElementById('dateRangeDropdown');
    const start = document.getElementById('startDate');
    const end = document.getElementById('endDate');
    const apply = document.getElementById('applyDateRange');
    const clear = document.getElementById('clearDateRange');

    btn?.addEventListener('click', e => {
      e.stopPropagation();
      drop?.classList.toggle('hidden');
      start?.focus();
    });
    apply?.addEventListener('click', () => {
      if (!start.value || !end.value) return alert('Seleccione ambas fechas');
      if (new Date(start.value) > new Date(end.value)) return alert('Fechas inválidas');
      this.state.filters.dateStart = start.value;
      this.state.filters.dateEnd = end.value;
      btn.querySelector('p').textContent = `${this.formatDate(start.value)} → ${this.formatDate(end.value)}`;
      drop?.classList.add('hidden');
      this.filterAndPaginate();
    });
    clear?.addEventListener('click', () => {
      start.value = end.value = '';
      this.state.filters.dateStart = this.state.filters.dateEnd = '';
      btn.querySelector('p').textContent = 'Rango de Fechas';
      drop?.classList.add('hidden');
      this.filterAndPaginate();
    });
  },

  formatDate(d) {
    const dt = new Date(d);
    return `${dt.getDate().toString().padStart(2,'0')}/${(dt.getMonth()+1).toString().padStart(2,'0')}/${dt.getFullYear()}`;
  },

  // -------------------- Filtro + Paginación --------------------
  refreshRows() {
    this.state.rows = Array.from(document.querySelectorAll('.product-row'));
    this.state.filteredRows = [...this.state.rows];
  },

  filterAndPaginate() {
    const f = this.state.filters;
    const term = this.searchInput?.value.toLowerCase() || '';
    this.state.filteredRows = this.state.rows.filter(row => {
      const name = row.dataset.name || '';
      const cat = row.dataset.category || '';
      const stock = parseInt(row.dataset.stock) || 0;
      const dateStr = row.dataset.date || '';
      let visible = true;

      if (term && !name.includes(term)) visible = false;
      if (f.category && cat !== f.category) visible = false;
      if (f.status) {
        if (f.status === 'normal' && stock < 10) visible = false;
        if (f.status === 'bajo' && (stock >= 10 || stock === 0)) visible = false;
        if (f.status === 'agotado' && stock !== 0) visible = false;
      }
      if (f.dateStart && f.dateEnd && dateStr) {
        const d = new Date(dateStr.split('T')[0]);
        const s = new Date(f.dateStart);
        const e = new Date(f.dateEnd); e.setHours(23,59,59,999);
        if (isNaN(d) || d < s || d > e) visible = false;
      }
      row.style.display = visible ? '' : 'none';
      return visible;
    });
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

    this.state.rows.forEach(r => r.style.display = 'none');
    for (let i = start; i < end; i++) this.state.filteredRows[i].style.display = '';

    if (this.pageStats) this.pageStats.textContent = total ? `${start+1}–${end} de ${total}` : '0–0 de 0';
  },

  // -------------------- Exportar --------------------
  exportVisible() {
    const rows = this.state.filteredRows;
    if (rows.length === 0) return alert('No hay datos para exportar');
    let csv = 'ID,Código,Nombre,Categoría,Stock,Peso,Estado,Fecha\n';
    rows.forEach(r => {
      const cells = r.querySelectorAll('td');
      const arr = Array.from(cells).slice(0,7).map(c => `"${c.textContent.trim()}"`);
      csv += arr.join(',') + '\n';
    });
    const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'inventario_'+new Date().toISOString().split('T')[0]+'.csv';
    document.body.appendChild(link); link.click(); link.remove();
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', ()=>Inventario.init());
