// ===========================================================
// Sistema Weigence - Ventas.js (Paginación y Modal)
// Basado en la lógica de Inventario.js
// ===========================================================

const Ventas = {
  state: {
    page: 1,
    pageSize: 10,
    rows: [],
    filteredRows: [],
    detallesVentas: {},
    productosDict: {},
    filtrosActivos: {
      producto: '',
      vendedor: '',
      fechaDesde: '',
      fechaHasta: '',
      totalMin: '',
      totalMax: ''
    },
    filtroTemporalActivo: false,
    rangoTemporal: null // 'hoy', 'semana', 'mes'
  },

  init() {
    this.cacheDOM();
    this.cargarDatosIniciales();
    this.refreshRows();
    this.bindEvents();
    this.conectarBotonesHeaderFiltros(); // Conectar botones del header
    this.bindFiltros();
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
    this.modal = document.getElementById('detalleVentaModal');
    this.modalContent = document.getElementById('modalDetalleContent');
    this.ventasCounter = document.getElementById('ventas-counter');
    
    // Elementos de filtros
    this.filtroProducto = document.getElementById('filtro-producto');
    this.filtroVendedor = document.getElementById('filtro-vendedor');
    this.filtroFechaDesde = document.getElementById('filtro-fecha-desde');
    this.filtroFechaHasta = document.getElementById('filtro-fecha-hasta');
    this.filtroTotalMin = document.getElementById('filtro-total-min');
    this.filtroTotalMax = document.getElementById('filtro-total-max');
    this.btnAplicarFiltros = document.getElementById('btn-aplicar-filtros');
    this.btnLimpiarFiltros = document.getElementById('btn-limpiar-filtros');
    this.filtrosActivosContainer = document.getElementById('filtros-activos');
    this.filtrosActivosChips = document.getElementById('filtros-activos-chips');
  },

  cargarDatosIniciales() {
    // Cargar detalles de ventas desde atributos data en las filas
    const rows = document.querySelectorAll('.venta-row');
    console.log(`🔍 DEBUG: Cargando datos de ${rows.length} ventas`);
    
    rows.forEach(row => {
      const idVenta = row.dataset.idventa;
      const detallesJson = row.dataset.detalles;
      const productosJson = row.dataset.productos;
      
      if (detallesJson) {
        try {
          const detalles = JSON.parse(detallesJson);
          this.state.detallesVentas[idVenta] = {
            items: detalles,
            fecha: row.dataset.fecha,
            vendedorRut: row.dataset.vendedorRut,
            vendedorNombre: row.dataset.vendedorNombre,
            total: parseFloat(row.dataset.total)
          };
          console.log(`✅ Detalles cargados para venta #${idVenta}:`, this.state.detallesVentas[idVenta]);
        } catch (e) {
          console.error(`❌ Error al parsear detalles de venta #${idVenta}:`, e);
        }
      }
      
      if (productosJson && !Object.keys(this.state.productosDict).length) {
        try {
          this.state.productosDict = JSON.parse(productosJson);
          console.log('✅ Diccionario de productos cargado:', this.state.productosDict);
        } catch (e) {
          console.error('❌ Error al parsear productos:', e);
        }
      }
    });
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

    // Botones "Ver detalles"
    document.addEventListener('click', (e) => {
      if (e.target.closest('.btn-ver-detalle')) {
        const btn = e.target.closest('.btn-ver-detalle');
        const idVenta = btn.dataset.idventa;
        this.mostrarDetalleVenta(idVenta);
      }

      // Cerrar modal
      if (e.target.classList.contains('modal-overlay') || e.target.closest('.btn-cerrar-modal')) {
        this.cerrarModal();
      }
    });

    // Cerrar modal con ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.modal && !this.modal.classList.contains('hidden')) {
        this.cerrarModal();
      }
    });
  },

  // ============================================================
  // FILTROS TEMPORALES DEL HEADER (Hoy/Semana/Mes)
  // ============================================================
  conectarBotonesHeaderFiltros() {
    const botonesHeader = document.querySelectorAll('.filtro-fecha-btn');
    
    console.log('🔍 Buscando botones de filtro del header:', botonesHeader.length, 'encontrados');
    
    if (!botonesHeader.length) {
      console.warn('⚠️ No se encontraron botones de filtro de fecha en el header');
      return;
    }
    
    botonesHeader.forEach(btn => {
      console.log('✅ Conectando botón:', btn.dataset.rango);
      
      // Evitar listeners duplicados
      if (btn.dataset.listenerAdded === 'true') {
        console.log('⚠️ Ya tiene listener:', btn.dataset.rango);
        return;
      }
      btn.dataset.listenerAdded = 'true';
      
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        const rango = btn.getAttribute('data-rango');
        console.log('🎯 Click en filtro del header:', rango);
        
        // Remover clase activa de todos los botones
        botonesHeader.forEach(b => {
          b.classList.remove('filtro-activo');
        });
        
        // Activar el botón clickeado
        btn.classList.add('filtro-activo');
        
        // Ejecutar filtro correspondiente
        if (rango === 'hoy') {
          console.log('📅 Ejecutando filtrarHoy()');
          this.filtrarHoy();
        } else if (rango === 'semana') {
          console.log('📅 Ejecutando filtrarSemana()');
          this.filtrarSemana();
        } else if (rango === 'mes') {
          console.log('📅 Ejecutando filtrarMes()');
          this.filtrarMes();
        }
      });
    });
    
    console.log('✅ Botones de filtro del header conectados correctamente');
  },

  filtrarHoy() {
    this.state.filtroTemporalActivo = true;
    this.state.rangoTemporal = 'hoy';
    
    const ahora = new Date();
    const inicioHoy = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
    
    this.aplicarFiltroTemporalPorRango(inicioHoy, null, 'Hoy (últimas 24h)');
    this.mostrarNotificacion('📅 Mostrando ventas de hoy', 'info');
  },

  filtrarSemana() {
    this.state.filtroTemporalActivo = true;
    this.state.rangoTemporal = 'semana';
    
    const ahora = new Date();
    const inicioSemana = new Date(ahora);
    inicioSemana.setDate(ahora.getDate() - 7);
    
    this.aplicarFiltroTemporalPorRango(inicioSemana, null, 'Últimos 7 días');
    this.mostrarNotificacion('📅 Mostrando ventas de la última semana', 'info');
  },

  filtrarMes() {
    this.state.filtroTemporalActivo = true;
    this.state.rangoTemporal = 'mes';
    
    const ahora = new Date();
    const inicioMes = new Date(ahora);
    inicioMes.setMonth(ahora.getMonth() - 1);
    
    this.aplicarFiltroTemporalPorRango(inicioMes, null, 'Últimos 30 días');
    this.mostrarNotificacion('📅 Mostrando ventas del último mes', 'info');
  },

  aplicarFiltroTemporalPorRango(fechaInicio, fechaFin, textoRango) {
    console.log('📅 Aplicando filtro temporal:', textoRango, 'Desde:', fechaInicio);
    
    // Filtrar filas por rango de fecha
    this.state.filteredRows = this.state.rows.filter(row => {
      const fechaTexto = row.dataset.fecha;
      if (!fechaTexto) return false;
      
      const fechaVenta = new Date(fechaTexto);
      
      // Verificar fecha de inicio
      if (fechaInicio && fechaVenta < fechaInicio) {
        return false;
      }
      
      // Verificar fecha de fin (si aplica)
      if (fechaFin && fechaVenta > fechaFin) {
        return false;
      }
      
      return true;
    });

    console.log(`✅ Filtro temporal aplicado: ${this.state.filteredRows.length} de ${this.state.rows.length} ventas`);
    
    // Actualizar KPIs con datos filtrados
    this.actualizarKPIsConFiltro();
    
    // Mostrar widget de filtro activo
    this.mostrarWidgetFiltroActivo(textoRango);
    
    // Actualizar contador de ventas
    this.actualizarContadorVentas();
    
    // Resetear a primera página
    this.state.page = 1;
    this.applyPagination();
  },

  mostrarWidgetFiltroActivo(textoRango) {
    // Buscar o crear el contenedor del widget en el header de la tabla
    const tableHeader = document.querySelector('#ventasTable').closest('.bg-\\[var\\(--card-bg-light\\)\\]').querySelector('.px-6.py-4.border-b');
    
    if (!tableHeader) {
      console.warn('⚠️ No se encontró el header de la tabla para agregar el widget');
      return;
    }
    
    // Remover widget existente si hay uno
    const widgetExistente = tableHeader.querySelector('.widget-filtro-activo');
    if (widgetExistente) {
      widgetExistente.remove();
    }
    
    // Crear el widget
    const widget = document.createElement('div');
    widget.className = 'widget-filtro-activo inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium bg-purple-500/20 border border-purple-500/40 text-purple-600 dark:text-purple-400 ml-2';
    widget.innerHTML = `
      <span class="material-symbols-outlined text-sm">schedule</span>
      <span class="font-semibold">Filtro:</span>
      <span>${textoRango}</span>
      <button class="material-symbols-outlined text-sm hover:text-white transition-colors widget-clear-btn">close</button>
    `;
    
    // Agregar evento para limpiar el filtro
    widget.querySelector('.widget-clear-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      this.limpiarFiltroTemporal();
    });
    
    // Agregar al final del header, al lado del contador de ventas
    const counterContainer = tableHeader.querySelector('.flex.items-center.gap-2');
    if (counterContainer) {
      counterContainer.appendChild(widget);
    }
    
    console.log('✅ Widget de filtro activo agregado');
  },

  limpiarFiltroTemporal() {
    console.log('🧹 Limpiando filtro temporal del header');
    
    this.state.filtroTemporalActivo = false;
    this.state.rangoTemporal = null;
    
    // Remover clase activa de botones del header
    const botonesHeader = document.querySelectorAll('.filtro-fecha-btn');
    botonesHeader.forEach(btn => btn.classList.remove('filtro-activo'));
    
    // Remover widget
    const widget = document.querySelector('.widget-filtro-activo');
    if (widget) {
      widget.remove();
    }
    
    // Restaurar todas las ventas
    this.state.filteredRows = [...this.state.rows];
    
    // Actualizar KPIs originales
    this.restaurarKPIsOriginales();
    
    // Actualizar contador
    this.actualizarContadorVentas();
    
    // Resetear a primera página
    this.state.page = 1;
    this.applyPagination();
    
    this.mostrarNotificacion('Filtro temporal eliminado', 'info');
  },

  actualizarKPIsConFiltro() {
    const ventasFiltradas = this.state.filteredRows;
    
    if (ventasFiltradas.length === 0) {
      // Actualizar KPIs a 0
      this.actualizarKPI('total-ventas', '$0');
      this.actualizarKPI('promedio-ventas', '$0');
      this.actualizarKPI('num-transacciones', '0');
      this.actualizarKPI('top-producto', 'N/A');
      return;
    }
    
    // Calcular total de ventas
    const totalVentas = ventasFiltradas.reduce((sum, row) => {
      return sum + parseFloat(row.dataset.total || 0);
    }, 0);
    
    // Calcular promedio
    const promedioVentas = totalVentas / ventasFiltradas.length;
    
    // Contar productos vendidos
    const productosCount = {};
    ventasFiltradas.forEach(row => {
      const idVenta = row.dataset.idventa;
      const ventaData = this.state.detallesVentas[idVenta];
      
      if (ventaData && ventaData.items) {
        ventaData.items.forEach(item => {
          const idProducto = item.idproducto;
          if (!productosCount[idProducto]) {
            productosCount[idProducto] = 0;
          }
          productosCount[idProducto] += item.cantidad || 0;
        });
      }
    });
    
    // Encontrar producto más vendido
    let topProductoId = null;
    let maxCantidad = 0;
    
    Object.entries(productosCount).forEach(([id, cantidad]) => {
      if (cantidad > maxCantidad) {
        maxCantidad = cantidad;
        topProductoId = id;
      }
    });
    
    const topProductoNombre = topProductoId ? (this.state.productosDict[topProductoId] || 'Desconocido') : 'N/A';
    
    // Actualizar KPIs en el DOM
    this.actualizarKPI('total-ventas', `$${this.formatearNumero(totalVentas)}`);
    this.actualizarKPI('promedio-ventas', `$${this.formatearNumero(promedioVentas)}`);
    this.actualizarKPI('num-transacciones', ventasFiltradas.length);
    this.actualizarKPI('top-producto', topProductoNombre);
    
    console.log('📊 KPIs actualizados con filtro:', {
      total: totalVentas,
      promedio: promedioVentas,
      transacciones: ventasFiltradas.length,
      topProducto: topProductoNombre
    });
  },

  restaurarKPIsOriginales() {
    // Restaurar valores originales desde los elementos del DOM que tienen data attributes o texto original
    // Los valores originales deben venir del servidor, así que simplemente recalculamos con todas las filas
    const todasLasVentas = this.state.rows;
    
    if (todasLasVentas.length === 0) {
      return;
    }
    
    // Calcular total de ventas
    const totalVentas = todasLasVentas.reduce((sum, row) => {
      return sum + parseFloat(row.dataset.total || 0);
    }, 0);
    
    // Calcular promedio
    const promedioVentas = totalVentas / todasLasVentas.length;
    
    // Contar productos vendidos
    const productosCount = {};
    todasLasVentas.forEach(row => {
      const idVenta = row.dataset.idventa;
      const ventaData = this.state.detallesVentas[idVenta];
      
      if (ventaData && ventaData.items) {
        ventaData.items.forEach(item => {
          const idProducto = item.idproducto;
          if (!productosCount[idProducto]) {
            productosCount[idProducto] = 0;
          }
          productosCount[idProducto] += item.cantidad || 0;
        });
      }
    });
    
    // Encontrar producto más vendido
    let topProductoId = null;
    let maxCantidad = 0;
    
    Object.entries(productosCount).forEach(([id, cantidad]) => {
      if (cantidad > maxCantidad) {
        maxCantidad = cantidad;
        topProductoId = id;
      }
    });
    
    const topProductoNombre = topProductoId ? (this.state.productosDict[topProductoId] || 'Desconocido') : 'N/A';
    
    // Actualizar KPIs en el DOM
    this.actualizarKPI('total-ventas', `$${this.formatearNumero(totalVentas)}`);
    this.actualizarKPI('promedio-ventas', `$${this.formatearNumero(promedioVentas)}`);
    this.actualizarKPI('num-transacciones', todasLasVentas.length);
    this.actualizarKPI('top-producto', topProductoNombre);
    
    console.log('📊 KPIs restaurados a valores originales');
  },

  actualizarKPI(tipo, valor) {
    // Mapeo de tipos a selectores
    const selectores = {
      'total-ventas': '.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4 > div:nth-child(1) p.text-2xl',
      'promedio-ventas': '.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4 > div:nth-child(2) p.text-2xl',
      'num-transacciones': '.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4 > div:nth-child(3) p.text-2xl',
      'top-producto': '.grid.grid-cols-1.md\\:grid-cols-2.lg\\:grid-cols-4 > div:nth-child(4) p.text-2xl'
    };
    
    const elemento = document.querySelector(selectores[tipo]);
    if (elemento) {
      elemento.textContent = valor;
    }
  },

  formatearNumero(numero) {
    // Formatear número con separadores de miles (punto) y sin decimales
    return Math.round(numero).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  },

  mostrarNotificacion(mensaje, tipo = 'info') {
    // Reutilizar la función global si existe
    if (typeof mostrarNotificacion === 'function') {
      mostrarNotificacion(mensaje, tipo);
    } else {
      console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
    }
  },

  bindFiltros() {
    // Aplicar filtros al presionar el botón
    this.btnAplicarFiltros?.addEventListener('click', () => {
      this.aplicarFiltros();
    });

    // Limpiar filtros
    this.btnLimpiarFiltros?.addEventListener('click', () => {
      this.limpiarFiltros();
    });

    // Aplicar filtros al presionar Enter en los inputs
    [this.filtroTotalMin, this.filtroTotalMax, this.filtroFechaDesde, this.filtroFechaHasta].forEach(input => {
      input?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.aplicarFiltros();
        }
      });
    });

    // Aplicar filtros al cambiar select
    [this.filtroProducto, this.filtroVendedor].forEach(select => {
      select?.addEventListener('change', () => {
        this.aplicarFiltros();
      });
    });
  },

  aplicarFiltros() {
    // Guardar valores de filtros
    this.state.filtrosActivos = {
      producto: this.filtroProducto?.value || '',
      vendedor: this.filtroVendedor?.value || '',
      fechaDesde: this.filtroFechaDesde?.value || '',
      fechaHasta: this.filtroFechaHasta?.value || '',
      totalMin: this.filtroTotalMin?.value || '',
      totalMax: this.filtroTotalMax?.value || ''
    };

    console.log('🔍 Aplicando filtros:', this.state.filtrosActivos);

    // Filtrar filas
    this.state.filteredRows = this.state.rows.filter(row => {
      // Filtro por producto
      if (this.state.filtrosActivos.producto) {
        const detalles = this.state.detallesVentas[row.dataset.idventa];
        if (!detalles || !detalles.items) return false;
        
        const tieneProducto = detalles.items.some(item => 
          item.idproducto == this.state.filtrosActivos.producto
        );
        if (!tieneProducto) return false;
      }

      // Filtro por vendedor
      if (this.state.filtrosActivos.vendedor) {
        if (row.dataset.vendedorRut !== this.state.filtrosActivos.vendedor) {
          return false;
        }
      }

      // Filtro por fecha desde
      if (this.state.filtrosActivos.fechaDesde) {
        const fechaVenta = row.dataset.fecha.split('T')[0];
        if (fechaVenta < this.state.filtrosActivos.fechaDesde) {
          return false;
        }
      }

      // Filtro por fecha hasta
      if (this.state.filtrosActivos.fechaHasta) {
        const fechaVenta = row.dataset.fecha.split('T')[0];
        if (fechaVenta > this.state.filtrosActivos.fechaHasta) {
          return false;
        }
      }

      // Filtro por total mínimo
      if (this.state.filtrosActivos.totalMin) {
        const total = parseFloat(row.dataset.total);
        if (total < parseFloat(this.state.filtrosActivos.totalMin)) {
          return false;
        }
      }

      // Filtro por total máximo
      if (this.state.filtrosActivos.totalMax) {
        const total = parseFloat(row.dataset.total);
        if (total > parseFloat(this.state.filtrosActivos.totalMax)) {
          return false;
        }
      }

      return true;
    });

    // Actualizar contador de ventas
    this.actualizarContadorVentas();

    // Mostrar chips de filtros activos
    this.mostrarFiltrosActivos();

    // Resetear a primera página
    this.state.page = 1;
    this.applyPagination();

    console.log(`✅ Filtros aplicados: ${this.state.filteredRows.length} de ${this.state.rows.length} ventas`);
  },

  limpiarFiltros() {
    // Limpiar inputs
    if (this.filtroProducto) this.filtroProducto.value = '';
    if (this.filtroVendedor) this.filtroVendedor.value = '';
    if (this.filtroFechaDesde) this.filtroFechaDesde.value = '';
    if (this.filtroFechaHasta) this.filtroFechaHasta.value = '';
    if (this.filtroTotalMin) this.filtroTotalMin.value = '';
    if (this.filtroTotalMax) this.filtroTotalMax.value = '';

    // Resetear estado
    this.state.filtrosActivos = {
      producto: '',
      vendedor: '',
      fechaDesde: '',
      fechaHasta: '',
      totalMin: '',
      totalMax: ''
    };

    // Mostrar todas las filas
    this.state.filteredRows = [...this.state.rows];

    // Ocultar chips de filtros activos
    if (this.filtrosActivosContainer) {
      this.filtrosActivosContainer.classList.add('hidden');
    }

    // Actualizar contador
    this.actualizarContadorVentas();

    // Resetear a primera página
    this.state.page = 1;
    this.applyPagination();

    console.log('🧹 Filtros limpiados');
  },

  mostrarFiltrosActivos() {
    if (!this.filtrosActivosChips || !this.filtrosActivosContainer) return;

    const chips = [];
    const filtros = this.state.filtrosActivos;

    // Chip de producto
    if (filtros.producto) {
      const nombreProducto = this.state.productosDict[filtros.producto] || `Producto ID ${filtros.producto}`;
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
          <span class="material-symbols-outlined text-sm">inventory_2</span>
          ${nombreProducto}
        </span>
      `);
    }

    // Chip de vendedor
    if (filtros.vendedor) {
      const nombreVendedor = this.filtroVendedor.options[this.filtroVendedor.selectedIndex].text;
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
          <span class="material-symbols-outlined text-sm">person</span>
          ${nombreVendedor}
        </span>
      `);
    }

    // Chip de fecha
    if (filtros.fechaDesde || filtros.fechaHasta) {
      let textoFecha = '';
      if (filtros.fechaDesde && filtros.fechaHasta) {
        textoFecha = `${filtros.fechaDesde} al ${filtros.fechaHasta}`;
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

    // Chip de total
    if (filtros.totalMin || filtros.totalMax) {
      let textoTotal = '';
      if (filtros.totalMin && filtros.totalMax) {
        textoTotal = `$${parseFloat(filtros.totalMin).toLocaleString('es-CL')} - $${parseFloat(filtros.totalMax).toLocaleString('es-CL')}`;
      } else if (filtros.totalMin) {
        textoTotal = `Mín: $${parseFloat(filtros.totalMin).toLocaleString('es-CL')}`;
      } else {
        textoTotal = `Máx: $${parseFloat(filtros.totalMax).toLocaleString('es-CL')}`;
      }
      chips.push(`
        <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200">
          <span class="material-symbols-outlined text-sm">attach_money</span>
          ${textoTotal}
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

  actualizarContadorVentas() {
    if (!this.ventasCounter) return;

    const total = this.state.filteredRows.length;
    const totalOriginal = this.state.rows.length;

    if (total === totalOriginal) {
      this.ventasCounter.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-green-600 dark:bg-green-400 mr-2 animate-pulse"></span>
        ${total} ventas
      `;
    } else {
      this.ventasCounter.innerHTML = `
        <span class="w-2 h-2 rounded-full bg-blue-600 dark:bg-blue-400 mr-2 animate-pulse"></span>
        ${total} de ${totalOriginal} ventas
      `;
    }
  },

  refreshRows() {
    // Actualiza la lista de filas desde el DOM
    this.state.rows = Array.from(document.querySelectorAll('.venta-row'));
    this.state.filteredRows = [...this.state.rows];
    this.actualizarContadorVentas();
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

    // Manejar fila de "No hay ventas"
    const noVentasRow = document.getElementById('noVentasRow');
    
    if (total === 0) {
      // Mostrar mensaje de no hay resultados
      if (noVentasRow) {
        noVentasRow.style.display = '';
        // Cambiar mensaje si hay filtros activos
        const hayFiltros = Object.values(this.state.filtrosActivos).some(v => v !== '');
        if (hayFiltros) {
          const cell = noVentasRow.querySelector('td');
          if (cell) {
            cell.innerHTML = `
              <div class="flex flex-col items-center justify-center gap-3 py-8">
                <div class="p-4 rounded-full bg-neutral-100 dark:bg-neutral-800">
                  <span class="material-symbols-outlined text-5xl text-neutral-400">search_off</span>
                </div>
                <p class="text-neutral-600 dark:text-neutral-400 font-medium">No se encontraron ventas con los filtros aplicados</p>
                <p class="text-sm text-neutral-500 dark:text-neutral-500">Intenta ajustar los criterios de búsqueda</p>
              </div>
            `;
          }
        }
      }
    } else {
      // Ocultar mensaje de no hay ventas
      if (noVentasRow) {
        noVentasRow.style.display = 'none';
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
      this.pageStats.textContent = total ? `${start + 1}–${end} de ${total}` : '0–0 de 0';
    }

    // Actualizar estado de botones de navegación
    if (this.pagePrev) {
      this.pagePrev.disabled = this.state.page === 1 || total === 0;
      this.pagePrev.style.opacity = (this.state.page === 1 || total === 0) ? '0.5' : '1';
      this.pagePrev.style.cursor = (this.state.page === 1 || total === 0) ? 'not-allowed' : 'pointer';
    }

    if (this.pageNext) {
      this.pageNext.disabled = this.state.page >= pages || total === 0;
      this.pageNext.style.opacity = (this.state.page >= pages || total === 0) ? '0.5' : '1';
      this.pageNext.style.cursor = (this.state.page >= pages || total === 0) ? 'not-allowed' : 'pointer';
    }

    console.log(`📄 Página ${this.state.page}/${pages} - Mostrando ${total > 0 ? start + 1 : 0} a ${end} de ${total}`);
  },

  mostrarDetalleVenta(idVenta) {
    console.log(`🔍 DEBUG: Mostrando detalles de venta #${idVenta}`);
    
    const ventaData = this.state.detallesVentas[idVenta];
    
    if (!ventaData || !ventaData.items || ventaData.items.length === 0) {
      console.warn(`⚠️ No se encontraron detalles para venta #${idVenta}`);
      this.modalContent.innerHTML = `
        <div class="text-center py-8">
          <span class="material-symbols-outlined text-6xl text-neutral-400">inbox</span>
          <p class="mt-4 text-neutral-600 dark:text-neutral-400">No hay detalles disponibles para esta venta</p>
        </div>
      `;
      this.modal.classList.remove('hidden');
      return;
    }

    console.log(`✅ DEBUG: Detalles encontrados:`, ventaData);

    const detalles = ventaData.items;
    const totalProductos = detalles.length;
    const totalUnidades = detalles.reduce((sum, d) => sum + (d.cantidad || 0), 0);
    const totalVenta = ventaData.total;

    // Formatear fecha
    const fecha = new Date(ventaData.fecha);
    const fechaFormateada = fecha.toLocaleDateString('es-CL', { 
      day: '2-digit', 
      month: 'long', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    // Construir HTML del modal con diseño mejorado
    let detallesHTML = detalles.map((det, index) => {
      const nombreProducto = this.state.productosDict[det.idproducto] || `Producto ID ${det.idproducto}`;
      return `
        <tr class="hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors">
          <td class="px-4 py-4 text-center text-neutral-600 dark:text-neutral-400">${index + 1}</td>
          <td class="px-4 py-4">
            <div class="flex flex-col">
              <span class="font-semibold text-neutral-900 dark:text-neutral-100">${nombreProducto}</span>
              <span class="text-xs text-neutral-500 dark:text-neutral-400">ID: ${det.idproducto}</span>
            </div>
          </td>
          <td class="px-4 py-4 text-center">
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
              ${det.cantidad} un.
            </span>
          </td>
          <td class="px-4 py-4 text-right text-neutral-700 dark:text-neutral-300">
            $${(det.precio_unitario || 0).toLocaleString('es-CL')}
          </td>
          <td class="px-4 py-4 text-right">
            <span class="font-semibold text-neutral-900 dark:text-neutral-100">
              $${(det.subtotal || 0).toLocaleString('es-CL')}
            </span>
          </td>
        </tr>
      `;
    }).join('');

    this.modalContent.innerHTML = `
      <!-- Header del Modal -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex items-center gap-4">
          <div class="p-3 rounded-xl bg-primary-100 dark:bg-primary-900/30">
            <span class="material-symbols-outlined text-3xl text-primary-600 dark:text-primary-400">receipt_long</span>
          </div>
          <div>
            <h2 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
              Venta #${idVenta}
            </h2>
            <p class="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
              <span class="material-symbols-outlined text-sm align-middle">calendar_today</span>
              ${fechaFormateada}
            </p>
          </div>
        </div>
        <button class="btn-cerrar-modal p-2 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition-colors">
          <span class="material-symbols-outlined text-neutral-600 dark:text-neutral-400">close</span>
        </button>
      </div>

      <!-- Información del Vendedor -->
      <div class="mb-6 p-4 rounded-lg bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800">
        <div class="flex items-center gap-3">
          <div class="p-2 rounded-lg bg-white dark:bg-neutral-800 shadow-sm">
            <span class="material-symbols-outlined text-blue-600 dark:text-blue-400">person</span>
          </div>
          <div>
            <p class="text-xs font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wide">Atendido por</p>
            <p class="text-lg font-bold text-neutral-900 dark:text-neutral-100">${ventaData.vendedorNombre}</p>
            <p class="text-sm text-neutral-600 dark:text-neutral-400">RUT: ${ventaData.vendedorRut}</p>
          </div>
        </div>
      </div>

      <!-- Tarjetas de Resumen -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="p-4 rounded-lg bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
          <p class="text-xs font-medium text-purple-600 dark:text-purple-400 mb-1">Productos</p>
          <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">${totalProductos}</p>
        </div>
        <div class="p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
          <p class="text-xs font-medium text-green-600 dark:text-green-400 mb-1">Unidades</p>
          <p class="text-2xl font-bold text-green-900 dark:text-green-100">${totalUnidades}</p>
        </div>
        <div class="p-4 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800">
          <p class="text-xs font-medium text-amber-600 dark:text-amber-400 mb-1">Total</p>
          <p class="text-2xl font-bold text-amber-900 dark:text-amber-100">$${totalVenta.toLocaleString('es-CL')}</p>
        </div>
      </div>

      <!-- Tabla de Productos -->
      <div class="mb-4">
        <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-3 flex items-center gap-2">
          <span class="material-symbols-outlined text-primary-600 dark:text-primary-400">inventory_2</span>
          Productos Vendidos
        </h3>
        <div class="overflow-x-auto rounded-lg border border-gray-300 dark:border-neutral-700">
          <table class="w-full text-sm">
            <thead class="bg-neutral-100 dark:bg-neutral-800 border-b border-gray-300 dark:border-neutral-700">
              <tr>
                <th class="px-4 py-3 text-center font-semibold text-neutral-700 dark:text-neutral-300">#</th>
                <th class="px-4 py-3 text-left font-semibold text-neutral-700 dark:text-neutral-300">Producto</th>
                <th class="px-4 py-3 text-center font-semibold text-neutral-700 dark:text-neutral-300">Cantidad</th>
                <th class="px-4 py-3 text-right font-semibold text-neutral-700 dark:text-neutral-300">Precio Unit.</th>
                <th class="px-4 py-3 text-right font-semibold text-neutral-700 dark:text-neutral-300">Subtotal</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-neutral-700 bg-white dark:bg-neutral-900">
              ${detallesHTML}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Total Final -->
      <div class="mt-6 p-5 rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="p-2 rounded-lg bg-white/20">
              <span class="material-symbols-outlined text-2xl">paid</span>
            </div>
            <div>
              <p class="text-sm font-medium opacity-90">Total de la Venta</p>
              <p class="text-3xl font-bold">$${totalVenta.toLocaleString('es-CL')}</p>
            </div>
          </div>
          <div class="text-right">
            <p class="text-xs opacity-75">Incluye ${totalProductos} producto${totalProductos !== 1 ? 's' : ''}</p>
            <p class="text-xs opacity-75">${totalUnidades} unidad${totalUnidades !== 1 ? 'es' : ''} en total</p>
          </div>
        </div>
      </div>
    `;

    this.modal.classList.remove('hidden');
    console.log('✅ Modal abierto correctamente');
  },

  cerrarModal() {
    if (this.modal) {
      this.modal.classList.add('hidden');
      console.log('🔒 Modal cerrado');
    }
  }
};

// ===========================================================
// Modal para Crear Nueva Venta
// ===========================================================

const NuevaVenta = {
  productosSeleccionados: [],

  init() {
    this.cacheDOM();
    this.bindEvents();
    console.info("✅ Modal Nueva Venta inicializado");
  },

  cacheDOM() {
    this.btnCrearVenta = document.getElementById('btn-crear-venta');
    this.modalVenta = document.getElementById('modal-nueva-venta');
    this.formVenta = document.getElementById('form-nueva-venta');
    this.productosContainer = document.getElementById('productos-venta-list');
    this.totalVenta = document.getElementById('total-venta');
  },

  bindEvents() {
    // Abrir modal
    this.btnCrearVenta?.addEventListener('click', () => this.abrirModal());

    // Cerrar modal
    document.querySelectorAll('.close-modal-venta').forEach(btn => {
      btn.addEventListener('click', () => this.cerrarModal());
    });

    // Cerrar al hacer click fuera
    this.modalVenta?.addEventListener('click', (e) => {
      if (e.target === this.modalVenta) {
        this.cerrarModal();
      }
    });

    // Agregar producto
    document.getElementById('btn-agregar-producto')?.addEventListener('click', () => {
      this.agregarProducto();
    });

    // Enviar formulario
    this.formVenta?.addEventListener('submit', (e) => {
      e.preventDefault();
      this.guardarVenta();
    });
  },

  async abrirModal() {
    this.productosSeleccionados = [];
    this.modalVenta?.classList.remove('hidden');
    await this.cargarProductos();
    this.renderProductos();
  },

  cerrarModal() {
    this.modalVenta?.classList.add('hidden');
    this.productosSeleccionados = [];
    this.formVenta?.reset();
  },

  async cargarProductos() {
    try {
      const response = await fetch('/api/productos/disponibles');
      const productos = await response.json();
      
      const select = document.getElementById('producto-select');
      if (!select) return;

      select.innerHTML = '<option value="">Seleccione un producto</option>' +
        productos.map(p => `
          <option value="${p.idproducto}" 
                  data-precio="${p.precio_unitario}" 
                  data-stock="${p.stock}">
            ${p.nombre} - Stock: ${p.stock} - $${p.precio_unitario.toLocaleString('es-CL')}
          </option>
        `).join('');
      
      console.log('✅ Productos cargados:', productos.length);
    } catch (error) {
      if (window.errorLogger) {
        window.errorLogger.critical('Error al cargar productos', 'ventas', '', error);
      }
      console.error('❌ Error al cargar productos:', error);
    }
  },

  agregarProducto() {
    const select = document.getElementById('producto-select');
    const cantidadInput = document.getElementById('cantidad-producto');
    
    if (!select || !cantidadInput) return;

    const idproducto = parseInt(select.value);
    const cantidad = parseInt(cantidadInput.value);
    const option = select.options[select.selectedIndex];
    const precio_unitario = parseFloat(option.dataset.precio);
    const stock = parseInt(option.dataset.stock);
    const nombre = option.text.split(' - ')[0];

    // Validaciones
    if (!idproducto) {
      alert('Debe seleccionar un producto');
      return;
    }

    if (!cantidad || cantidad <= 0) {
      alert('La cantidad debe ser mayor a 0');
      return;
    }

    if (cantidad > stock) {
      alert(`Stock insuficiente. Disponible: ${stock}`);
      return;
    }

    // Verificar si ya existe
    const existe = this.productosSeleccionados.find(p => p.idproducto === idproducto);
    if (existe) {
      if (existe.cantidad + cantidad > stock) {
        alert(`Stock insuficiente. Ya agregó ${existe.cantidad}, disponible: ${stock}`);
        return;
      }
      existe.cantidad += cantidad;
    } else {
      this.productosSeleccionados.push({
        idproducto,
        nombre,
        cantidad,
        precio_unitario,
        stock
      });
    }

    // Resetear selección
    select.value = '';
    cantidadInput.value = '1';

    this.renderProductos();
    console.log('✅ Producto agregado:', { idproducto, nombre, cantidad });
  },

  renderProductos() {
    if (!this.productosContainer) return;

    if (this.productosSeleccionados.length === 0) {
      this.productosContainer.innerHTML = `
        <div class="text-center py-8 text-neutral-500 dark:text-neutral-400">
          <span class="material-symbols-outlined text-5xl mb-2">shopping_cart</span>
          <p>No hay productos agregados</p>
        </div>
      `;
      this.totalVenta.textContent = '$0';
      return;
    }

    let total = 0;
    this.productosContainer.innerHTML = this.productosSeleccionados.map((p, index) => {
      const subtotal = p.cantidad * p.precio_unitario;
      total += subtotal;

      return `
        <div class="flex items-center justify-between p-3 bg-neutral-50 dark:bg-neutral-800 rounded-lg">
          <div class="flex-1">
            <p class="font-semibold text-neutral-900 dark:text-neutral-100">${p.nombre}</p>
            <p class="text-sm text-neutral-600 dark:text-neutral-400">
              ${p.cantidad} x $${p.precio_unitario.toLocaleString('es-CL')}
            </p>
          </div>
          <div class="text-right mr-3">
            <p class="font-bold text-neutral-900 dark:text-neutral-100">
              $${subtotal.toLocaleString('es-CL')}
            </p>
          </div>
          <button type="button" 
                  class="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
                  onclick="NuevaVenta.eliminarProducto(${index})">
            <span class="material-symbols-outlined">delete</span>
          </button>
        </div>
      `;
    }).join('');

    this.totalVenta.textContent = `$${total.toLocaleString('es-CL')}`;
  },

  eliminarProducto(index) {
    this.productosSeleccionados.splice(index, 1);
    this.renderProductos();
  },

  async guardarVenta() {
    if (this.productosSeleccionados.length === 0) {
      alert('Debe agregar al menos un producto');
      return;
    }

    const btnSubmit = this.formVenta.querySelector('button[type="submit"]');
    const originalText = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Guardando...';

    try {
      // Obtener CSRF token del meta tag
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
      
      const response = await fetch('/api/ventas/nueva', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ productos: this.productosSeleccionados })
      });

      const result = await response.json();

      if (result.success) {
        alert(`✅ Venta registrada exitosamente\nID Venta: #${result.id_venta}\nTotal: $${result.total.toLocaleString('es-CL')}`);
        this.cerrarModal();
        window.location.reload(); // Recargar para ver la nueva venta
      } else {
        alert(`❌ Error: ${result.error}`);
      }
    } catch (error) {
      if (window.errorLogger) {
        window.errorLogger.critical('Error al guardar venta', 'ventas', '', error);
      }
      console.error('❌ Error al guardar venta:', error);
      alert('Error al guardar la venta. Por favor, intente nuevamente.');
    } finally {
      btnSubmit.disabled = false;
      btnSubmit.innerHTML = originalText;
    }
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  Ventas.init();
  NuevaVenta.init();
  initBotonesAccion();
});

// ===========================================================
// Funciones para Botones de Acción
// ===========================================================

function initBotonesAccion() {
  // Botón "Exportar reporte"
  const btnExportar = document.getElementById('btn-exportar-reporte');
  if (btnExportar) {
    btnExportar.addEventListener('click', () => {
      exportarReporteVentas();
    });
  }

  console.log('✅ Botones de acción inicializados correctamente');
}

async function exportarReporteVentas() {
  try {
    const ventas = Ventas.state.filteredRows;
    
    if (ventas.length === 0) {
      mostrarNotificacion('No hay ventas para exportar', 'warning');
      return;
    }

    // Mostrar notificación de carga
    mostrarNotificacion('📊 Generando archivo Excel profesional...', 'info');

    // Preparar filtros de fecha si existen
    const filtros = {
      fechaDesde: Ventas.state.filters?.dateStart || null,
      fechaHasta: Ventas.state.filters?.dateEnd || null
    };

    // Llamar al endpoint del backend
    const response = await fetch('/api/ventas/exportar-excel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filtros })
    });

    if (!response.ok) {
      throw new Error(`Error del servidor: ${response.status}`);
    }

    // Obtener el blob del archivo
    const blob = await response.blob();
    
    // Crear URL temporal y descargar
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    
    // Nombre del archivo
    const fecha = new Date().toISOString().split('T')[0];
    link.download = `Weigence_Ventas_${fecha}.xlsx`;
    
    // Simular click para descargar
    document.body.appendChild(link);
    link.click();
    
    // Limpiar
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    mostrarNotificacion(`✅ Reporte de ventas exportado: ${ventas.length} registros`, 'success');
    console.log('✅ Reporte exportado:', ventas.length, 'ventas');
    
  } catch (error) {
    if (window.errorLogger) {
      window.errorLogger.error('Error al exportar reporte', 'ventas', '', error);
    }
    console.error('❌ Error al exportar reporte:', error);
    mostrarNotificacion('Error al exportar el reporte. Intente nuevamente.', 'error');
  }
}

function formatearFecha(fechaISO) {
  const fecha = new Date(fechaISO);
  return fecha.toLocaleDateString('es-CL', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function mostrarNotificacion(mensaje, tipo = 'info') {
  // Crear elemento de notificación
  const notificacion = document.createElement('div');
  notificacion.className = `fixed top-4 right-4 z-[9999] px-6 py-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-[400px]`;
  
  // Estilos según tipo
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
  
  // Animar entrada
  setTimeout(() => {
    notificacion.style.transform = 'translateX(0)';
  }, 10);
  
  // Remover después de 3 segundos
  setTimeout(() => {
    notificacion.style.transform = 'translateX(400px)';
    setTimeout(() => {
      notificacion.remove();
    }, 300);
  }, 3000);
}
