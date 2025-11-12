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
    filteredRows: [],
    shelfMap: {}
  },

  // -------------------- Inicialización --------------------
  init() {
    this.state.shelfMap = this.normalizarMapa(window.CATEGORIA_ESTANTES || {});
    this.cacheDOM();
    this.bindEvents();
    this.setupDropdowns();
    this.setupDateRange();
    this.refreshRows();
    this.applyPagination();
    console.info("Inventario inicializado correctamente");
  },
  
  normalizarMapa(map) {
    const normalizado = {};
    if (!map || typeof map !== 'object') return normalizado;
    Object.entries(map).forEach(([nombre, estante]) => {
      if (!nombre || !estante) return;
      normalizado[nombre.trim().toLowerCase()] = estante;
    });
    return normalizado;
  },

  calcularEstantePorInicial(inicial) {
    if (!inicial) return '';
    const letra = inicial.toUpperCase();
    if ('ABC'.includes(letra)) return 'E01';
    if ('DEF'.includes(letra)) return 'E02';
    if ('GHIJ'.includes(letra)) return 'E03';
    if ('KLMNO'.includes(letra)) return 'E04';
    if ('PQRS'.includes(letra)) return 'E05';
    if ('TUVWXYZ'.includes(letra)) return 'E06';
    return '';
  },

  obtenerEstantePorCategoria(nombre) {
    if (!nombre) return '';
    const clave = nombre.trim().toLowerCase();
    if (!clave) return '';
    if (this.state.shelfMap[clave]) return this.state.shelfMap[clave];

    const estante = this.calcularEstantePorInicial(clave[0]);
    if (estante) this.state.shelfMap[clave] = estante;
    return estante;
  },

  configurarAsignacionEstante(container) {
    if (!container) return;
    const selectorCategoria = container.querySelector('select[name="categoria"], input[name="categoria"]');
    const inputEstante = container.querySelector('input[name="id_estante"]');

    const actualizar = () => {
      if (!inputEstante) return;
      const nombreCategoria = selectorCategoria ? selectorCategoria.value : '';
      inputEstante.value = this.obtenerEstantePorCategoria(nombreCategoria) || '';
    };

    selectorCategoria?.addEventListener('change', actualizar);
    selectorCategoria?.addEventListener('input', actualizar);
    actualizar();
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
  // Manejo de los botones de filtro de estado
    const filtroBtns = document.querySelectorAll('.filtro-btn'); // Seleccionar todos los botones de filtro
  if (filtroBtns) {
    filtroBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        // Remover clases activas de todos los botones
        filtroBtns.forEach(b => {
          b.classList.remove('bg-[var(--primary-color)]', 'text-white');
          b.classList.add('bg-[var(--card-bg-light)]', 'dark:bg-[var(--card-bg-dark)]', 'text-neutral-900', 'dark:text-neutral-100');
        });

        // Agregar clases activas al botón seleccionado
        btn.classList.remove('bg-[var(--card-bg-light)]', 'dark:bg-[var(--card-bg-dark)]', 'text-neutral-900', 'dark:text-neutral-100');
        btn.classList.add('bg-[var(--primary-color)]', 'text-white');

        // Filtrar las filas de productos según el estado seleccionado
        const status = btn.getAttribute('data-status');
        this.filterByStatus(status);
      });
    });
  }
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

  // -------------------- Filtrado y Paginación --------------------

filterByStatus(status) {
  const productRows = document.querySelectorAll('.product-row');
  console.log(`Estado seleccionado: ${status}`);

  // Limpiar cualquier filtro previo de paginación
  this.state.filteredRows = [];

  productRows.forEach(row => {
    const stock = parseInt(row.getAttribute('data-stock'), 10);

    let shouldShow = false;

    if (status === 'todos') {
      shouldShow = true;
    } else if (status === 'agotado' && stock === 0) {
      shouldShow = true;
    } else if (status === 'bajo' && stock > 0 && stock < 10) {
      shouldShow = true;
    } else if (status === 'normal' && stock >= 10) {
      shouldShow = true;
    }

    // Aplicar visibilidad usando classList en lugar de style.display
    if (shouldShow) {
      row.classList.remove('hidden');
      this.state.filteredRows.push(row);
    } else {
      row.classList.add('hidden');
    }
  });

  // Actualizar la paginación
  this.state.page = 1;
  this.applyPagination();
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
        this.configurarAsignacionEstante(this.modalContent);
    this.modal.classList.remove('hidden');
  },

  saveNew(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    data.stock = parseInt(data.stock);
    data.peso = parseFloat(data.peso);
    data.precio_unitario = parseFloat(data.precio_unitario);
    data.id_estante = this.obtenerEstantePorCategoria(data.categoria);


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
    if (!this.state.current.id_estante) {
      this.state.current.id_estante = this.obtenerEstantePorCategoria(this.state.current.categoria);
    }
    this.modalTitle.textContent = `Detalles: ${producto.nombre}`;
    this.modalContent.innerHTML = this.templates.details(this.state.current);
    this.modal.classList.remove('hidden');
  },

  editProduct() {
    const p = this.state.current;
    if (!p) return;
    this.modalTitle.textContent = `Editar Producto: ${p.nombre}`;
    this.modalContent.innerHTML = this.templates.formEdit(p);
    this.configurarAsignacionEstante(this.modalContent);
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
      codigo_estante: this.state.current.codigo_estante || this.state.current.d_estante || '',
      d_estante: this.state.current.codigo_estante || this.state.current.d_estante || '',
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
            <label class="block text-sm font-medium mb-1">Estante asignado</label>
            <input type="text" name="id_estante" readonly placeholder="Asignado automáticamente" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
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
            <p><span class="font-medium">Estante:</span> ${p.codigo_estante || p.d_estante || 'N/A'}</p>
            <p><span class="font-medium">Estante:</span> ${p.id_estante || 'N/A'}</p>
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
            <input type="text" name="d_estante" value="${p.codigo_estante || p.d_estante || ''}" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100" disabled>
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
async function actualizarGraficoProyeccion(dias = 90) {
  try {
    const res = await fetch(`/api/proyeccion_consumo?dias=${dias}`);
    const data = await res.json();

    if (!Array.isArray(data) || !data.length) {
      console.warn("No hay datos de consumo.");
      return;
    }

    // --- Normaliza datos: rellena días faltantes con 0
    const fechas = data.map(d => d.fecha);
    const unidades = data.map(d => d.unidades);
    const map = {};
    data.forEach(d => (map[d.fecha] = d.unidades));

    const start = new Date(fechas[0]);
    const end = new Date(fechas.at(-1));
    const fechasContinuas = [];
    const unidadesContinuas = [];

    for (let f = new Date(start); f <= end; f.setDate(f.getDate() + 1)) {
      const key = f.toISOString().split("T")[0];
      fechasContinuas.push(key);
      unidadesContinuas.push(map[key] || 0);
    }

    // --- Promedio y proyección (7 días futuros)
    const promedio =
      unidadesContinuas.reduce((a, b) => a + b, 0) / unidadesContinuas.length;
    const ultFecha = new Date(fechasContinuas.at(-1));
    const futuras = Array.from({ length: 7 }, (_, i) => {
      const f = new Date(ultFecha);
      f.setDate(f.getDate() + i + 1);
      return f.toISOString().split("T")[0];
    });
    const proyeccion = Array(7).fill(promedio.toFixed(1));

    // --- Limpia el gráfico anterior
    const ctx = document.getElementById("chartProyeccion").getContext("2d");
    if (window.chartProyeccion) window.chartProyeccion.destroy();

    // --- Configura datasets adaptativos
    const datasets = [
      {
        label: "Consumo real",
        data: unidadesContinuas,
        borderColor: "#38bdf8",
        backgroundColor: "rgba(56,189,248,0.08)",
        tension: 0.35,
        fill: true,
        pointRadius: unidadesContinuas.length === 1 ? 6 : 3,
        pointHoverRadius: 7,
      },
    ];

    if (unidadesContinuas.length > 1) {
      datasets.push({
        label: "Proyección (7 días)",
        data: [...Array(unidadesContinuas.length).fill(null), ...proyeccion],
        borderColor: "#a855f7",
        borderDash: [6, 4],
        tension: 0.3,
        pointRadius: 0,
      });
    }

    // --- Render Chart
    window.chartProyeccion = new Chart(ctx, {
      type: "line",
      data: {
        labels: [...fechasContinuas, ...futuras],
        datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            ticks: {
              color: "#9CA3AF",
              autoSkip: true,
              maxRotation: 45,
              callback: function (val, i, ticks) {
                return i % Math.ceil(ticks.length / 6) === 0
                  ? this.getLabelForValue(val)
                  : "";
              },
            },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
          y: {
            beginAtZero: true,
            suggestedMax: Math.max(...unidadesContinuas, promedio) + 2,
            ticks: { color: "#9CA3AF" },
            grid: { color: "rgba(255,255,255,0.05)" },
          },
        },
        plugins: {
          legend: { labels: { color: "#E5E7EB", boxWidth: 12 } },
          tooltip: {
            backgroundColor: "#1E293B",
            titleColor: "#F9FAFB",
            bodyColor: "#CBD5E1",
            callbacks: {
              label: ctx =>
                `${ctx.dataset.label}: ${ctx.parsed.y} unidades`,
            },
          },
        },
      },
    });
  } catch (err) {
    console.error("Error al generar gráfico:", err);
  }
}

document.addEventListener("DOMContentLoaded", () =>
  actualizarGraficoProyeccion(90)
);

// endpoints inventario
const WeigenceMonitor = {
  async init() {
    await this.actualizarTodo();
    setInterval(() => this.actualizarTodo(), 60000); // refresco cada 60 s
  },

  async actualizarTodo() {
    this.actualizarEstantes();
    this.actualizarAlertas();
    this.actualizarProyeccion();
  },

  // -------------------- 1. Monitoreo de estantes --------------------
  async actualizarEstantes() {
    try {
      const res = await fetch("/api/estantes_estado");
      const data = await res.json();
      if (!Array.isArray(data)) return;

      const contenedor = document.querySelector("#monitoreo-estantes");
      if (!contenedor) return;
      contenedor.innerHTML = "";

      data.forEach(e => {
        const color =
          e.estado === "critico"
            ? "red"
            : e.estado === "advertencia"
            ? "orange"
            : e.estado === "estable"
            ? "green"
            : "gray";

        contenedor.insertAdjacentHTML(
          "beforeend",
          `
          <div class="border border-${color}-400/50 bg-${color}-400/10 rounded-md p-3 animate-fadeIn">
            <div class="flex justify-between items-center mb-2">
              <span class="font-bold">Estante ${e.id_estante}</span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-${color}-200 text-${color}-800">${e.estado}</span>
            </div>
            <p class="text-sm mb-1">Ocupación: ${e.ocupacion_pct || 0}%</p>
            <div class="w-full bg-gray-200 dark:bg-neutral-700 rounded-full h-2.5 mb-2">
              <div class="bg-${color}-500 h-2.5 rounded-full" style="width:${Math.min(e.ocupacion_pct || 0, 100)}%"></div>
            </div>
            <p class="text-sm">Peso: ${e.peso_actual} kg / ${e.peso_maximo} kg</p>
          </div>`
        );
      });
    } catch (err) {
      console.error("Error monitoreo estantes:", err);
    }
  },

  // -------------------- 2. Alertas y acciones sugeridas --------------------
  async actualizarAlertas() {
    try {
      const res = await fetch("/api/alertas_activas");
      const data = await res.json();
      if (!Array.isArray(data)) return;

      const cont = document.querySelector("#alertas-sugeridas");
      if (!cont) return;
      cont.innerHTML = "";

      data.slice(0, 3).forEach(a => {
        const color =
          a.tipo_color === "rojo"
            ? "red"
            : a.tipo_color === "amarilla"
            ? "yellow"
            : "blue";
        cont.insertAdjacentHTML(
          "beforeend",
          `
          <div class="flex items-start gap-3 p-3 rounded-md bg-${color}-400/10 border border-${color}-400/30 animate-fadeIn">
            <span class="material-symbols-outlined text-${color}-500 mt-0.5">${a.icono || "warning"}</span>
            <div>
              <p class="font-medium text-sm">${a.titulo || "Alerta"}</p>
              <p class="text-xs mb-1 text-neutral-600 dark:text-neutral-400">${a.descripcion}</p>
              <button data-id="${a.id}" class="resolver-alerta text-xs font-bold text-[var(--primary-color)] hover:underline">Marcar resuelta</button>
            </div>
          </div>`
        );
      });

      cont.querySelectorAll(".resolver-alerta").forEach(b =>
        b.addEventListener("click", () => this.resolverAlerta(b.dataset.id))
      );
    } catch (err) {
      console.error("Error alertas:", err);
    }
  },

  async resolverAlerta(id) {
    try {
      await fetch(`/api/alertas/${id}/estado`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ estado: "resuelto" }),
      });
      this.actualizarAlertas();
    } catch (e) {
      console.error("Error resolviendo alerta:", e);
    }
  },

  // -------------------- 3. Proyección de consumo --------------------
  async actualizarProyeccion() {
    try {
      const res = await fetch("/api/proyeccion_consumo");
      const data = await res.json();
      if (!Array.isArray(data) || !data.length) {
        console.warn("Sin datos de consumo.");
        return;
      }

      const svg = document.querySelector("#grafico-proyeccion");
      if (!svg) return;

      const max = Math.max(...data.map(d => Number(d.consumo) || 0)) || 1; // evita división por 0
      const puntos = data
        .map((d, i) => {
          const x = 30 + i * 25;
          const y = 170 - (Number(d.consumo) / max) * 120;
          return `${x},${y}`;
        })
        .join(" L ");

      svg.querySelector("path#linea")?.setAttribute("d", `M ${puntos}`);
    } catch (err) {
      console.error("Error proyección:", err);
    }
  }
};
WeigenceMonitor.actualizarSVG = async function () {
  try {
    const res = await fetch("/api/estantes_estado");
    const data = await res.json();
    const svg = document.getElementById("svg-almacen");
    if (!svg) return;

    const estantes = Array.isArray(data) ? data : [];
    svg.innerHTML = "";

    const ns = "http://www.w3.org/2000/svg";
    const columns = 3;
    const spacingX = 150;
    const spacingY = 180;
    const offsetX = 40;
    const offsetY = 40;
    const shelfWidth = 116;
    const shelfHeight = 150;
    const accentWidth = 10;

    const total = estantes.length;
    const effectiveColumns = Math.min(columns, Math.max(1, total)) || 1;
    const rows = Math.max(1, Math.ceil((total || 1) / columns));

    const viewWidth = offsetX * 2 + shelfWidth + spacingX * (effectiveColumns - 1);
    const viewHeight = offsetY * 2 + shelfHeight + spacingY * (rows - 1);

    svg.setAttribute("viewBox", `0 0 ${viewWidth} ${viewHeight}`);
    svg.setAttribute("preserveAspectRatio", "xMidYMid meet");

    const backdrop = document.createElementNS(ns, "rect");
    backdrop.setAttribute("x", "0");
    backdrop.setAttribute("y", "0");
    backdrop.setAttribute("width", viewWidth);
    backdrop.setAttribute("height", viewHeight);
    backdrop.setAttribute("fill", "transparent");
    svg.appendChild(backdrop);

    const stateColors = {
      critico: "#ef4444",
      advertencia: "#f59e0b",
      estable: "#22c55e",
    };

    const stateLabels = {
      critico: "Crítico",
      advertencia: "Advertencia",
      estable: "Estable",
    };

    const modules = [];

    estantes.forEach((shelf, index) => {
      const rawState = (shelf.estado || "").toString().toLowerCase();
      const state = stateColors[rawState] ? rawState : "estable";
      const stateColor = stateColors[state];

      const col = index % columns;
      const row = Math.floor(index / columns);
      const posX = offsetX + col * spacingX;
      const posY = offsetY + row * spacingY;

      const ocupacion = Math.max(0, Math.min(100, Number(shelf.ocupacion_pct) || 0));
      const ocupacionTexto = ocupacion % 1 === 0 ? `${ocupacion}` : ocupacion.toFixed(1);
      const pesoActual = Number(shelf.peso_actual ?? 0);
      const pesoMaximo = Number(shelf.peso_maximo ?? 0);

      const group = document.createElementNS(ns, "g");
      group.setAttribute("transform", `translate(${posX}, ${posY})`);
      group.setAttribute("class", `shelf-module shelf-${state}`);
      group.setAttribute("tabindex", "0");
      group.dataset.id = shelf.id_estante || "";
      group.dataset.estado = state;
      group.dataset.ocupacion = ocupacionTexto;
      group.dataset.pesoActual = pesoActual;
      group.dataset.pesoMaximo = pesoMaximo;
      group.style.setProperty("--shelf-state", stateColor);

      const frame = document.createElementNS(ns, "rect");
      frame.setAttribute("x", "0");
      frame.setAttribute("y", "0");
      frame.setAttribute("width", shelfWidth);
      frame.setAttribute("height", shelfHeight);
      frame.setAttribute("class", "rack-frame");
      group.appendChild(frame);

      const inner = document.createElementNS(ns, "rect");
      inner.setAttribute("x", "6");
      inner.setAttribute("y", "6");
      inner.setAttribute("width", shelfWidth - 12);
      inner.setAttribute("height", shelfHeight - 12);
      inner.setAttribute("class", "rack-inner");
      group.appendChild(inner);

      const shadow = document.createElementNS(ns, "rect");
      shadow.setAttribute("x", "6");
      shadow.setAttribute("y", "6");
      shadow.setAttribute("width", shelfWidth - accentWidth - 18);
      shadow.setAttribute("height", shelfHeight - 18);
      shadow.setAttribute("class", "rack-shadow");
      group.appendChild(shadow);

      const sideShade = document.createElementNS(ns, "rect");
      sideShade.setAttribute("x", shelfWidth - 24);
      sideShade.setAttribute("y", "12");
      sideShade.setAttribute("width", "12");
      sideShade.setAttribute("height", shelfHeight - 24);
      sideShade.setAttribute("class", "rack-side-shade");
      group.appendChild(sideShade);

      const accentTrack = document.createElementNS(ns, "rect");
      accentTrack.setAttribute("x", shelfWidth - accentWidth - 6);
      accentTrack.setAttribute("y", "12");
      accentTrack.setAttribute("width", accentWidth);
      accentTrack.setAttribute("height", shelfHeight - 24);
      accentTrack.setAttribute("class", "rack-accent-track");
      group.appendChild(accentTrack);

      const accentTrackHeight = shelfHeight - 24;
      const accentHeight = Math.max(0, (accentTrackHeight * ocupacion) / 100);
      const accentFillHeight = ocupacion > 0 ? Math.max(4, accentHeight) : 0;
      const accentFill = document.createElementNS(ns, "rect");
      accentFill.setAttribute("x", shelfWidth - accentWidth - 6);
      accentFill.setAttribute("y", 12 + (accentTrackHeight - accentFillHeight));
      accentFill.setAttribute("width", accentWidth);
      accentFill.setAttribute("height", accentFillHeight);
      accentFill.setAttribute("class", "rack-accent-fill");
      group.appendChild(accentFill);

      const foot = document.createElementNS(ns, "rect");
      foot.setAttribute("x", "6");
      foot.setAttribute("y", shelfHeight - 8);
      foot.setAttribute("width", shelfWidth - 12);
      foot.setAttribute("height", "6");
      foot.setAttribute("class", "rack-foot");
      group.appendChild(foot);

      const levelCount = 3;
      for (let i = 1; i <= levelCount; i += 1) {
        const y = 12 + (i * (shelfHeight - 24)) / (levelCount + 1);
        const level = document.createElementNS(ns, "line");
        level.setAttribute("x1", "14");
        level.setAttribute("x2", shelfWidth - accentWidth - 14);
        level.setAttribute("y1", y);
        level.setAttribute("y2", y);
        level.setAttribute("class", "rack-level");
        group.appendChild(level);
      }

      const label = document.createElementNS(ns, "text");
      label.setAttribute("x", "14");
      label.setAttribute("y", "28");
      label.setAttribute("class", "rack-label");
      label.setAttribute("text-anchor", "start");
      label.textContent = `Estante ${shelf.id_estante || ""}`.trim();
      group.appendChild(label);

      const meta = document.createElementNS(ns, "text");
      meta.setAttribute("x", "14");
      meta.setAttribute("y", shelfHeight - 18);
      meta.setAttribute("class", "rack-meta");
      meta.setAttribute("text-anchor", "start");
      meta.textContent = `${ocupacionTexto}% ocupación`;
      group.appendChild(meta);

      svg.appendChild(group);
      modules.push({ node: group, data: shelf });
    });

    requestAnimationFrame(() => {
      modules.forEach(({ node }, index) => {
        setTimeout(() => node.classList.add("is-visible"), index * 55);
      });
    });

    let tooltip = document.getElementById("tooltip-estante");
    if (!tooltip) {
      tooltip = document.createElement("div");
      tooltip.id = "tooltip-estante";
      tooltip.className = "hidden absolute z-50 rounded-lg px-3 py-2 pointer-events-none";
      svg.parentElement.appendChild(tooltip);
    } else {
      tooltip.classList.add("hidden");
    }

    const formatNumber = value =>
      new Intl.NumberFormat("es-CL", { maximumFractionDigits: 1 }).format(Number(value ?? 0));

    const showTooltip = (module, evt) => {
      if (!module) return;
      tooltip.classList.remove("hidden");

      const svgRect = svg.getBoundingClientRect();
      let x;
      let y;

      if (evt && typeof evt.clientX === "number") {
        x = evt.clientX - svgRect.left;
        y = evt.clientY - svgRect.top;
      } else {
        const bounds = module.getBoundingClientRect();
        x = bounds.left + bounds.width / 2 - svgRect.left;
        y = bounds.top + bounds.height / 2 - svgRect.top;
      }

      tooltip.style.left = `${x + 18}px`;
      tooltip.style.top = `${y - tooltip.offsetHeight / 2}px`;

      const tipRect = tooltip.getBoundingClientRect();
      if (tipRect.right > window.innerWidth - 16) {
        tooltip.style.left = `${x - tipRect.width - 18}px`;
      }
      if (tipRect.top < 0) {
        tooltip.style.top = `${y + 12}px`;
      }

      tooltip.innerHTML = `
        <div class="tooltip-line"><span class="tooltip-key">Estante</span><span>${module.dataset.id || "-"}</span></div>
        <div class="tooltip-line"><span class="tooltip-key">Ocupación</span><span>${module.dataset.ocupacion || 0}%</span></div>
        <div class="tooltip-line"><span class="tooltip-key">Peso</span><span>${formatNumber(module.dataset.pesoActual)} / ${formatNumber(module.dataset.pesoMaximo)} kg</span></div>
        <div class="tooltip-line"><span class="tooltip-key">Estado</span><span>${stateLabels[module.dataset.estado] || stateLabels.estable}</span></div>`;
    };

    const hideTooltip = () => tooltip.classList.add("hidden");

    modules.forEach(({ node, data }) => {
      node.addEventListener("mousemove", evt => showTooltip(node, evt));
      node.addEventListener("focus", () => showTooltip(node));
      node.addEventListener("mouseleave", hideTooltip);
      node.addEventListener("blur", hideTooltip);
      node.addEventListener("click", () => WeigenceMonitor.mostrarDetalleEstante?.(data));
      node.addEventListener("keydown", evt => {
        if (evt.key === "Enter" || evt.key === " ") {
          evt.preventDefault();
          WeigenceMonitor.mostrarDetalleEstante?.(data);
        }
      });
    });
  } catch (err) {
    console.error("Error SVG almacén:", err);
  }
};

// detalle en modal
WeigenceMonitor.mostrarDetalleEstante = function (estante) {
  const html = `
    <div class="p-5">
      <h2 class="text-xl font-semibold mb-3">Estante ${estante.id_estante}</h2>
      <p><b>Ocupación:</b> ${estante.ocupacion_pct}%</p>
      <p><b>Peso actual:</b> ${estante.peso_actual} kg</p>
      <p><b>Peso máximo:</b> ${estante.peso_maximo} kg</p>
      <p><b>Estado:</b> ${estante.estado}</p>
      <div class="mt-4 text-sm text-neutral-600 dark:text-neutral-400">Haz clic fuera para cerrar.</div>
    </div>
  `;
  const modal = document.createElement("div");
  modal.className =
    "fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[999]";
  modal.innerHTML = `<div class='bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] rounded-lg border border-gray-300 dark:border-neutral-700 shadow-lg w-80'>${html}</div>`;
  modal.addEventListener("click", e => {
    if (e.target === modal) modal.remove();
  });
  document.body.appendChild(modal);
};
async function cargarAlertas() {
  try {
    await fetch("/api/generar_alertas_basicas");
    const res = await fetch("/api/alertas_activas");
    const alertas = await res.json();
    const cont = document.getElementById("alertas-sugeridas");
    if (!cont) return;

    cont.innerHTML = "";

    const maxAlertas = 3;
    alertas.slice(0, maxAlertas).forEach(a => {
      const color =
        a.tipo_color === "rojo"
          ? "border-l-4 border-red-500 bg-red-500/10"
          : a.tipo_color === "amarilla"
          ? "border-l-4 border-yellow-500 bg-yellow-500/10"
          : "border-l-4 border-blue-500 bg-blue-500/10";

      const iconoColor =
        a.tipo_color === "rojo"
          ? "text-red-500"
          : a.tipo_color === "amarilla"
          ? "text-yellow-500"
          : "text-blue-500";

      const card = document.createElement("div");
      card.className = `flex items-start gap-3 p-3 rounded-md ${color} shadow-sm hover:shadow-md transition-all`;
      card.innerHTML = `
        <span class="material-symbols-outlined ${iconoColor} mt-0.5">${a.icono}</span>
        <div class="flex flex-col">
          <p class="font-semibold text-sm text-neutral-900 dark:text-neutral-100">${a.titulo}</p>
          <p class="text-xs text-neutral-600 dark:text-neutral-400 mb-1">${a.descripcion}</p>
          <button data-id="${a.id}" class="text-xs font-bold text-[var(--primary-color)] hover:underline">
            Marcar como revisada
          </button>
        </div>
      `;
      cont.appendChild(card);
    });

    // Eliminar scroll y ajustar altura
    cont.style.maxHeight = "none";
    cont.style.overflowY = "visible";

    // Eventos "Marcar como revisada"
    cont.querySelectorAll("button[data-id]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        await fetch(`/api/alertas/marcar_revisada/${id}`, { method: "POST" });
        cargarAlertas();
      });
    });
  } catch (err) {
    console.error("Error cargando alertas:", err);
  }
}

// Ejecutar al cargar la página
document.addEventListener("DOMContentLoaded", cargarAlertas);
// Refrescar cada 20 segundos
setInterval(cargarAlertas, 20000);


// integrar con el resto
const oldUpdate = WeigenceMonitor.actualizarTodo.bind(WeigenceMonitor);
WeigenceMonitor.actualizarTodo = async function () {
  await oldUpdate();
  this.actualizarSVG();
};

// Activar al cargar
document.addEventListener("DOMContentLoaded", () => WeigenceMonitor.init());

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', ()=>Inventario.init());


