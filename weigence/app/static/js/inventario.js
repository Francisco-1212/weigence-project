// ===========================================================
// Sistema Weigence - Inventario.js (Refactor Senior)
// ===========================================================

const Inventario = {
  state: {
    current: null,
    editMode: false,
    filters: { 
      category: '', 
      status: '', 
      dateStart: '', 
      dateEnd: '',
      estante: '',
      ordenVencimiento: ''
    },
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
    this.toggleFiltrosBtn = document.getElementById('toggleFiltrosBtn');
    this.panelFiltros = document.getElementById('panelFiltros');
    this.filtrosChevron = document.getElementById('filtrosChevron');
    this.filtroEstante = document.getElementById('filtroEstante');
    this.filtroCategoria = document.getElementById('filtroCategoria');
    this.ordenVencimiento = document.getElementById('ordenVencimiento');
    this.limpiarFiltrosBtn = document.getElementById('limpiarFiltrosBtn');
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
        const title = btn.getAttribute('title');
        
        this.state.current = producto;
        
        if (title === 'Editar') {
          // Mostrar detalles/historial del producto
          this.showDetails(producto);
        } else if (title === 'Eliminar') {
          if (confirm(`¿Estás seguro de eliminar el producto "${producto.nombre}"?`)) {
            this.deleteProduct(producto.idproducto);
          }
        } else {
          this.showDetails(producto);
        }
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

    // Toggle panel de filtros
    this.toggleFiltrosBtn?.addEventListener('click', () => {
      const isHidden = this.panelFiltros.classList.contains('hidden');
      if (isHidden) {
        this.panelFiltros.classList.remove('hidden');
        this.filtrosChevron.style.transform = 'rotate(180deg)';
      } else {
        this.panelFiltros.classList.add('hidden');
        this.filtrosChevron.style.transform = 'rotate(0deg)';
      }
    });

    // Filtros por estante y categoria
    this.filtroEstante?.addEventListener('change', () => {
      this.state.filters.estante = this.filtroEstante.value;
      this.aplicarFiltrosCompletos();
    });

    this.filtroCategoria?.addEventListener('change', () => {
      this.state.filters.category = this.filtroCategoria.value;
      this.aplicarFiltrosCompletos();
    });

    // Ordenamiento por vencimiento
    this.ordenVencimiento?.addEventListener('change', () => {
      this.state.filters.ordenVencimiento = this.ordenVencimiento.value;
      this.aplicarFiltrosCompletos();
    });

    // Limpiar filtros
    this.limpiarFiltrosBtn?.addEventListener('click', () => {
      this.limpiarFiltros();
    });

    // Filtros de fecha (Hoy/Semana/Mes)
    const filtroFechaBtns = document.querySelectorAll('.filtro-fecha-btn');
    if (filtroFechaBtns.length > 0) {
      filtroFechaBtns.forEach(btn => {
        btn.addEventListener('click', () => {
          const rango = btn.dataset.rango;
          this.aplicarFiltroFecha(rango);
          
          // Actualizar estilo activo
          filtroFechaBtns.forEach(b => b.classList.remove('filtro-activo'));
          btn.classList.add('filtro-activo');
        });
      });
      
      // Inicializar con "Hoy" por defecto
      filtroFechaBtns[0]?.classList.add('filtro-activo');
      this.aplicarFiltroFecha('hoy');
    }
  },

  aplicarFiltroFecha(rango) {
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
    if (fechaInicio) {
      this.rows.forEach(row => {
        const fechaTexto = row.dataset.fecha; // Asumiendo que cada fila tiene data-fecha
        if (fechaTexto) {
          const fechaProducto = new Date(fechaTexto);
          if (fechaProducto >= fechaInicio) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        }
      });
    } else {
      // Mostrar todo
      this.rows.forEach(row => row.style.display = '');
    }

    this.refreshRows();
    this.filterAndPaginate();
  },

  // -------------------- Filtrado y Paginación --------------------

filterByStatus(status) {
  this.state.filters.status = status;
  this.aplicarFiltrosCompletos();
},

aplicarFiltrosCompletos() {
  const productRows = document.querySelectorAll('.product-row');
  this.state.filteredRows = [];

  let rowsArray = Array.from(productRows);

  // Aplicar filtros
  rowsArray.forEach(row => {
    const stock = parseInt(row.getAttribute('data-stock'), 10);
    const category = row.getAttribute('data-category') || '';
    const estante = row.getAttribute('data-estante') || '';
    
    let shouldShow = true;

    // Filtro por estado de stock
    if (this.state.filters.status && this.state.filters.status !== 'todos') {
      if (this.state.filters.status === 'agotado' && stock !== 0) {
        shouldShow = false;
      } else if (this.state.filters.status === 'bajo' && (stock === 0 || stock >= 10)) {
        shouldShow = false;
      } else if (this.state.filters.status === 'normal' && stock < 10) {
        shouldShow = false;
      }
    }

    // Filtro por categoria
    if (shouldShow && this.state.filters.category) {
      if (category.toLowerCase() !== this.state.filters.category.toLowerCase()) {
        shouldShow = false;
      }
    }

    // Filtro por estante
    if (shouldShow && this.state.filters.estante) {
      if (estante !== this.state.filters.estante) {
        shouldShow = false;
      }
    }

    if (shouldShow) {
      row.classList.remove('hidden');
      this.state.filteredRows.push(row);
    } else {
      row.classList.add('hidden');
    }
  });

  // Ordenar por vencimiento si esta seleccionado
  if (this.state.filters.ordenVencimiento) {
    this.ordenarPorVencimiento(this.state.filteredRows, this.state.filters.ordenVencimiento);
  }

  // Actualizar la paginación
  this.state.page = 1;
  this.applyPagination();
},

ordenarPorVencimiento(rows, orden) {
  const tbody = this.table.querySelector('tbody');
  if (!tbody) return;

  // Ordenar las filas
  rows.sort((a, b) => {
    const fechaA = a.getAttribute('data-fecha-venc');
    const fechaB = b.getAttribute('data-fecha-venc');

    // Manejar productos sin fecha de vencimiento (se colocan al final)
    if (!fechaA && !fechaB) return 0;
    if (!fechaA) return 1;
    if (!fechaB) return -1;

    const dateA = new Date(fechaA);
    const dateB = new Date(fechaB);

    if (orden === 'asc') {
      return dateA - dateB;
    } else {
      return dateB - dateA;
    }
  });

  // Reordenar en el DOM
  rows.forEach(row => {
    tbody.appendChild(row);
  });
},

limpiarFiltros() {
  // Resetear filtros en el estado
  this.state.filters = {
    category: '',
    status: 'todos',
    dateStart: '',
    dateEnd: '',
    estante: '',
    ordenVencimiento: ''
  };

  // Resetear UI
  if (this.filtroEstante) this.filtroEstante.value = '';
  if (this.filtroCategoria) this.filtroCategoria.value = '';
  if (this.ordenVencimiento) this.ordenVencimiento.value = '';

  // Resetear botones de estado
  const filtroBtns = document.querySelectorAll('.filtro-btn');
  filtroBtns.forEach(btn => {
    const status = btn.getAttribute('data-status');
    if (status === 'todos') {
      btn.classList.remove('bg-[var(--card-bg-light)]', 'dark:bg-[var(--card-bg-dark)]', 'text-neutral-900', 'dark:text-neutral-100');
      btn.classList.add('bg-[var(--primary-color)]', 'text-white');
    } else {
      btn.classList.remove('bg-[var(--primary-color)]', 'text-white');
      btn.classList.add('bg-[var(--card-bg-light)]', 'dark:bg-[var(--card-bg-dark)]', 'text-neutral-900', 'dark:text-neutral-100');
    }
  });

  // Aplicar filtros (mostrara todos)
  this.aplicarFiltrosCompletos();
},

filterByVencimiento(vencimiento) {
  const productRows = document.querySelectorAll('.product-row');
  console.log(`Vencimiento seleccionado: ${vencimiento}`);

  this.state.filteredRows = [];
  const ahora = new Date();
  ahora.setHours(0, 0, 0, 0);
  
  productRows.forEach(row => {
    const estadoVenc = row.getAttribute('data-vencimiento');
    const fechaVencStr = row.getAttribute('data-fecha-venc');
    let shouldShow = false;

    if (!fechaVencStr) {
      shouldShow = false;
    } else {
      if (vencimiento === 'vencido' && (estadoVenc === 'vencido' || estadoVenc === 'vence_hoy')) {
        shouldShow = true;
      } else if (vencimiento === 'critico' && estadoVenc === 'critico') {
        shouldShow = true;
      } else if (vencimiento === 'proximo' && estadoVenc === 'proximo') {
        shouldShow = true;
      }
    }

    if (shouldShow) {
      row.classList.remove('hidden');
      this.state.filteredRows.push(row);
    } else {
      row.classList.add('hidden');
    }
  });

  this.state.page = 1;
  this.applyPagination();
},

validarFechas(fechaElab, fechaVenc) {
  const warning = document.getElementById('fecha_warning');
  const warningText = document.getElementById('fecha_warning_text');
  
  if (!warning || !warningText) return true;

  warning.classList.add('hidden');

  if (!fechaElab && !fechaVenc) return true;

  if (fechaElab && fechaVenc) {
    const elab = new Date(fechaElab);
    const venc = new Date(fechaVenc);
    
    if (elab > venc) {
      warningText.textContent = 'La fecha de elaboración no puede ser posterior a la fecha de vencimiento';
      warning.classList.remove('hidden');
      warning.classList.remove('bg-yellow-50', 'dark:bg-yellow-900/20', 'border-yellow-300', 'dark:border-yellow-700', 'text-yellow-500', 'dark:text-yellow-400');
      warning.classList.add('bg-red-50', 'dark:bg-red-900/20', 'border-red-300', 'dark:border-red-700', 'text-red-500', 'dark:text-red-400');
      return false;
    }
    
    const ahora = new Date();
    ahora.setHours(0, 0, 0, 0);
    const diasRestantes = Math.ceil((venc - ahora) / (1000 * 60 * 60 * 24));
    
    if (diasRestantes < 0) {
      warningText.textContent = '⚠️ Este producto ya está vencido';
      warning.classList.remove('hidden');
    } else if (diasRestantes === 0) {
      warningText.textContent = '⚠️ Este producto vence HOY';
      warning.classList.remove('hidden');
    } else if (diasRestantes <= 7) {
      warningText.textContent = `⚠️ Este producto vence en ${diasRestantes} días (Crítico)`;
      warning.classList.remove('hidden');
    } else if (diasRestantes <= 30) {
      warningText.textContent = `📅 Este producto vence en ${diasRestantes} días`;
      warning.classList.remove('hidden');
    }
  }

  return true;
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
    this.configurarValidacionFechas();
    this.modal.classList.remove('hidden');
  },

  configurarValidacionFechas() {
    const fechaElab = document.getElementById('fecha_elaboracion');
    const fechaVenc = document.getElementById('fecha_vencimiento');
    
    if (fechaElab && fechaVenc) {
      const validar = () => {
        this.validarFechas(fechaElab.value, fechaVenc.value);
      };
      
      fechaElab.addEventListener('change', validar);
      fechaVenc.addEventListener('change', validar);
    }
  },

  saveNew(form) {
    const data = Object.fromEntries(new FormData(form).entries());
    
    // Validar fechas antes de enviar
    if (!this.validarFechas(data.fecha_elaboracion, data.fecha_vencimiento)) {
      return;
    }
    
    data.stock = parseInt(data.stock);
    data.peso = parseFloat(data.peso);
    data.precio_unitario = parseFloat(data.precio_unitario);
    data.id_estante = this.obtenerEstantePorCategoria(data.categoria);
    
    // Enviar fechas solo si no están vacías
    if (!data.fecha_elaboracion) delete data.fecha_elaboracion;
    if (!data.fecha_vencimiento) delete data.fecha_vencimiento;


    const btn = form.querySelector('button[type="submit"]');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Guardando...';

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

    fetch('/api/productos/agregar', {
      method: 'POST',
      headers: {
        'Content-Type':'application/json',
        'X-CSRFToken': csrfToken
      },
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
    this.configurarValidacionFechas();
  },

  saveEdit(form) {
    const fd = new FormData(form);
    
    // Validar fechas antes de guardar
    const fechaElab = fd.get('fecha_elaboracion');
    const fechaVenc = fd.get('fecha_vencimiento');
    if (!this.validarFechas(fechaElab, fechaVenc)) {
      return;
    }
    
    const updated = {
      nombre: fd.get('nombre'),
      categoria: fd.get('categoria'),
      stock: parseInt(fd.get('stock')),
      peso: parseFloat(fd.get('peso')),
      descripcion: fd.get('descripcion'),
      fecha_elaboracion: fechaElab || null,
      fecha_vencimiento: fechaVenc || null
    };

    const btn = form.querySelector('button[type="submit"]');
    const originalHTML = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Guardando...';

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    const idproducto = this.state.current.idproducto;

    fetch(`/api/productos/editar/${idproducto}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      body: JSON.stringify(updated)
    })
    .then(r => r.json())
    .then(res => {
      if (res.success) {
        console.info('Producto actualizado', res);
        this.closeModal();
        location.reload();
      } else {
        console.error(res.error);
        alert('Error al actualizar: ' + (res.error || 'Error desconocido'));
        btn.disabled = false;
        btn.innerHTML = originalHTML;
      }
    })
    .catch(err => {
      console.error('Error al actualizar producto', err);
      alert('Error de conexión al actualizar el producto');
      btn.disabled = false;
      btn.innerHTML = originalHTML;
    });
  },

  async deleteProduct(id) {
    try {
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      const response = await fetch(`/api/productos/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        }
      });
      
      // Verificar si la respuesta es válida
      if (!response.ok) {
        // Intentar leer el error del servidor
        try {
          const errorData = await response.json();
          console.error('Error del servidor:', errorData);
          alert('Error al eliminar: ' + (errorData.error || 'Error desconocido'));
        } catch {
          alert('Error al eliminar el producto (código ' + response.status + ')');
        }
        return;
      }
      
      const data = await response.json();
      
      if (data.success) {
        console.info('Producto eliminado exitosamente');
        alert('✅ Producto eliminado exitosamente');
        this.closeModal();
        await this.loadData();
      } else {
        console.error(data.error);
        alert('Error al eliminar: ' + (typeof data.error === 'string' ? data.error : JSON.stringify(data.error)));
      }
    } catch (error) {
      console.error('Error al eliminar producto:', error);
      // Si el producto se eliminó pero hubo un error al recargar, no mostrar error
      console.info('Recargando datos...');
      await this.loadData();
    }
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
            <label class="block text-sm font-medium mb-1">Fecha de Elaboración</label>
            <input type="date" name="fecha_elaboracion" id="fecha_elaboracion" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Fecha de Vencimiento</label>
            <input type="date" name="fecha_vencimiento" id="fecha_vencimiento" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
        </div>
        <div id="fecha_warning" class="hidden text-sm text-yellow-500 dark:text-yellow-400 flex items-center gap-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-md px-3 py-2">
          <span class="material-symbols-outlined text-base">warning</span>
          <span id="fecha_warning_text"></span>
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
          <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Fechas y Vencimiento</h4>
          <div class="space-y-2 text-neutral-100">
            <p><span class="font-medium">Fecha Elaboración:</span> ${p.fecha_elaboracion_formato || p.fecha_elaboracion || 'N/A'}</p>
            <p><span class="font-medium">Fecha Vencimiento:</span> ${p.fecha_vencimiento_formato || p.fecha_vencimiento || 'N/A'}</p>
            ${p.estado_vencimiento ? `
              <p><span class="font-medium">Estado:</span> 
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                  ${p.estado_vencimiento.estado === 'vencido' || p.estado_vencimiento.estado === 'vence_hoy' ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-400' : 
                    p.estado_vencimiento.estado === 'critico' ? 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-400' :
                    p.estado_vencimiento.estado === 'proximo' ? 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-400' :
                    'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-400'}">
                  ${p.estado_vencimiento.mensaje_detallado || p.estado_vencimiento.mensaje}
                </span>
              </p>` : ''}
          </div>
        </div>
      </div>
      <div class="bg-[var(--card-bg-dark)] p-4 rounded-lg mb-6">
        <h4 class="text-lg font-semibold mb-3 text-[var(--primary-color)]">Auditoría</h4>
        <div class="space-y-2 text-neutral-100">
          <p><span class="font-medium">Fecha de Ingreso:</span> ${p.fecha_ingreso || 'N/A'}</p>
          <p><span class="font-medium">Ingresado por:</span> ${p.ingresado_por || 'N/A'}</p>
          <p><span class="font-medium">Modificado por:</span> ${p.modificado_por || 'N/A'}</p>
          <p><span class="font-medium">Fecha de Modificación:</span> ${p.fecha_modificacion || 'N/A'}</p>
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
          <div>
            <label class="block text-sm font-medium mb-1">Fecha de Elaboración</label>
            <input type="date" name="fecha_elaboracion" id="fecha_elaboracion" value="${p.fecha_elaboracion || ''}" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Fecha de Vencimiento</label>
            <input type="date" name="fecha_vencimiento" id="fecha_vencimiento" value="${p.fecha_vencimiento || ''}" class="w-full bg-[var(--card-bg-dark)] border border-neutral-700 rounded-md px-3 py-2 text-neutral-100">
          </div>
        </div>
        <div id="fecha_warning" class="hidden text-sm text-yellow-500 dark:text-yellow-400 flex items-center gap-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-300 dark:border-yellow-700 rounded-md px-3 py-2">
          <span class="material-symbols-outlined text-base">warning</span>
          <span id="fecha_warning_text"></span>
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
  async exportVisible() {
    try {
      console.log('🔵 [INVENTARIO] Iniciando exportación...');
      const rows = this.state.filteredRows;
      console.log('🔵 [INVENTARIO] Filas filtradas:', rows.length);
      
      if (rows.length === 0) {
        alert('No hay datos para exportar');
        return;
      }

      // Mostrar notificación de carga
      if (typeof mostrarNotificacion === 'function') {
        mostrarNotificacion('📊 Generando archivo Excel profesional...', 'info');
      }

      // Preparar filtros actuales
      const filtros = {
        categoria: this.state.filters.category || null,
        estante: null, // Agregar si existe filtro de estante
        estado: this.state.filters.status || null
      };
      console.log('🔵 [INVENTARIO] Filtros:', filtros);

      // Llamar al endpoint del backend
      console.log('🔵 [INVENTARIO] Llamando a /api/inventario/exportar-excel...');
      const response = await fetch('/api/inventario/exportar-excel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filtros })
      });

      console.log('🔵 [INVENTARIO] Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ [INVENTARIO] Error del servidor:', errorText);
        throw new Error(`Error del servidor: ${response.status} - ${errorText}`);
      }

      // Obtener el blob del archivo
      console.log('🔵 [INVENTARIO] Obteniendo blob...');
      const blob = await response.blob();
      console.log('🔵 [INVENTARIO] Blob size:', blob.size, 'bytes');
      
      // Crear URL temporal y descargar
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Nombre del archivo
      const fecha = new Date().toISOString().split('T')[0];
      link.download = `Weigence_Inventario_${fecha}.xlsx`;
      
      console.log('🔵 [INVENTARIO] Descargando archivo:', link.download);
      
      // Simular click para descargar
      document.body.appendChild(link);
      link.click();
      
      // Limpiar
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      console.log('✅ [INVENTARIO] Exportación exitosa');
      if (typeof mostrarNotificacion === 'function') {
        mostrarNotificacion(`✅ Inventario exportado: ${rows.length} productos`, 'success');
      }
      
    } catch (error) {
      console.error('❌ [INVENTARIO] Error completo:', error);
      console.error('❌ [INVENTARIO] Stack:', error.stack);
      if (typeof mostrarNotificacion === 'function') {
        mostrarNotificacion(`Error al exportar: ${error.message}`, 'error');
      } else {
        alert('Error al exportar el inventario: ' + error.message);
      }
    }
  }
};


// endpoints inventario
const WeigenceMonitor = {
  async init() {
    await this.actualizarTodo();
    setInterval(() => this.actualizarTodo(), 60000); // refresco cada 60 s
    
    // Iniciar actualización automática de alertas
    this.iniciarActualizacionAutomatica();
    
    // Evento del botón actualizar
    const btnActualizar = document.querySelector('#btnActualizarEstantes');
    if (btnActualizar) {
      btnActualizar.addEventListener('click', async () => {
        btnActualizar.disabled = true;
        btnActualizar.innerHTML = '<span class="material-symbols-outlined text-base animate-spin">refresh</span> Actualizando...';
        await this.actualizarEstantes();
        await this.actualizarAlertas();
        // Actualizar badge de notificaciones
        if (window.actualizarBadgeNotificaciones) {
          window.actualizarBadgeNotificaciones();
        }
        btnActualizar.disabled = false;
        btnActualizar.innerHTML = '<span class="material-symbols-outlined text-base">refresh</span> Actualizar';
      });
    }
  },

  async actualizarTodo() {
    this.actualizarEstantes();
    this.actualizarAlertas();
    this.actualizarProyeccion();
  },

  // -------------------- 1. Monitoreo de estantes --------------------
  async actualizarEstantes() {
    const contenedor = document.querySelector("#monitoreo-estantes");
    if (!contenedor) return;
    
    try {
      // Mostrar indicador de carga
      contenedor.innerHTML = '<div class="col-span-full text-center py-4 text-neutral-500"><span class="material-symbols-outlined animate-spin">refresh</span> Cargando estantes...</div>';
      
      // Agregar timeout de 5 segundos
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const res = await fetch("/api/estantes_estado", { signal: controller.signal });
      clearTimeout(timeoutId);
      
      let data = await res.json();
      if (!Array.isArray(data)) {
        contenedor.innerHTML = '<div class="col-span-full text-center py-4 text-red-500">Error al cargar estantes</div>';
        return;
      }
      
      // Ordenar estantes numéricamente por id_estante (1, 2, 3, 4, 5, 6)
      data = data.sort((a, b) => {
        const numA = parseInt(String(a.id_estante).replace(/\D/g, '')) || 0;
        const numB = parseInt(String(b.id_estante).replace(/\D/g, '')) || 0;
        return numA - numB;
      });

      // Las alertas de estantes se crean automáticamente en el backend
      // y aparecen en el panel de notificaciones del header
      contenedor.innerHTML = "";

      data.forEach(e => {
        // Determinar estado (usar estado_calculado que viene del backend)
        const estado = e.estado_calculado || e.estado || 'estable';
        
        // Definir colores y texto según el estado
        let borderColor, bgColor, badgeBg, badgeText, barColor, textoBadge;
        
        if (estado === 'critico') {
          borderColor = '#fca5a5';
          bgColor = 'rgba(248, 113, 113, 0.1)';
          badgeBg = '#fecaca';
          badgeText = '#991b1b';
          barColor = '#ef4444';
          textoBadge = 'Crítico';
        } else if (estado === 'advertencia') {
          borderColor = '#fcd34d';
          bgColor = 'rgba(250, 204, 21, 0.1)';
          badgeBg = '#fef08a';
          badgeText = '#854d0e';
          barColor = '#eab308';
          textoBadge = 'Alerta';
        } else {
          borderColor = '#86efac';
          bgColor = 'rgba(74, 222, 128, 0.1)';
          badgeBg = '#bbf7d0';
          badgeText = '#166534';
          barColor = '#22c55e';
          textoBadge = 'Estable';
        }

        // Convertir gramos a kilogramos para mostrar
        const pesoActualKg = ((e.peso_actual || 0) / 1000).toFixed(2);
        const pesoMaximoKg = ((e.peso_maximo || 0) / 1000).toFixed(2);
        
        // Determinar color e icono del indicador de pesa
        let pesaIndicador = '';
        if (e.id_estante >= 6) {
          const pesaActiva = e.estado_pesa === true;
          const pesaColorIcon = pesaActiva ? '#22c55e' : '#ef4444';
          const pesaColorText = pesaActiva ? '#16a34a' : '#dc2626';
          const pesaIcon = pesaActiva ? 'check_circle' : 'error';
          const pesaTexto = pesaActiva ? 'Sensor Activo' : 'Sensor Inactivo';
          pesaIndicador = `
            <div class="flex items-center gap-1 mt-2 text-xs">
              <span class="material-symbols-outlined" style="font-size: 16px; color: ${pesaColorIcon};">${pesaIcon}</span>
              <span class="font-medium" style="color: ${pesaColorText};">${pesaTexto}</span>
            </div>
          `;
        }

        contenedor.insertAdjacentHTML(
          "beforeend",
          `
          <div class="border rounded-md p-3 animate-fadeIn" style="border-color: ${borderColor}; background-color: ${bgColor};">
            <div class="flex justify-between items-center mb-2">
              <span class="font-bold text-neutral-900 dark:text-neutral-100">Estante ${e.id_estante}</span>
              <span class="text-xs font-medium px-2 py-0.5 rounded-full" style="background-color: ${badgeBg}; color: ${badgeText};">${textoBadge}</span>
            </div>
            <p class="text-sm mb-1 text-neutral-700 dark:text-neutral-300">Ocupación: ${(e.ocupacion_pct || 0).toFixed(1)}%</p>
            <div class="w-full bg-gray-200 dark:bg-neutral-700 rounded-full h-2.5 mb-2">
              <div class="h-2.5 rounded-full transition-all duration-300" style="width: ${Math.min(e.ocupacion_pct || 0, 100)}%; background-color: ${barColor};"></div>
            </div>
            <p class="text-sm text-neutral-700 dark:text-neutral-300">Peso: ${pesoActualKg} kg / ${pesoMaximoKg} kg</p>
            ${pesaIndicador}
          </div>`
        );
      });
    } catch (err) {
      console.error("Error monitoreo estantes:", err);
      if (err.name === 'AbortError') {
        contenedor.innerHTML = '<div class="col-span-full text-center py-4 text-yellow-600">⏱️ Tiempo de espera agotado. <button onclick="WeigenceMonitor.actualizarEstantes()" class="underline">Reintentar</button></div>';
      } else {
        contenedor.innerHTML = '<div class="col-span-full text-center py-4 text-red-500">❌ Error al cargar estantes</div>';
      }
    }
  },

  // -------------------- 2. Alertas y acciones sugeridas --------------------
  async actualizarAlertas() {
    try {
      const res = await fetch("/api/alertas_activas", { cache: 'no-store' });
      const data = await res.json();
      if (!Array.isArray(data)) return;

      const cont = document.querySelector("#alertas-sugeridas");
      if (!cont) return;
      
      // Solo actualizar si hay cambios
      const currentIds = Array.from(cont.querySelectorAll('[data-id]')).map(el => el.dataset.id).join(',');
      const newIds = data.slice(0, 3).map(a => a.id).join(',');
      
      if (currentIds === newIds) return; // No hay cambios
      
      cont.innerHTML = "";
      cont.classList.remove("opacity-0"); // Mostrar contenedor

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
      // Actualizar alertas y notificaciones
      this.actualizarAlertas();
      if (window.actualizarBadgeNotificaciones) {
        window.actualizarBadgeNotificaciones();
      }
    } catch (e) {
      console.error("Error resolviendo alerta:", e);
    }
  },
  
  // Inicializar actualización automática de alertas
  iniciarActualizacionAutomatica() {
    // Actualizar alertas cada 30 segundos
    setInterval(() => {
      this.actualizarAlertas();
    }, 30000);
  },

  // -------------------- 3. Proyección de consumo --------------------
  async actualizarProyeccion() {
    try {
      const res = await fetch("/api/proyeccion_consumo");
      const data = await res.json();
      if (!Array.isArray(data)) {
        console.warn("Sin datos de consumo (respuesta no es array).");
        return;
      }

      // Si la API devuelve un array vacío, crear una serie placeholder
      // para que el gráfico muestre una línea cero y la proyección a 7 días.
      let usePlaceholder = false;
      if (Array.isArray(data) && data.length === 0) {
        usePlaceholder = true;
      }

      const canvas = document.getElementById("chartProyeccion");
      if (!canvas) return;

      // Normalizar y ordenar por fecha si existe
      let series = [];
      if (usePlaceholder) {
        const today = new Date();
        const iso = today.toISOString().split('T')[0];
        series = [{ label: iso, consumo: 0 }];
      } else {
        series = data
          .map(d => ({ label: d.fecha || d.label || '', consumo: Number(d.consumo) || 0 }))
          .sort((a, b) => (a.label && b.label) ? new Date(a.label) - new Date(b.label) : 0);
      }

      // Detectar si los labels son categóricos (productos) -> contienen letras
      const isCategorical = series.length && series.every(s => /[A-Za-zÀ-ÖØ-öø-ÿ]/.test(String(s.label)));

      const actualLabels = series.map(s => s.label || '');
      const actualValues = series.map(s => s.consumo);

      // Generar proyección avanzada: tendencia basada en últimas ventas y comparación semanal
      const futurePoints = 7;
      let projValues = [];
      let projLabels = [];
      // Detectar si los labels son fechas válidas (time-series)
      const isDateLike = actualLabels.length > 0 && actualLabels.every(l => {
        try { const d = new Date(l); return !isNaN(d); } catch (e) { return false; }
      });

      if (actualValues.length >= 2 && !isDateLike) {
        // Si no es time-series (pero tiene números), seguir con extrapolación por índice
        const last = actualValues[actualValues.length - 1];
        const prev = actualValues[actualValues.length - 2];
        const slope = last - prev; // cambio por paso de índice
        for (let i = 1; i <= futurePoints; i++) {
          projLabels.push(`+${i}`);
          projValues.push(Math.max(0, Math.round((last + slope * i) * 100) / 100));
        }
      } else if (actualValues.length === 1 && !isDateLike) {
        for (let i = 1; i <= futurePoints; i++) {
          projLabels.push(`+${i}`);
          projValues.push(actualValues[0]);
        }
      } else if (isDateLike) {
        // Si son fechas, generar etiquetas de fecha para los próximos días
        const lastDate = new Date(actualLabels[actualLabels.length - 1] || new Date());
        for (let i = 1; i <= futurePoints; i++) {
          const d = new Date(lastDate);
          d.setDate(lastDate.getDate() + i);
          projLabels.push(d.toISOString().split('T')[0]);
        }

        // Proyección inteligente: promedio móvil ponderado de últimos 7 días + tendencia + comparación semanal
        if (actualValues.length >= 7) {
          const last7 = actualValues.slice(-7);
          const avg7 = last7.reduce((a, b) => a + b, 0) / 7;
          
          // Calcular tendencia (regresión lineal simple sobre últimos 7 días)
          let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
          for (let i = 0; i < last7.length; i++) {
            sumX += i;
            sumY += last7[i];
            sumXY += i * last7[i];
            sumX2 += i * i;
          }
          const n = last7.length;
          const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
          const intercept = (sumY - slope * sumX) / n;
          
          // Proyectar usando tendencia + factor de comparación semanal
          for (let i = 1; i <= futurePoints; i++) {
            const trendValue = slope * (n + i - 1) + intercept;
            // Si hay datos de hace 7 días, usar como referencia
            const weekAgoIndex = actualValues.length - 7 - i;
            let projectedValue = trendValue;
            if (weekAgoIndex >= 0) {
              const weekAgoValue = actualValues[weekAgoIndex];
              // Promedio ponderado: 70% tendencia actual, 30% comparación con semana anterior
              projectedValue = (trendValue * 0.7) + (weekAgoValue * 0.3);
            }
            projValues.push(Math.max(0, Math.round(projectedValue * 100) / 100));
          }
        } else if (actualValues.length >= 2) {
          // Si hay menos de 7 días, usar extrapolación lineal simple
          const last = actualValues[actualValues.length - 1];
          const prev = actualValues[actualValues.length - 2];
          const slope = last - prev;
          for (let i = 1; i <= futurePoints; i++) {
            projValues.push(Math.max(0, Math.round((last + slope * i) * 100) / 100));
          }
        } else if (actualValues.length === 1) {
          for (let i = 1; i <= futurePoints; i++) projValues.push(actualValues[0]);
        }

        // Si en los últimos 7 días no hubo ventas, usar histórico/promedio como proyección
        try {
          const last7 = actualValues.slice(-7);
          const last7Sum = last7.reduce((a, b) => a + (Number(b) || 0), 0);
          if (last7Sum === 0) {
            try {
              const resp = await fetch('/api/promedio_consumo');
              const pv = await resp.json();
              const histAvg = Number(pv.promedio_total) || 0;
              if (histAvg > 0) {
                projValues = new Array(futurePoints).fill(Math.round(histAvg * 100) / 100);
                // marcar que usamos fallback histórico
                this._proyeccionUsaHistorico = true;
              }
            } catch (e) {
              console.warn('Fallo al obtener promedio_consumo para histórico:', e);
            }
          }
        } catch (e) { /* noop */ }
      }

      // X labels: combinar reales y proyección
      const labels = actualLabels.concat(projLabels);
      const actualData = actualValues.concat(new Array(projLabels.length).fill(null));
      const projectionData = new Array(actualValues.length).fill(null).concat(projValues);

      // Si los datos son categóricos (productos), usar gráfico de barras y fallback a promedios
      if (isCategorical) {
        // Si todos los valores son 0, intentar obtener promedio desde backend
        const allZero = actualValues.every(v => v === 0);
        if (allZero) {
          try {
            const resp = await fetch('/api/promedio_consumo');
            const pv = await resp.json();
            const mapa = {};
            (pv.promedio_por_producto || []).forEach(p => { mapa[String(p.nombre).toLowerCase()] = p.promedio; });
            const defaultAvg = pv.promedio_total || 0;
            // Reemplazar actualValues por promedios cuando existan, sino por promedio total
            for (let i = 0; i < actualValues.length; i++) {
              const key = String(actualLabels[i] || '').toLowerCase();
              actualData[i] = mapa[key] != null ? mapa[key] : defaultAvg;
            }
          } catch (e) {
            console.warn('No se pudo obtener promedio_consumo:', e);
          }
        }

        // Dibujar/actualizar gráfico de barras
        const canvas = document.getElementById('chartProyeccion');
        if (!canvas) return;
        const ChartLib = (typeof Chart !== 'undefined') ? Chart : (window && window.Chart ? window.Chart : null);
        if (!ChartLib) {
          console.warn('Chart.js no está disponible.');
          return;
        }
        if (this.chartProyeccion && typeof this.chartProyeccion.destroy === 'function') try { this.chartProyeccion.destroy(); } catch(e){}
        try {
          const ctx = canvas.getContext('2d');
          this.chartProyeccion = new ChartLib(ctx, {
            type: 'bar',
            data: { labels: actualLabels, datasets: [{ label: 'Consumo (promedio)', data: actualData, backgroundColor: '#60a5fa' }] },
            options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{display:false}}, scales:{x:{grid:{display:false}}, y:{beginAtZero:true}} }
          });
        } catch (e) { console.error('Error inicializando gráfico de barras:', e); }

        return; // no continuar con la lógica de líneas/proyección
      }

      // Verificar Chart.js disponible y usarlo de forma robusta
      const ChartLib = (typeof Chart !== 'undefined') ? Chart : (window && window.Chart ? window.Chart : null);
      if (!ChartLib) {
        console.warn('Chart.js no está disponible. Asegúrate de que esté cargado en la plantilla.');
        return;
      }

      // Destruir instancia previa si existe (evita problemas al recargar datos)
      if (this.chartProyeccion && typeof this.chartProyeccion.destroy === 'function') {
        try { this.chartProyeccion.destroy(); } catch (e) { /* noop */ }
        this.chartProyeccion = null;
      }

      try {
        const ctx = canvas.getContext('2d');
        const allValues = actualValues.concat(projValues);
        const maxVal = allValues.length ? Math.max(...allValues) : 1;
        const suggestedMax = Math.ceil(maxVal * 1.2) || 5;

        this.chartProyeccion = new ChartLib(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: [
              {
                label: 'Consumo Real',
                data: actualData,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59,130,246,0.1)',
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#3b82f6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                borderWidth: 3,
                fill: true,
                spanGaps: true
              },
              {
                label: 'Proyección (7 días)',
                data: projectionData,
                borderColor: '#f59e0b',
                borderDash: [8, 4],
                backgroundColor: 'rgba(245,158,11,0.08)',
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 5,
                pointBackgroundColor: '#f59e0b',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                borderWidth: 2,
                fill: false,
                spanGaps: false
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { 
              legend: { 
                display: true,
                position: 'top',
                labels: {
                  usePointStyle: true,
                  padding: 15,
                  font: { size: 11, weight: '500' }
                }
              },
              tooltip: {
                mode: 'index',
                intersect: false,
                backgroundColor: 'rgba(0,0,0,0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                borderColor: '#3b82f6',
                borderWidth: 1,
                padding: 10,
                displayColors: true
              }
            },
            scales: {
              x: { 
                display: true, 
                grid: { display: false },
                ticks: { font: { size: 10 } }
              },
              y: { 
                beginAtZero: true, 
                suggestedMax: suggestedMax,
                ticks: { font: { size: 10 } },
                grid: { color: 'rgba(0,0,0,0.05)' }
              }
            },
            elements: { line: { capBezierPoints: true } },
            interaction: {
              mode: 'nearest',
              axis: 'x',
              intersect: false
            }
          }
        });
      } catch (e) {
        console.error('Error inicializando/actualizando Chart.js:', e);
      }
    } catch (err) {
      console.error("Error proyección:", err);
    }
  }
  };
  WeigenceMonitor.actualizarSVG = async function () {
    const svg = document.getElementById("svg-almacen");
      if (!svg) {
        console.warn("SVG del almacén no encontrado en el DOM todavía");
        return;
      }

    try {
      const res = await fetch("/api/estantes_estado");
      let data = await res.json();
      if (!Array.isArray(data) || data.length === 0) {
        console.warn("No hay datos de estantes disponibles para renderizar.");
        return;
      }
      
      // Ordenar estantes numéricamente por id_estante (1, 2, 3, 4, 5, 6)
      data = data.sort((a, b) => {
        const numA = parseInt(String(a.id_estante).replace(/\D/g, '')) || 0;
        const numB = parseInt(String(b.id_estante).replace(/\D/g, '')) || 0;
        return numA - numB;
      });
      
      if (!svg || !Array.isArray(data)) return;

      // Limpia el SVG
      while (svg.firstChild) svg.removeChild(svg.firstChild);

      // Layout en cuadrícula fija: 3 columnas x 2 filas para 6 estantes
      const vb = svg.viewBox && svg.viewBox.baseVal ? svg.viewBox.baseVal : { width: 600, height: 165 };
      const svgW = vb.width || svg.clientWidth || 600;
      const svgH = vb.height || svg.clientHeight || 165;
      const padding = 12;

      const n = data.length;
      if (n === 0) return;

      // Forzar grid de 3 columnas x 2 filas
      const cols = 3;
      const rows = 2;

      const cellW = (svgW - padding * 2) / cols;
      const cellH = (svgH - padding * 2) / rows;
      const rectW = Math.max(36, Math.min(100, cellW * 0.75));
      const rectH = Math.max(22, Math.min(48, cellH * 0.55));

      // Crear <defs> con gradientes y sombra si no existen (se reutilizan)
      if (!svg.querySelector('defs')) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');

        const makeGradient = (id, base) => {
          const g = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
          g.setAttribute('id', id);
          g.setAttribute('x1', '0%'); g.setAttribute('y1', '0%'); g.setAttribute('x2', '0%'); g.setAttribute('y2', '100%');
          const s1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
          s1.setAttribute('offset', '0%'); s1.setAttribute('stop-color', base); s1.setAttribute('stop-opacity', '0.95');
          const s2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
          s2.setAttribute('offset', '60%'); s2.setAttribute('stop-color', base); s2.setAttribute('stop-opacity', '0.75');
          const s3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
          s3.setAttribute('offset', '100%'); s3.setAttribute('stop-color', '#000'); s3.setAttribute('stop-opacity', '0.06');
          g.appendChild(s1); g.appendChild(s2); g.appendChild(s3);
          return g;
        };

        defs.appendChild(makeGradient('grad-critico', '#ef4444'));
        defs.appendChild(makeGradient('grad-advertencia', '#f59e0b'));
        defs.appendChild(makeGradient('grad-estable', '#22c55e'));

        // Sombra suave (drop shadow)
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.setAttribute('id', 'shelfShadow');
        filter.setAttribute('x', '-20%'); filter.setAttribute('y', '-20%'); filter.setAttribute('width', '140%'); filter.setAttribute('height', '140%');
        const feDrop = document.createElementNS('http://www.w3.org/2000/svg', 'feDropShadow');
        feDrop.setAttribute('dx', '0'); feDrop.setAttribute('dy', '2'); feDrop.setAttribute('stdDeviation', '3'); feDrop.setAttribute('flood-color', '#000'); feDrop.setAttribute('flood-opacity', '0.25');
        filter.appendChild(feDrop);
        defs.appendChild(filter);

        svg.appendChild(defs);
      }

    // Fondo adaptable a modo claro/oscuro (sin overlay blanco)
    try {
      const darkMode =
        document.documentElement.classList.contains("dark") ||
        document.body.classList.contains("dark");

      svg.style.background = darkMode
        ? "rgba(15, 23, 42, 0)" // totalmente transparente en dark
        : "rgba(255, 255, 255, 0)"; // totalmente transparente en light

      svg.style.borderRadius = "8px";
      svg.style.pointerEvents = "auto";
    } catch (e) {
      console.warn("No se pudo aplicar fondo SVG:", e);
    }




    data.forEach((e, idx) => {
        const estado = e.estado_calculado || e.estado || 'estable';
        const baseColor = estado === 'critico' ? '#ef4444' : estado === 'advertencia' ? '#f59e0b' : '#22c55e';
        const gradId = estado === 'critico' ? 'grad-critico' : estado === 'advertencia' ? 'grad-advertencia' : 'grad-estable';

        const col = idx % cols;
        const row = Math.floor(idx / cols);

        const cellX = padding + col * cellW;
        const cellY = padding + row * cellH;

        const posX = cellX + (cellW - rectW) / 2;
        const posY = cellY + (cellH - rectH) / 2;

    // Grupo principal del estante (minimalista: líneas + subrayado de color)
    const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    g.setAttribute('transform', `translate(${posX},${posY})`);
    g.style.cursor = 'pointer';

    // Hit area transparente para mantener la interactividad (clic/hover) sin cambiar la apariencia
    const hit = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    hit.setAttribute('x', 0);
    hit.setAttribute('y', 0);
    hit.setAttribute('width', rectW);
    hit.setAttribute('height', rectH);
    hit.setAttribute('fill', 'transparent');
    hit.setAttribute('pointer-events', 'all');
    // poner dataset para depuración
    hit.dataset.id = e.id_estante;
    g.appendChild(hit);

  // Detectar modo oscuro y obtener color de texto calculado del contenedor padre
  const darkMode = (document.documentElement.classList && document.documentElement.classList.contains('dark')) || (document.body.classList && document.body.classList.contains('dark'));
      const parent = svg.parentElement || document.body;
      // Buscar hacia arriba el primer ancestro que tenga un background no transparente
      const findAncestorWithBg = (el) => {
        let cur = el;
        while (cur && cur !== document.documentElement) {
          try {
            const s = window.getComputedStyle(cur);
            const bg = s && (s.backgroundColor || s.backgroundImage || s.background);
            if (bg && bg !== 'transparent' && !/rgba?\(0,\s*0,\s*0,\s*0\)/i.test(bg)) return { bg: s.backgroundColor || bg, radius: s.borderRadius };
          } catch (e) { /* noop */ }
          cur = cur.parentElement;
        }
        return null;
      };
      const anc = findAncestorWithBg(parent);
      const rootStyle = window.getComputedStyle(document.documentElement);
      const cssVarCard = (rootStyle && rootStyle.getPropertyValue) ? rootStyle.getPropertyValue('--card-bg-light').trim() : '';
      const parentBg = anc && anc.bg ? anc.bg : (cssVarCard || 'transparent');
      // Forzar fondo siempre transparente (evita que tape leyendas)
      svg.style.background = "transparent";
      try { svg.style.borderRadius = (anc && anc.radius) || (parent && window.getComputedStyle(parent).borderRadius) || '8px'; } catch (err) { /* noop */ }

      // Determinar color de texto accesible en base al fondo (luminancia)
      const parseRgb = str => {
        if (!str) return null;
        const m = String(str).match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
        if (m) return [Number(m[1]), Number(m[2]), Number(m[3])];
        const hex = String(str).replace('#','').trim();
        if (hex.length === 3) return [parseInt(hex[0]+hex[0],16), parseInt(hex[1]+hex[1],16), parseInt(hex[2]+hex[2],16)];
        if (hex.length === 6) return [parseInt(hex.substring(0,2),16), parseInt(hex.substring(2,4),16), parseInt(hex.substring(4,6),16)];
        return null;
      };
  let rgb = parseRgb(parentBg);
  let luminance = rgb ? ( (0.2126 * (rgb[0]/255)) + (0.7152 * (rgb[1]/255)) + (0.0722 * (rgb[2]/255)) ) : (darkMode ? 0.1 : 0.9);
      // Si no estamos en modo oscuro pero el fondo detectado es muy oscuro o transparente, forzar el fondo claro de la tarjeta
      const cssVarCardCheck = cssVarCard || '';
      if (!darkMode && (parentBg === 'transparent' || parentBg === '' || luminance < 0.18)) {
        const forced = cssVarCardCheck || '#f1f5f9';
        try { svg.style.background = forced; } catch (err) { /* noop */ }
        rgb = parseRgb(forced);
        luminance = rgb ? ( (0.2126 * (rgb[0]/255)) + (0.7152 * (rgb[1]/255)) + (0.0722 * (rgb[2]/255)) ) : 0.95;
      }
  const computedTextColor = luminance < 0.5 ? '#e5e7eb' : '#0f172a';

      // Usamos currentColor para que textos/contornos hereden el color calculado
      const neutralStroke = 'currentColor';

      // Aplicar color al grupo (currentColor heredará de aquí)
      g.style.color = computedTextColor;

      // Contorno leve (sombra muy sutil, mantiene separación con fondo) - sin relleno
  const outline = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      outline.setAttribute('x', 0);
      outline.setAttribute('y', 0);
      outline.setAttribute('width', rectW);
      outline.setAttribute('height', rectH);
      outline.setAttribute('rx', Math.min(6, rectH / 4));
      outline.setAttribute('ry', Math.min(6, rectH / 4));
  outline.setAttribute('fill', 'none');
  outline.setAttribute('stroke', neutralStroke);
  outline.setAttribute('stroke-width', '1');
  outline.setAttribute('stroke-opacity', darkMode ? '0.06' : '0.06');
      outline.setAttribute('pointer-events', 'none');
      g.appendChild(outline);

      // Líneas que simulan estantes: dos líneas finas horizontales
      const shelfLine = (yFrac, color, width, opacity) => {
        const ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        const y = Math.round(rectH * yFrac);
        ln.setAttribute('x1', 6);
        ln.setAttribute('y1', y);
        ln.setAttribute('x2', rectW - 6);
        ln.setAttribute('y2', y);
        ln.setAttribute('stroke', color);
        ln.setAttribute('stroke-width', String(width));
        ln.setAttribute('stroke-linecap', 'round');
        ln.setAttribute('opacity', String(opacity));
        ln.setAttribute('pointer-events', 'none');
        return ln;
      };

      // líneas neutras (estructura)
      g.appendChild(shelfLine(0.44, darkMode ? 'rgba(255,255,255,0.04)' : 'rgba(2,6,23,0.04)', 1, 1));
      g.appendChild(shelfLine(0.72, darkMode ? 'rgba(255,255,255,0.03)' : 'rgba(2,6,23,0.03)', 1, 1));

      // Subrayado de color (accent): una línea en la base con color según estado
      const accent = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      const accentY = Math.round(rectH - Math.max(4, rectH * 0.12));
      accent.setAttribute('x1', 6);
      accent.setAttribute('y1', accentY);
      accent.setAttribute('x2', rectW - 6);
      accent.setAttribute('y2', accentY);
      accent.setAttribute('stroke', baseColor);
      accent.setAttribute('stroke-width', Math.max(2, Math.round(rectH * 0.12)));
      accent.setAttribute('stroke-linecap', 'round');
      accent.setAttribute('opacity', '0.92');
      accent.setAttribute('pointer-events', 'none');
      g.appendChild(accent);

      // leve brillo interior sobre el subrayado (más sutil)
      const accentGlow = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      accentGlow.setAttribute('x1', 6);
      accentGlow.setAttribute('y1', accentY - 2);
      accentGlow.setAttribute('x2', rectW - 6);
      accentGlow.setAttribute('y2', accentY - 2);
      accentGlow.setAttribute('stroke', '#ffffff');
      accentGlow.setAttribute('stroke-width', '1');
      accentGlow.setAttribute('opacity', darkMode ? '0.06' : '0.04');
      accentGlow.setAttribute('pointer-events', 'none');
      g.appendChild(accentGlow);

      // Texto (nombre completo) centrado. Añadimos un pequeño bloque (labelBox) detrás del texto
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', rectW / 2);
      text.setAttribute('y', Math.round(rectH * 0.45) + 4);
      text.setAttribute('text-anchor', 'middle');
      const fontSize = Math.max(8, Math.min(12, Math.floor(rectH * 0.34)));
      text.setAttribute('font-size', String(fontSize));
      text.setAttribute('fill', 'currentColor');
      text.setAttribute('pointer-events', 'none');
      text.textContent = `Estante ${e.id_estante}`;
      // Añadir texto (sin labelBox) y posicionarlo en centro del área del estante
      text.setAttribute('y', Math.round(rectH * 0.45) + 4);
      g.appendChild(text);

  svg.appendChild(g);

      // Mantener eventos existentes sobre el grupo
      const attachEventsTarget = g;
      attachEventsTarget.addEventListener('click', () => WeigenceMonitor.mostrarDetalleEstante(e));
      attachEventsTarget.addEventListener('mouseenter', evt => {
        const tooltip = document.getElementById('tooltip-estante');
        if (!tooltip) return;
        tooltip.classList.remove('hidden');
        const svgRect = svg.getBoundingClientRect();
        const x = evt.clientX - svgRect.left;
        const y = evt.clientY - svgRect.top;
        tooltip.style.left = `${x + 12}px`;
        tooltip.style.top = `${y - tooltip.offsetHeight / 2}px`;
        const tipRect = tooltip.getBoundingClientRect();
        if (tipRect.right > window.innerWidth - 10) tooltip.style.left = `${x - tipRect.width - 12}px`;
        if (tipRect.top < 0) tooltip.style.top = `${y + 10}px`;
        tooltip.innerHTML = `<b>Estante ${e.id_estante}</b><br>Estado: ${e.estado}<br>Ocupación: ${e.ocupacion_pct || 0}%`;
      });
      attachEventsTarget.addEventListener('mouseleave', () => {
        const tooltip = document.getElementById('tooltip-estante');
        if (tooltip) tooltip.classList.add('hidden');
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
    cont.classList.remove("opacity-0"); // Mostrar contenedor

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
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    cont.querySelectorAll("button[data-id]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.id;
        await fetch(`/api/alertas/marcar_revisada/${id}`, { 
          method: "POST",
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
          }
        });
        cargarAlertas();
      });
    });
  } catch (err) {
    console.error("Error cargando alertas:", err);
  }
}
// --- Sincroniza el mapa SVG con el modo claro/oscuro dinámicamente ---
const observer = new MutationObserver((mutations) => {
  for (const m of mutations) {
    if (m.attributeName === "class") {
      const isDark = document.documentElement.classList.contains("dark");

      // Si existe el SVG, actualiza fondo y texto
      const svg = document.getElementById("svg-almacen");
      if (svg) {
        svg.style.background = "transparent"; // siempre limpio
        svg.querySelectorAll("text").forEach(t => {
          t.setAttribute("fill", isDark ? "#E5E7EB" : "#0F172A");
        });
      }

      // Si quieres que recalcule todo el diseño del mapa:
      if (typeof WeigenceMonitor.actualizarSVG === "function") {
        WeigenceMonitor.actualizarSVG();
      }
    }
  }
});

// Observa cambios en la clase del <html> (Tailwind usa esto para modo dark)
observer.observe(document.documentElement, { attributes: true });


// Integrar con el resto
if (typeof WeigenceMonitor.actualizarTodo === 'function') {
  const oldUpdate = WeigenceMonitor.actualizarTodo.bind(WeigenceMonitor);
  WeigenceMonitor.actualizarTodo = async function () {
    await oldUpdate();
    this.actualizarSVG();
  };
} else {
  WeigenceMonitor.actualizarTodo = async function () {
    this.actualizarSVG();
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  await WeigenceMonitor.init();
  await WeigenceMonitor.actualizarSVG();
  await cargarAlertas();
  Inventario.init();
  console.info("Weigence Inventory System listo.");
});

// Refrescar alertas cada 20 segundos
setInterval(cargarAlertas, 20000);


