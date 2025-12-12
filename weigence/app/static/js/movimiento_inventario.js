document.addEventListener("DOMContentLoaded", async () => {
  const detalle = document.getElementById("detalle-contextual");
  const contenedor = document.getElementById("timeline-container");
  const cerrarBtn = document.getElementById("cerrar-detalle");
  let movimientos = Array.isArray(window.MOVIMIENTOS) ? window.MOVIMIENTOS : [];
  let pinnedMovimiento = null;
  
  // Estado de paginación
  let paginacion = {
    actual: 1,
    porPagina: 8,
    total: movimientos.length
  };

  console.log("Movimientos cargados:", movimientos.length, "| Paginación:", paginacion);

  const fTipo = document.getElementById("filter-type");
  const fUser = document.getElementById("filter-user");
  const fDateFrom = document.getElementById("filter-date-from");
  const fDateTo = document.getElementById("filter-date-to");
  const panelFiltros = document.getElementById("panel-filtros");
  const btnToggleFilters = document.getElementById("btn-toggle-filters");
  const btnClearFilters = document.getElementById("btn-clear-filters");

  // Leer parámetro id de la URL
  const urlParams = new URLSearchParams(window.location.search);
  const movimientoId = urlParams.get('id');

  console.log("Elementos DOM encontrados:", { // Log 2: Verificar elementos DOM
    detalle: !!detalle,
    contenedor: !!contenedor,
    cerrarBtn: !!cerrarBtn,
    fTipo: !!fTipo,
    fUser: !!fUser,
    fDateFrom: !!fDateFrom,
    fDateTo: !!fDateTo,
    panelFiltros: !!panelFiltros,
    btnToggleFilters: !!btnToggleFilters
  });

  if (!detalle || !contenedor) {
    console.error("Elementos requeridos no encontrados");
    return;
  }

  // Función para poblar el select de usuarios
  function cargarUsuariosFiltro() {
    if (!fUser) return;
    
    // Obtener usuarios únicos de los movimientos
    const usuariosUnicos = [...new Set(movimientos.map(m => m.usuario_nombre))].sort();
    
    // Limpiar opciones existentes (excepto la primera "Todos")
    fUser.innerHTML = '<option value="">Todos los usuarios</option>';
    
    // Agregar opciones de usuarios
    usuariosUnicos.forEach(usuario => {
      if (usuario && usuario !== "Usuario no registrado") {
        const option = document.createElement('option');
        option.value = usuario.toLowerCase();
        option.textContent = usuario;
        fUser.appendChild(option);
      }
    });
    
    console.log("Usuarios cargados en filtro:", usuariosUnicos.length);
  }

  // Cargar usuarios al inicio
  cargarUsuariosFiltro();

  // Función para mostrar notificaciones toast
  function mostrarToast(mensaje, tipo = 'info') {
    const colores = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      warning: 'bg-yellow-500',
      info: 'bg-blue-500'
    };

    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 ${colores[tipo]} text-white px-6 py-3 rounded-lg shadow-lg z-[100] animate-slideInRight`;
    toast.textContent = mensaje;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // Función para cargar movimiento desde historial
  async function cargarMovimientoPinned(id) {
    try {
      const response = await fetch(`/api/movimientos/${id}`);
      const data = await response.json();
      
      if (data.success && data.movimiento) {
        pinnedMovimiento = data.movimiento;
        renderizarMovimientos();
        
        // Esperar a que el DOM se actualice y luego mostrar detalle
        setTimeout(() => {
          seleccionarMovimiento(pinnedMovimiento, true);
          
          // Scroll suave al detalle
          document.getElementById('detalle-movimiento')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
        return true;
      } else {
        console.error('Movimiento no encontrado:', data.error);
        mostrarToast('Movimiento no encontrado', 'error');
        return false;
      }
    } catch (error) {
      console.error('Error al cargar movimiento:', error);
      mostrarToast('Error al cargar el movimiento', 'error');
      return false;
    }
  }

  // Función para remover movimiento pinned
  function removerPinned() {
    pinnedMovimiento = null;
    // Limpiar URL sin recargar
    const url = new URL(window.location);
    url.searchParams.delete('id');
    window.history.replaceState({}, '', url);
    renderizarMovimientos();
  }

  // Función de renderizado completa con paginación
  function renderizarMovimientos() {
    console.log("Renderizando movimientos:", {
      cantidadMovimientos: movimientos.length,
      tienePinned: !!pinnedMovimiento,
      pagina: paginacion.actual,
      porPagina: paginacion.porPagina
    });

    let html = '';

    // Renderizar movimiento pinned si existe (minimalista y profesional)
    if (pinnedMovimiento) {
      const m = pinnedMovimiento;
      const color = m.tipo_evento === "Añadir" ? "green"
                  : m.tipo_evento === "Retirar" ? "red" : "blue";

      html += `
        <div class="pinned-item relative pl-8 mb-6 cursor-pointer group"
             data-pinned="true"
             data-tipo="${m.tipo_evento}" 
             data-user="${(m.usuario_nombre || '').toLowerCase()}"
             draggable="true">
          
          <!-- Botón cerrar -->
          <button onclick="event.stopPropagation(); removerPinned()" 
                  class="absolute -top-2 right-2 w-6 h-6 bg-neutral-200 hover:bg-red-500 dark:bg-neutral-700 dark:hover:bg-red-600 text-neutral-600 hover:text-white dark:text-neutral-300 dark:hover:text-white rounded flex items-center justify-center transition-colors z-10"
                  title="Quitar">
            <span class="material-symbols-outlined text-sm">close</span>
          </button>

          <div class="absolute left-0 top-6 w-5 h-5 rounded-full bg-${color}-500 ring-4 ring-[var(--card-bg-light)] dark:ring-[var(--card-bg-dark)]"></div>
          <div class="ml-4 p-6 rounded-xl border-l-4 border-t border-r border-b border-l-blue-400 border-t-neutral-200 border-r-neutral-200 border-b-neutral-200 dark:border-l-neutral-600 dark:border-t-[var(--border-dark)] dark:border-r-[var(--border-dark)] dark:border-b-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] shadow-md hover:shadow-lg transition-all">
            
            <!-- Mensaje minimalista profesional -->
            <div class="mb-3 pb-3 border-b border-neutral-200 dark:border-neutral-700">
              <p class="text-[11px] text-neutral-500 dark:text-neutral-400 flex items-center gap-1.5">
                <span class="material-symbols-outlined text-xs">history</span>
                Movimiento traído desde historial
              </p>
            </div>
            
            <div class="flex items-start justify-between">
              <div>
                <p class="text-lg font-bold text-[var(--text-light)] dark:text-[var(--text-dark)]">
                  ${m.tipo_evento === "Añadir" ? "➕" :
                    m.tipo_evento === "Retirar" ? "➖" : "⟳"} ${m.producto}
                </p>
                <p class="text-sm text-neutral-600 dark:text-neutral-400 mt-2">
                  ${m.ubicacion} • ${m.usuario_nombre}
                </p>
              </div>
              <div class="text-right">
                <p class="text-lg font-bold ${
                  m.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-500"
                  : m.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-500"
                  : "text-blue-600 dark:text-blue-500"
                }">
                  ${
                    m.tipo_evento === "Añadir" ? "+" 
                    : m.tipo_evento === "Retirar" ? "-" 
                    : m.tipo_evento === "gris" && m.cantidad < 0 ? "-"
                    : m.tipo_evento === "gris" && m.cantidad > 0 ? "+"
                    : ""
                  }${(m.peso_total || 0).toFixed(2)}kg
                </p>
                <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
                  ${m.cantidad} unid × ${(m.peso_por_unidad || 0).toFixed(2)}kg
                </p>
                <p class="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
                  ${(m.timestamp || "").split(" ")[1]?.slice(0,5) || ""}
                </p>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // Paginación: calcular movimientos a mostrar
    const inicio = (paginacion.actual - 1) * paginacion.porPagina;
    const fin = inicio + paginacion.porPagina;
    const lista = movimientos.slice(inicio, fin);
    const totalPaginas = Math.ceil(movimientos.length / paginacion.porPagina);
    
    console.log("📄 Paginación:", {
      paginaActual: paginacion.actual,
      porPagina: paginacion.porPagina,
      totalMovimientos: movimientos.length,
      totalPaginas: totalPaginas,
      inicio: inicio,
      fin: fin,
      itemsEnPagina: lista.length
    });

    html += lista.map((m, i) => {
  const indexReal = inicio + i; // Índice real en el array completo
  let color = m.tipo_evento === "Añadir" ? "green"
              : m.tipo_evento === "Retirar" ? "red"
              : m.tipo_evento === "VentaPendiente" ? "yellow"
              : "blue";

  return `
    <div class="timeline-item relative mb-3 cursor-pointer group"
         data-index="${indexReal}" 
         data-tipo="${m.tipo_evento}" 
         data-user="${(m.usuario_nombre || '').toLowerCase()}"
         draggable="true">
      <!-- Punto en timeline -->
      <div class="absolute -left-3 top-3 w-3 h-3 rounded-full bg-${color}-500 ring-4 ring-[var(--bg-light)] dark:ring-[var(--bg-dark)] z-10"></div>
      
      <!-- Línea vertical conectora -->
      <div class="absolute -left-[9px] top-6 bottom-0 w-0.5 bg-neutral-300 dark:bg-neutral-700"></div>
      
      <!-- Tarjeta -->
      <div class="ml-4 p-2.5 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] shadow-sm hover:shadow-md hover:border-primary-400 dark:hover:border-primary-600 transition-all duration-200">
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-1.5 flex-1 min-w-0">
            ${m.tipo_evento === "VentaPendiente" ? `<span class="material-symbols-outlined animate-spin text-yellow-500 text-base flex-shrink-0">autorenew</span>` :
              m.tipo_evento === "Añadir" ? `<span class="material-symbols-outlined text-green-600 dark:text-green-500 text-base flex-shrink-0">arrow_upward</span>` :
              m.tipo_evento === "Retirar" ? `<span class="material-symbols-outlined text-red-600 dark:text-red-500 text-base flex-shrink-0">arrow_downward</span>` :
              `<span class="material-symbols-outlined text-blue-600 dark:text-blue-500 text-base flex-shrink-0">sync_alt</span>`}
            <p class="text-xs font-semibold text-[var(--text-light)] dark:text-[var(--text-dark)] truncate">
              ${m.producto}
            </p>
          </div>
          <div class="text-right flex-shrink-0">
            <p class="text-sm font-bold ${
              m.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-500"
              : m.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-500"
              : m.tipo_evento === "VentaPendiente" ? "text-yellow-500"
              : "text-blue-600 dark:text-blue-500"
            }">
              ${
                m.tipo_evento === "Añadir" ? "+" 
                : m.tipo_evento === "Retirar" ? "-" 
                : m.tipo_evento === "gris" && m.cantidad < 0 ? "-"
                : m.tipo_evento === "gris" && m.cantidad > 0 ? "+"
                : ""
              }${(m.peso_total || 0).toFixed(2)}kg
            </p>
            <p class="text-[10px] text-neutral-500 dark:text-neutral-400">
              ${(m.timestamp || "").split(" ")[1]?.slice(0,5) || ""}
            </p>
          </div>
        </div>
      </div>
    </div>
  `;
}).join("");

    // Agregar controles de paginación
    if (totalPaginas > 1) {
      html += `
        <div class="flex items-center justify-between mt-6 pt-4 border-t border-neutral-300 dark:border-[var(--border-dark)]">
          <button id="btn-prev-page" ${paginacion.actual === 1 ? 'disabled' : ''} 
                  class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <span class="material-symbols-outlined text-sm">chevron_left</span>
            <span>Anterior</span>
          </button>
          
          <div class="flex items-center gap-2">
            <span class="text-xs text-neutral-600 dark:text-neutral-400">
              Página ${paginacion.actual} de ${totalPaginas}
            </span>
            <span class="text-xs text-neutral-500 dark:text-neutral-500">
              (${movimientos.length} total)
            </span>
          </div>
          
          <button id="btn-next-page" ${paginacion.actual === totalPaginas ? 'disabled' : ''} 
                  class="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] hover:bg-neutral-100 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
            <span>Siguiente</span>
            <span class="material-symbols-outlined text-sm">chevron_right</span>
          </button>
        </div>
      `;
    }
    
    // Agregar botón de historial completo
    html += `
      <div class="flex justify-center mt-4">
        <button class="btn-show-history text-sm text-primary-500 dark:text-primary-400 hover:underline underline-offset-2 focus:outline-none flex items-center gap-1">
          <span class="material-symbols-outlined text-sm">history</span>
          <span>Ver historial completo (${movimientos.length} registros)</span>
        </button>
      </div>
    `;

    contenedor.innerHTML = html;
    
    // Agregar listeners de paginación DESPUÉS de insertar el HTML
    const btnPrev = document.getElementById('btn-prev-page');
    const btnNext = document.getElementById('btn-next-page');
    
    if (btnPrev) {
      btnPrev.addEventListener('click', (e) => {
        e.preventDefault();
        console.log("⬅️ Click en Anterior. Página actual:", paginacion.actual);
        if (paginacion.actual > 1) {
          paginacion.actual--;
          console.log("⬅️ Nueva página:", paginacion.actual);
          renderizarMovimientos();
          // Scroll suave al inicio del contenedor
          contenedor.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
    }
    
    if (btnNext) {
      btnNext.addEventListener('click', (e) => {
        e.preventDefault();
        console.log("➡️ Click en Siguiente. Página actual:", paginacion.actual, "Total páginas:", totalPaginas);
        if (paginacion.actual < totalPaginas) {
          paginacion.actual++;
          console.log("➡️ Nueva página:", paginacion.actual);
          renderizarMovimientos();
          // Scroll suave al inicio del contenedor
          contenedor.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
          console.log("➡️ Ya estás en la última página");
        }
      });
    }
    
    // El listener para .btn-show-history ya está manejado por historial.js globalmente

    console.log("HTML generado, pinned:", !!pinnedMovimiento, "Página:", paginacion.actual, "Items mostrados:", lista.length);
  }

  // Función auxiliar para crear bloques de información
  function info(label, value) {
    return `
      <div class="bg-neutral-100 dark:bg-[var(--card-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg p-3">
        <p class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)] uppercase tracking-wide">${label}</p>
        <p class="text-[14px] font-semibold text-[var(--text-light)] dark:text-white mt-1">${value || "—"}</p>
      </div>
    `;
  }

  // Función para seleccionar y mostrar detalles de movimiento
  function seleccionarMovimiento(m, isPinned = false) {
    // Remover selección previa de todos los items
    document.querySelectorAll('.timeline-item').forEach(item => {
      item.classList.remove('item-activo', 'ring-2', 'ring-primary-400/50', 'ring-primary-500/60', 'selected', 'ring-gray-500/60');
    });

    // Marcar visualmente el item seleccionado si NO es pinned
    if (!isPinned) {
      const idx = movimientos.indexOf(m);
      const selectedItem = document.querySelector(`.timeline-item[data-index="${idx}"]`);
      if (selectedItem) {
        selectedItem.classList.add(
          'item-activo',
          'ring-2',
          document.documentElement.classList.contains('dark')
            ? 'ring-gray-500/60'
            : 'ring-gray-500/60',
          'selected'
        );
      }
    }

    // Mostrar detalles usando la función existente renderDetalle
    // Primero necesitamos encontrar el índice en el array de movimientos
    const idx = movimientos.indexOf(m);
    if (idx >= 0) {
      renderDetalle(idx);
    } else if (isPinned) {
      // Si es pinned, mostrar directamente
      renderDetalleDirecto(m);
    }
  }

  // Función auxiliar para renderizar detalles de movimiento pinned
  function renderDetalleDirecto(m) {
    // Usar el mismo formato que renderDetalle
    const tipo = {
      "Añadir": { icon: "south", color: "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/40" },
      "Retirar": { icon: "north", color: "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/40" },
      "VentaPendiente": { icon: "autorenew", color: "text-yellow-500 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/40 animate-spin-slow" },
      "Mover": { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" },
    }[m.tipo_evento] || { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" };

    const relacionados = window.MOVIMIENTOS ? window.MOVIMIENTOS.filter(x => x.producto === m.producto).slice(0, 5) : [];

    detalle.className = "min-h-[46vh] flex flex-col bg-[var(--card-bg-light)] dark:bg-[var(--card-sub-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg overflow-hidden transition-all duration-300";

    detalle.innerHTML = `
      <!-- Header compacto -->
      <div class="relative ${tipo.color} border-b border-neutral-300 dark:border-[var(--border-dark)] p-3">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2.5 flex-1 min-w-0">
            <div class="w-9 h-9 flex items-center justify-center rounded-lg bg-white dark:bg-neutral-900 shadow-sm flex-shrink-0">
              <span class="material-symbols-outlined text-xl ${tipo.color.split(' ')[0]}">${tipo.icon}</span>
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="text-sm font-bold text-[var(--text-light)] dark:text-white truncate">${m.producto}</h2>
            </div>
          </div>
          <div class="text-right flex-shrink-0">
            <p class="text-[10px] text-neutral-600 dark:text-neutral-400 flex items-center justify-end gap-1">
              <span class="material-symbols-outlined text-xs">schedule</span>
              ${new Date(m.timestamp).toLocaleString("es-ES", {dateStyle: 'short', timeStyle: 'short'})}
            </p>
          </div>
        </div>
      </div>

      <!-- Contenido compacto en grid 2 columnas -->
      <div class="p-3 overflow-auto">
        <!-- Resumen de peso compacto (ancho completo) -->
        <div class="grid grid-cols-3 gap-2 mb-3">
          <div class="p-2 rounded-lg border-2 ${tipo.color.includes('green') ? 'border-green-300 dark:border-green-800 bg-green-50 dark:bg-green-900/20' : tipo.color.includes('red') ? 'border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/20' : 'border-blue-300 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20'} text-center">
            <span class="material-symbols-outlined ${tipo.color.split(' ')[0]} text-lg">scale</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Peso Total</p>
            <p class="text-xl font-bold ${tipo.color.split(' ')[0]}">${(m.peso_total || 0).toFixed(2)}</p>
            <p class="text-[10px] text-neutral-500">kg</p>
          </div>
          <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] text-center">
            <span class="material-symbols-outlined text-primary-500 text-lg">inventory_2</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Cantidad</p>
            <p class="text-xl font-bold text-[var(--text-light)] dark:text-white">${m.cantidad}</p>
            <p class="text-[10px] text-neutral-500">unid.</p>
          </div>
          <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] text-center">
            <span class="material-symbols-outlined text-primary-500 text-lg">balance</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Peso/Unid.</p>
            <p class="text-xl font-bold text-[var(--text-light)] dark:text-white">${(m.peso_por_unidad || 0).toFixed(2)}</p>
            <p class="text-[10px] text-neutral-500">kg/u</p>
          </div>
        </div>

        <!-- Grid 2 columnas: Info + Historial -->
        <div class="grid grid-cols-2 gap-3">
          <!-- Columna izquierda: Información + Observación -->
          <div class="space-y-1.5">
            <h3 class="text-xs font-bold text-[var(--text-light)] dark:text-white flex items-center gap-1.5 mb-0.5">
              <span class="material-symbols-outlined text-base">info</span>
              Información
            </h3>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">location_on</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">Ubicación</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.ubicacion}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">person</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">Usuario</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.usuario_nombre}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">badge</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">RUT</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.rut_usuario || "—"}</p>
              </div>
            </div>
            ${m.observacion ? `
              <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-neutral-50 dark:bg-[var(--card-bg-dark)]">
                <div class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-warning-500 text-lg flex-shrink-0">notes</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mb-1">Observación</p>
                    <p class="text-xs text-neutral-800 dark:text-neutral-200 break-words">${m.observacion}</p>
                  </div>
                </div>
              </div>
            ` : ''}
          </div>

          <!-- Columna derecha: Historial del producto -->
          <div class="space-y-1.5">
            <h3 class="text-xs font-bold text-[var(--text-light)] dark:text-white flex items-center gap-1.5 mb-0.5">
              <span class="material-symbols-outlined text-base">history</span>
              Historial de ${m.producto}
            </h3>
            ${relacionados.slice(0, 4).map(r => {
              const rColor = r.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-400" :
                             r.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-400" :
                             "text-blue-600 dark:text-blue-400";
              return `
                <div class="p-2 rounded-lg border border-neutral-200 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors duration-200">
                  <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-1.5">
                      <span class="material-symbols-outlined text-sm ${rColor}">${
                        r.tipo_evento === "Añadir" ? "south" :
                        r.tipo_evento === "Retirar" ? "north" : "sync_alt"
                      }</span>
                      <span class="text-xs text-neutral-700 dark:text-neutral-300">
                        <span class="font-semibold">${r.tipo_evento}</span>
                      </span>
                    </div>
                    <div class="text-right">
                      <p class="text-xs font-semibold ${rColor}">${(r.peso_total || 0).toFixed(2)}kg</p>
                      <p class="text-[10px] text-neutral-500">${String(r.timestamp).split(" ")[1]?.slice(0,5) || ""}</p>
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `;
    
    // Mostrar sección de estadísticas
    const statsSection = document.getElementById('stats-producto');
    if (statsSection) {
      statsSection.classList.remove('hidden');
    }
    // Cargar estadísticas del producto
    if (m.idproducto) {
      cargarEstadisticas(m.idproducto);
    }
  }

  // Renderizado inicial
  renderizarMovimientos();

  // Cargar movimiento desde historial si hay ID
  if (movimientoId) {
    // Buscar el movimiento en toda la lista
    const encontrado = movimientos.find(m => m.id_movimiento == movimientoId);
    
    if (encontrado) {
      // Calcular en qué página está el movimiento
      const idxCompleto = movimientos.indexOf(encontrado);
      const paginaDelMovimiento = Math.floor(idxCompleto / paginacion.porPagina) + 1;
      
      // Ir a esa página
      paginacion.actual = paginaDelMovimiento;
      renderizarMovimientos();
      
      // Esperar a que el DOM esté renderizado
      setTimeout(() => {
        const item = document.querySelector(`.timeline-item[data-idx="${idxCompleto}"]`);
        if (item) {
          selectItem(item);
          renderDetalle(idxCompleto);
          
          // Scroll suave al detalle
          document.getElementById('detalle-movimiento')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    } else {
      // No está en los últimos 7, cargar como pinned
      await cargarMovimientoPinned(movimientoId);
    }
  }

  // Exponer funciones globalmente
  window.removerPinned = removerPinned;
  window.cargarDetallesMovimiento = cargarMovimientoPinned;
  window.mostrarPanelDetalles = cargarMovimientoPinned;

  // --- Click y Drag & Drop ---
  contenedor.addEventListener("click", (e) => {
    // Manejar clic en pinned
    const pinnedItem = e.target.closest(".pinned-item");
    if (pinnedItem && pinnedMovimiento) {
      // Animación de entrada
      detalle.style.opacity = "0";
      detalle.style.transform = "translateX(10px)";
      seleccionarMovimiento(pinnedMovimiento, true);
      setTimeout(() => {
        detalle.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        detalle.style.opacity = "1";
        detalle.style.transform = "";
      }, 50);
      return;
    }

    // Manejar clic en timeline normal
    const item = e.target.closest(".timeline-item");
    if (!item) return;
    
    const idx = Number(item.dataset.index);
    const m = movimientos[idx]; // Usar índice directo del array completo
    
    if (m) {
      // Animación de entrada
      detalle.style.opacity = "0";
      detalle.style.transform = "translateX(10px)";
      
      selectItem(item);
      renderDetalle(idx);
      
      setTimeout(() => {
        detalle.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        detalle.style.opacity = "1";
        detalle.style.transform = "";
      }, 50);
    }
  });

  contenedor.addEventListener("dragstart", (e) => {
    const item = e.target.closest(".timeline-item");
    if (!item) return;
    const img = new Image();
    img.src =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAEklEQVR42mP8/5+hHgAHggJ/P6pHUgAAAABJRU5ErkJggg==";
    e.dataTransfer.setDragImage(img, 0, 0);
    e.dataTransfer.setData("text/plain", item.dataset.index);
    item.style.opacity = "0.6";
    item.style.transform = "scale(0.98)";
    item.style.transition = "all 0.2s ease";
  });

  contenedor.addEventListener("dragend", (e) => {
    const item = e.target.closest(".timeline-item");
    if (item) {
      item.style.opacity = "1";
      item.style.transform = "";
    }
  });

  detalle.addEventListener("dragover", (e) => {
    e.preventDefault();
    detalle.style.transform = "scale(1.01)";
    detalle.style.boxShadow = "0 0 0 2px rgba(59, 130, 246, 0.3)";
    detalle.style.transition = "all 0.2s ease";
  });
  detalle.addEventListener("dragleave", () => {
    detalle.style.transform = "";
    detalle.style.boxShadow = "";
  });
  detalle.addEventListener("drop", (e) => {
    e.preventDefault();
    detalle.style.transform = "";
    detalle.style.boxShadow = "";
    
    // Animación de entrada
    detalle.style.opacity = "0";
    detalle.style.transform = "translateX(10px)";
    
    const i = Number(e.dataTransfer.getData("text/plain"));
    const m = movimientos[i]; // Usar índice directo
    
    if (m) {
      const el = contenedor.querySelector(`.timeline-item[data-index="${i}"]`);
      if (el) selectItem(el);
      
      renderDetalle(i);
      
      setTimeout(() => {
        detalle.style.transition = "opacity 0.3s ease, transform 0.3s ease";
        detalle.style.opacity = "1";
        detalle.style.transform = "";
      }, 50);
    }
  });

  if (cerrarBtn) cerrarBtn.addEventListener("click", resetDetalle);

  // Variable para estado del panel de filtros
  let filtrosAbiertos = false;

  // --- Toggle de filtros ---
  if (btnToggleFilters && panelFiltros) {
    btnToggleFilters.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      console.log("Toggle filtros - Estado actual:", filtrosAbiertos);
      
      if (!filtrosAbiertos) {
        // Mostrar panel
        console.log("Abriendo panel de filtros");
        filtrosAbiertos = true;
        panelFiltros.classList.remove("hidden");
        // Force reflow
        void panelFiltros.offsetHeight;
        panelFiltros.style.maxHeight = "0px";
        panelFiltros.style.opacity = "0";
        
        requestAnimationFrame(() => {
          panelFiltros.style.maxHeight = "500px";
          panelFiltros.style.opacity = "1";
        });
      } else {
        // Ocultar panel
        console.log("Cerrando panel de filtros");
        filtrosAbiertos = false;
        panelFiltros.style.maxHeight = "0px";
        panelFiltros.style.opacity = "0";
        setTimeout(() => {
          panelFiltros.classList.add("hidden");
          panelFiltros.style.maxHeight = "";
        }, 300);
      }
    });
    
    // Prevenir que clicks dentro del panel lo cierren
    panelFiltros.addEventListener("click", (e) => {
      e.stopPropagation();
    });
  }

  // --- Limpiar filtros ---
  if (btnClearFilters) {
    btnClearFilters.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (fTipo) fTipo.value = "";
      if (fUser) fUser.value = "";
      if (fDateFrom) fDateFrom.value = "";
      if (fDateTo) fDateTo.value = "";
      applyFilters();
      mostrarToast("Filtros limpiados", "info");
    });
  }

  // --- Filtros dinámicos ---
  // Usar "change" para selects y "input" para inputs de texto/fecha
  if (fTipo) fTipo.addEventListener("change", applyFilters);
  if (fUser) fUser.addEventListener("change", applyFilters);
  if (fDateFrom) fDateFrom.addEventListener("change", applyFilters);
  if (fDateTo) fDateTo.addEventListener("change", applyFilters);
  
  function applyFilters() {
    const t = fTipo?.value || "";
    const u = (fUser?.value || "").trim().toLowerCase();
    const dateFrom = fDateFrom?.value || "";
    const dateTo = fDateTo?.value || "";

    console.log("Aplicando filtros:", { tipo: t, usuario: u, desde: dateFrom, hasta: dateTo });

    // Filtrar el array de movimientos
    let movimientosFiltrados = movimientos.filter((m) => {
      // Filtro por tipo
      if (t && m.tipo_evento !== t) return false;
      
      // Filtro por usuario
      if (u && !m.usuario_nombre.toLowerCase().includes(u)) return false;
      
      // Filtro por fecha
      if (dateFrom || dateTo) {
        // Extraer fecha del timestamp (formato: "2024-11-20 14:30")
        const fechaMovimiento = m.timestamp.split(" ")[0]; // "2024-11-20"
        
        if (dateFrom && fechaMovimiento < dateFrom) return false;
        if (dateTo && fechaMovimiento > dateTo) return false;
      }
      
      return true;
    });

    console.log("Movimientos filtrados:", movimientosFiltrados.length, "de", movimientos.length);

    // Guardar movimientos originales y reemplazar temporalmente
    const movimientosOriginales = movimientos;
    movimientos = movimientosFiltrados;
    
    // Reiniciar paginación
    paginacion.actual = 1;
    paginacion.total = movimientosFiltrados.length;
    
    // Renderizar con filtros aplicados
    renderizarMovimientos();
    
    // Restaurar movimientos originales
    movimientos = movimientosOriginales;
  }

  // --- Selección visual ---
  function selectItem(item) {
    contenedor.querySelectorAll(".timeline-item").forEach((el) => {
      el.classList.remove("item-activo", "ring-2", "ring-primary-400/50", "ring-primary-500/60", "selected");
    });

    item.classList.add(
      "item-activo",
      "ring-2",
      document.documentElement.classList.contains("dark")
        ? "ring-gray-500/60"
        : "ring-gray-500/60",
      "selected"
    );
  }


  // --- Render de detalle ---
  function renderDetalle(i) {
    const m = movimientos[i];
    if (!m) return;

    const tipo = {
      "Añadir": { icon: "south", color: "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/40" },
      "Retirar": { icon: "north", color: "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/40" },
      "Mover": { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" },
    }[m.tipo_evento] || { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" };

    const relacionados = movimientos.filter(x => x.producto === m.producto).slice(0, 5);

    detalle.className = "min-h-[46vh] flex flex-col bg-[var(--card-bg-light)] dark:bg-[var(--card-sub-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg overflow-hidden transition-all duration-300";

    detalle.innerHTML = `
      <!-- Header compacto -->
      <div class="relative ${tipo.color} border-b border-neutral-300 dark:border-[var(--border-dark)] p-3">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2.5 flex-1 min-w-0">
            <div class="w-9 h-9 flex items-center justify-center rounded-lg bg-white dark:bg-neutral-900 shadow-sm flex-shrink-0">
              <span class="material-symbols-outlined text-xl ${tipo.color.split(' ')[0]}">${tipo.icon}</span>
            </div>
            <div class="min-w-0 flex-1">
              <h2 class="text-sm font-bold text-[var(--text-light)] dark:text-white truncate">${m.producto}</h2>
            </div>
          </div>
          <div class="text-right flex-shrink-0">
            <p class="text-[10px] text-neutral-600 dark:text-neutral-400 flex items-center justify-end gap-1">
              <span class="material-symbols-outlined text-xs">schedule</span>
              ${new Date(m.timestamp).toLocaleString("es-ES", {dateStyle: 'short', timeStyle: 'short'})}
            </p>
          </div>
        </div>
      </div>

      <!-- Contenido compacto en grid 2 columnas -->
      <div class="p-3 overflow-auto">
        
        <!-- Resumen de peso compacto (ancho completo) -->
        <div class="grid grid-cols-3 gap-2 mb-3">
          <div class="p-2 rounded-lg border-2 ${tipo.color.includes('green') ? 'border-green-300 dark:border-green-800 bg-green-50 dark:bg-green-900/20' : tipo.color.includes('red') ? 'border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/20' : 'border-blue-300 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20'} text-center">
            <span class="material-symbols-outlined ${tipo.color.split(' ')[0]} text-lg">scale</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Peso Total</p>
            <p class="text-xl font-bold ${tipo.color.split(' ')[0]}">${(m.peso_total || 0).toFixed(2)}</p>
            <p class="text-[10px] text-neutral-500">kg</p>
          </div>
          <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] text-center">
            <span class="material-symbols-outlined text-primary-500 text-lg">inventory_2</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Cantidad</p>
            <p class="text-xl font-bold text-[var(--text-light)] dark:text-white">${m.cantidad}</p>
            <p class="text-[10px] text-neutral-500">unid.</p>
          </div>
          <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] text-center">
            <span class="material-symbols-outlined text-primary-500 text-lg">balance</span>
            <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mt-1">Peso/Unid.</p>
            <p class="text-xl font-bold text-[var(--text-light)] dark:text-white">${(m.peso_por_unidad || 0).toFixed(2)}</p>
            <p class="text-[10px] text-neutral-500">kg/u</p>
          </div>
        </div>

        <!-- Grid 2 columnas: Info + Historial -->
        <div class="grid grid-cols-2 gap-3">
          <!-- Columna izquierda: Información + Observación -->
          <div class="space-y-1.5">
            <h3 class="text-xs font-bold text-[var(--text-light)] dark:text-white flex items-center gap-1.5 mb-0.5">
              <span class="material-symbols-outlined text-base">info</span>
              Información
            </h3>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">location_on</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">Ubicación</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.ubicacion}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">person</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">Usuario</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.usuario_nombre}</p>
              </div>
            </div>
            <div class="flex items-center gap-2 p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)]">
              <span class="material-symbols-outlined text-primary-500 text-lg">badge</span>
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-medium text-neutral-500 dark:text-neutral-400">RUT</p>
                <p class="text-xs font-semibold text-[var(--text-light)] dark:text-white truncate">${m.rut_usuario || "—"}</p>
              </div>
            </div>
            
            ${m.observacion ? `
              <div class="p-2 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-neutral-50 dark:bg-[var(--card-bg-dark)]">
                <div class="flex items-start gap-2">
                  <span class="material-symbols-outlined text-warning-500 text-lg flex-shrink-0">notes</span>
                  <div class="flex-1 min-w-0">
                    <p class="text-[10px] font-medium text-neutral-600 dark:text-neutral-400 uppercase mb-1">Observación</p>
                    <p class="text-xs text-neutral-800 dark:text-neutral-200 break-words">${m.observacion}</p>
                  </div>
                </div>
              </div>
            ` : ''}
          </div>

          <!-- Columna derecha: Historial del producto -->
          <div class="space-y-1.5">
            <h3 class="text-xs font-bold text-[var(--text-light)] dark:text-white flex items-center gap-1.5 mb-0.5">
              <span class="material-symbols-outlined text-base">history</span>
              Historial de ${m.producto}
            </h3>
            ${relacionados.slice(0, 4).map(r => {
              const rColor = r.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-400" :
                             r.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-400" :
                             "text-blue-600 dark:text-blue-400";
              return `
                <div class="p-2 rounded-lg border border-neutral-200 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors duration-200">
                  <div class="flex items-center justify-between gap-2">
                    <div class="flex items-center gap-1.5">
                      <span class="material-symbols-outlined text-sm ${rColor}">${
                        r.tipo_evento === "Añadir" ? "south" :
                        r.tipo_evento === "Retirar" ? "north" : "sync_alt"
                      }</span>
                      <span class="text-xs text-neutral-700 dark:text-neutral-300">
                        <span class="font-semibold">${r.tipo_evento}</span>
                      </span>
                    </div>
                    <div class="text-right">
                      <p class="text-xs font-semibold ${rColor}">${(r.peso_total || 0).toFixed(2)}kg</p>
                      <p class="text-[10px] text-neutral-500">${String(r.timestamp).split(" ")[1]?.slice(0,5) || ""}</p>
                    </div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      </div>
    `;
    
    // Mostrar sección de estadísticas
    const statsSection = document.getElementById('stats-producto');
    if (statsSection) {
      statsSection.classList.remove('hidden');
    }
    
    // Cargar estadísticas del producto
    if (m.idproducto) {
      cargarEstadisticas(m.idproducto);
    }
  }

  function resetDetalle() {
    detalle.className = "min-h-[46vh] flex flex-col items-center justify-center border-2 border-dashed border-neutral-400/40 dark:border-[var(--border-dark)] rounded-lg text-center px-6 py-10";
    detalle.innerHTML = `
      <span class="material-symbols-outlined text-5xl text-neutral-400 dark:text-neutral-600">touch_app</span>
      <p class="mt-2 text-sm text-neutral-500">Selecciona o arrastra un movimiento para ver detalles</p>
      <p class="text-xs text-neutral-500">Historial, usuarios y observaciones aparecerán aquí</p>
    `;
    
    // Ocultar estadísticas
    const statsSection = document.getElementById('stats-producto');
    if (statsSection) {
      statsSection.classList.add('hidden');
    }
  }

  // --- Modal de Nuevo Movimiento ---
  const modal = document.getElementById("modal-new-mov");
  const btnNew = document.getElementById("btn-new-mov");
  const btnNewHeader = document.getElementById("btn-registrar-movimiento-header");
  const form = document.getElementById("form-new-mov");

  // Función para abrir el modal
  const abrirModal = () => {
    modal?.classList.remove("hidden");
    document.body.classList.add("modal-open"); // Bloquear scroll del body
    form?.reset();
    document.getElementById('peso-total-display').value = '0.00 kg';
    
    // Cargar productos y estantes
    cargarProductos();
    cargarEstantes();
    
    // Re-configurar event listeners para inputs cada vez que se abre el modal
    setTimeout(() => {
      const formActual = document.getElementById('form-new-mov');
      const inputCantidad = formActual?.querySelector('#input-cantidad');
      const inputPesoUnidad = formActual?.querySelector('#input-peso-unidad');
      const selectProductos = formActual?.querySelector('[name=idproducto]');
      
      if (inputCantidad) {
        inputCantidad.removeEventListener('input', calcularPesoTotal);
        inputCantidad.addEventListener('input', calcularPesoTotal);
      }
      if (inputPesoUnidad) {
        inputPesoUnidad.removeEventListener('input', calcularPesoTotal);
        inputPesoUnidad.addEventListener('input', calcularPesoTotal);
      }
      if (selectProductos) {
        selectProductos.removeEventListener('change', actualizarPesoYEstante);
        selectProductos.addEventListener('change', actualizarPesoYEstante);
      }
    }, 100);
  };

  // Abrir modal desde el botón original (si existe)
  btnNew?.addEventListener("click", abrirModal);
  
  // Abrir modal desde el botón del header (si existe)
  btnNewHeader?.addEventListener("click", abrirModal);

  // Función para calcular peso total automáticamente
  function calcularPesoTotal() {
    const formActual = document.getElementById('form-new-mov');
    const inputCantidad = formActual?.querySelector('#input-cantidad');
    const inputPesoUnidad = formActual?.querySelector('#input-peso-unidad');
    const pesoTotalDisplay = formActual?.querySelector('#peso-total-display');
    
    const cantidad = parseFloat(inputCantidad?.value) || 0;
    const pesoUnidad = parseFloat(inputPesoUnidad?.value) || 0;
    const pesoTotal = cantidad * pesoUnidad;
    
    if (pesoTotalDisplay) {
      pesoTotalDisplay.value = pesoTotal > 0 ? `${pesoTotal.toFixed(2)} kg` : '0.00 kg';
    }
  }

  // Los event listeners se configurarán cuando se abra el modal

  // Cerrar modal
  modal?.querySelectorAll(".close-modal").forEach(btn => {
    btn.addEventListener("click", () => {
      modal.classList.add("hidden");
      document.body.classList.remove("modal-open"); // Restaurar scroll del body
    });
  });

  // Evitar cierre al hacer click dentro del modal
  modal?.querySelector("div > div").addEventListener("click", e => e.stopPropagation());

  // Cerrar al hacer click fuera
  modal?.addEventListener("click", e => {
    if (e.target === modal) modal.classList.add("hidden");
  });

  // Variable para almacenar productos y estantes globalmente
  let productosCache = [];
  let estantesCache = [];
  
  // Función para cargar estantes
  async function cargarEstantes() {
    console.log("🏢 Cargando estantes...");
    try {
      const response = await fetch('/api/estantes');
      if (!response.ok) throw new Error('Error al cargar estantes');
      
      estantesCache = await response.json();
      const formActual = document.getElementById("form-new-mov");
      const selectEstante = formActual?.querySelector('[name="id_estante"]');
      
      if (!selectEstante) {
        console.error("❌ No se encontró el select de estantes");
        return;
      }

      if (estantesCache && estantesCache.length > 0) {
        selectEstante.innerHTML = '<option value="">Seleccione un estante</option>' + 
          estantesCache.map(e => {
            return `<option value="${e.id_estante}">${e.nombre || 'Estante ' + e.id_estante}</option>`;
          }).join("");
        console.log(`✅ ${estantesCache.length} estantes agregados al select`);
      } else {
        selectEstante.innerHTML = '<option value="">No hay estantes disponibles</option>';
        console.warn("⚠️ No hay estantes en la base de datos");
      }
    } catch (error) {
      console.error('❌ Error cargando estantes:', error);
      mostrarToast('Error al cargar estantes', 'error');
    }
  }
  
  // Función para cargar productos
  function cargarProductos() {
    console.log("📦 Cargando productos...");
    fetch("/api/productos")
      .then(r => {
        console.log("📡 Respuesta recibida:", r.status);
        return r.json();
      })
      .then(productos => {
        console.log("✅ Productos cargados:", productos);
        productosCache = productos; // Guardar en cache
        
        // Buscar el form dinámicamente (puede haber sido clonado)
        const formActual = document.getElementById("form-new-mov");
        const selectProductos = formActual?.querySelector("[name=idproducto]");
        if (!selectProductos) {
          console.error("❌ No se encontró el select de productos");
          return;
        }

        if (productos && productos.length > 0) {
          selectProductos.innerHTML = productos.map(p => {
            // CONVERSIÓN: El peso viene en GRAMOS desde la BD, convertir a KG
            const pesoEnGramos = p.peso || 0;
            const pesoEnKg = pesoEnGramos / 1000;
            
            return `<option value="${p.idproducto}" data-peso="${pesoEnKg}" data-estante="${p.id_estante || ''}">${p.nombre} (Stock: ${p.stock || 0} unidades, ${pesoEnKg.toFixed(3)} kg/u)</option>`;
          }).join("");
          console.log(`✅ ${productos.length} productos agregados al select`);
          
          // Auto-llenar peso y estante del primer producto inmediatamente
          actualizarPesoYEstante();
        } else {
          selectProductos.innerHTML = '<option value="">No hay productos disponibles</option>';
          console.warn("⚠️ No hay productos en la base de datos");
        }
      })
      .catch(error => {
        if (window.errorLogger) {
          window.errorLogger.error('Error cargando productos', 'movimiento_inventario', '', error);
        }
        console.error("❌ Error cargando productos:", error);
        mostrarError("Error al cargar los productos");
      });
  }
  
  // Función para actualizar peso y estante cuando cambia el producto
  function actualizarPesoYEstante() {
    const formActual = document.getElementById("form-new-mov");
    const selectProductos = formActual?.querySelector("[name=idproducto]");
    const inputPesoUnidad = formActual?.querySelector('#input-peso-unidad');
    const inputEstante = formActual?.querySelector('[name="id_estante"]');
    
    if (!selectProductos || !inputPesoUnidad) return;
    
    const selectedOption = selectProductos.options[selectProductos.selectedIndex];
    const pesoEnKg = parseFloat(selectedOption.dataset.peso) || 0;
    const idEstante = selectedOption.dataset.estante || '';
    
    // Actualizar peso
    inputPesoUnidad.value = pesoEnKg.toFixed(3);
    calcularPesoTotal();
    
    // Actualizar estante (buscar el nombre del estante si existe)
    if (inputEstante && idEstante) {
      const estante = estantesCache.find(e => e.id_estante == idEstante);
      const nombreEstante = estante ? estante.nombre : `Estante ${idEstante}`;
      inputEstante.value = nombreEstante;
      // Guardar el id_estante en un campo oculto
      let hiddenEstante = formActual.querySelector('[name="id_estante_hidden"]');
      if (!hiddenEstante) {
        hiddenEstante = document.createElement('input');
        hiddenEstante.type = 'hidden';
        hiddenEstante.name = 'id_estante_hidden';
        formActual.appendChild(hiddenEstante);
      }
      hiddenEstante.value = idEstante;
    }
    
    console.log(`🏷️ Producto actualizado: ${pesoEnKg} kg, Estante: ${idEstante}`);
  }
  
  // Mantener la función anterior para compatibilidad
  function actualizarPesoProducto() {
    actualizarPesoYEstante();
  }
  
  // Los listeners de producto y tipo de evento se configuran en cargarProductos()

  // Variable para prevenir envíos duplicados (global al script)
  let isSubmitting = false;
  let lastSubmitTime = 0;

  // Función de manejo de submit del formulario
  async function handleFormSubmit(e) {
    e.preventDefault();
    e.stopImmediatePropagation(); // Prevenir propagación INMEDIATA del evento
    
    const now = Date.now();
    
    // Prevenir envíos duplicados - verificar tiempo entre envíos (mínimo 1 segundo)
    if (isSubmitting || (now - lastSubmitTime) < 1000) {
      console.log("⚠️ Envío ya en proceso o muy rápido, ignorando duplicado");
      return false;
    }

    // Marcar como en proceso
    isSubmitting = true;
    lastSubmitTime = now;

    try {
      // Buscar el formulario dinámicamente (puede haber sido clonado)
      const formActual = document.getElementById("form-new-mov");
      if (!formActual) {
        console.error("❌ Formulario no encontrado");
        isSubmitting = false;
        return;
      }
      
      const formData = new FormData(formActual);
      const datos = {};

      // Convertir y validar campos
      datos.tipo_evento = formData.get("tipo_evento");
      datos.idproducto = parseInt(formData.get("idproducto"));
      datos.cantidad = parseInt(formData.get("cantidad"));
      datos.peso_por_unidad = parseFloat(formData.get("peso_por_unidad"));
      datos.peso_total = datos.cantidad * datos.peso_por_unidad;
      datos.observacion = formData.get("observacion") || "";
      datos.timestamp = new Date().toISOString(); // Agregar timestamp actual
      // Obtener el id_estante del campo oculto
      const idEstanteHidden = formData.get("id_estante_hidden");
      datos.id_estante = parseInt(idEstanteHidden || formData.get("id_estante"));

      // Debug: mostrar valores capturados
      console.log("📋 Valores del formulario:", {
        tipo_evento: formData.get("tipo_evento"),
        idproducto: formData.get("idproducto"),
        cantidad: formData.get("cantidad"),
        peso_por_unidad: formData.get("peso_por_unidad"),
        id_estante: formData.get("id_estante"),
        id_estante_hidden: formData.get("id_estante_hidden")
      });
      console.log("🔢 Valores convertidos:", datos);

      // Validar campos numéricos
      if (isNaN(datos.idproducto) || isNaN(datos.cantidad) || isNaN(datos.peso_por_unidad) || isNaN(datos.id_estante)) {
        console.error("❌ Validación fallida:", {
          idproducto: datos.idproducto,
          cantidad: datos.cantidad,
          peso_por_unidad: datos.peso_por_unidad,
          id_estante: datos.id_estante
        });
        mostrarError("Todos los campos son requeridos. Por favor, verifica que hayas seleccionado un estante.");
        isSubmitting = false;
        return;
      }

      if (datos.cantidad <= 0) {
        mostrarError("La cantidad debe ser mayor a 0");
        isSubmitting = false;
        return;
      }

      if (datos.peso_por_unidad <= 0) {
        mostrarError("El peso por unidad debe ser mayor a 0");
        isSubmitting = false;
        return;
      }

      if (!datos.id_estante || datos.id_estante <= 0) {
        mostrarError("Debe seleccionar un estante válido");
        isSubmitting = false;
        return;
      }

      console.log("📤 Enviando movimiento:", datos);

      // Obtener CSRF token
      const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

      const response = await fetch("/api/movimientos/nuevo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken })
        },
        body: JSON.stringify(datos)
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || "Error al guardar el movimiento");
      }

      // Éxito
      console.log("✅ Movimiento guardado exitosamente");
      mostrarExito(result.mensaje || "Movimiento registrado correctamente");
      
      // NO resetear isSubmitting para prevenir múltiples envíos antes de recargar
      
      // Cerrar modal y resetear formulario
      if (modal) modal.classList.add("hidden");
      
      // Recargar página después de un breve delay
      setTimeout(() => {
        window.location.reload();
      }, 1000);

    } catch (error) {
      if (window.errorLogger) {
        window.errorLogger.critical('Error al guardar movimiento', 'movimiento_inventario', error.message, error);
      }
      console.error("❌ Error:", error);
      mostrarError(error.message);
      
      // Solo resetear la bandera en caso de error para permitir reintento
      isSubmitting = false;
      lastSubmitTime = 0;
    }
  }

  // Remover todos los listeners previos del formulario (si existen)
  if (form) {
    // Clonar el formulario para eliminar todos los event listeners
    const nuevoForm = form.cloneNode(true);
    form.parentNode.replaceChild(nuevoForm, form);
    
    // Agregar el listener al nuevo formulario
    nuevoForm.addEventListener("submit", handleFormSubmit, { once: false });
    console.log("✅ Listener de formulario agregado (sin duplicados)");
    
    // Actualizar referencias
    const btnGuardar = nuevoForm.querySelector('button[type="submit"]');
    if (btnGuardar) {
      // Deshabilitar botón al hacer submit para evitar doble clic
      nuevoForm.addEventListener("submit", function() {
        btnGuardar.disabled = true;
        btnGuardar.textContent = "Guardando...";
        setTimeout(() => {
          btnGuardar.disabled = false;
          btnGuardar.textContent = "Guardar";
        }, 2000);
      }, { once: true });
    }
  }

  // Funciones de notificación
  function mostrarError(mensaje) {
    // Crear notificación toast
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 z-50 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fadeIn';
    toast.innerHTML = `
      <span class="material-symbols-outlined">error</span>
      <span>${mensaje}</span>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  function mostrarExito(mensaje) {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 z-50 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-fadeIn';
    toast.innerHTML = `
      <span class="material-symbols-outlined">check_circle</span>
      <span>${mensaje}</span>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  // Función para cargar estadísticas del producto
  async function cargarEstadisticas(idproducto) {
    try {
      const response = await fetch(`/api/movimientos/estadisticas/${idproducto}`);
      const data = await response.json();

      if (data.success) {
        // Actualizar las estadísticas en la sección correspondiente
        actualizarEstadisticasUI(data);
      }
    } catch (error) {
      console.error("Error cargando estadísticas:", error);
    }
  }

  function actualizarEstadisticasUI(stats) {
    const statsSection = document.getElementById('stats-container');
    if (!statsSection) return;

    statsSection.innerHTML = `
      <div class="p-3 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] text-center animate-fadeIn">
        <p class="text-xs text-neutral-500 dark:text-neutral-400">Entradas</p>
        <p class="text-lg font-bold text-green-500">+${stats.entradas} unidades</p>
      </div>
      <div class="p-3 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] text-center animate-fadeIn" style="animation-delay: 50ms">
        <p class="text-xs text-neutral-500 dark:text-neutral-400">Retiros</p>
        <p class="text-lg font-bold text-red-500">−${stats.retiros} unidades</p>
      </div>
      <div class="p-3 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] text-center animate-fadeIn" style="animation-delay: 100ms">
        <p class="text-xs text-neutral-500 dark:text-neutral-400">Stock Actual</p>
        <p class="text-lg font-bold text-blue-500">${stats.stock_actual} unidades</p>
      </div>
      <div class="p-3 rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] text-center animate-fadeIn" style="animation-delay: 150ms">
        <p class="text-xs text-neutral-500 dark:text-neutral-400">Último Movimiento</p>
        <p class="text-sm font-semibold text-[var(--text-light)] dark:text-[var(--text-dark)]">${stats.ultimo_movimiento}</p>
      </div>
    `;
  }

  // Hook vacío para integración futura con hardware
  function procesarEventoHardware(peso) {
    // TODO: Integración con sensor de peso
    // Esta función se llamará cuando el hardware detecte un cambio de peso
    console.log("Evento de hardware detectado:", peso);
    
    // Ejemplo de uso futuro:
    // const cantidadDetectada = calcularCantidadDesdePeso(peso);
    // autocompletarFormulario(cantidadDetectada);
  }

  // Exponer funciones para uso futuro
  window.procesarEventoHardware = procesarEventoHardware;
  window.mostrarToast = mostrarToast;

  // Agregar estilos de animación
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateY(-20px); opacity: 0; }
      to { transform: translateY(0); opacity: 1; }
    }
    @keyframes slideInRight {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
      from { transform: translateX(0); opacity: 1; }
      to { transform: translateX(100%); opacity: 0; }
    }
    .animate-slideIn {
      animation: slideIn 0.3s ease-out;
    }
    .animate-slideInRight {
      animation: slideInRight 0.3s ease-out;
    }
  `;
  document.head.appendChild(style);

  // --- Estado inicial ---
  resetDetalle();
  // No llamar applyFilters() al inicio para evitar interferencias
});
