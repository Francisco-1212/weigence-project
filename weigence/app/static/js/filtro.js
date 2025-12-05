// DOM references will be acquired when the DOM is ready
let filtros = [];
let mesNavegador = null;
let mesLabel = null;
let btnMesBack = null;
let btnMesNext = null;
let chartContainer = null;
let chartLabels = null;

function aplicarEstiloActivo(boton) {
  filtros.forEach(btn => btn.classList.remove('filtro-activo'));
  if (boton) boton.classList.add('filtro-activo');
}

async function fetchDatosFiltrados(rango, boton, mes = null, year = null) {
  try {
    let url = `/api/dashboard_filtrado?rango=${rango}`;
    if (rango === 'mes' && mes !== null && year !== null) url += `&mes=${mes+1}&year=${year}`;
    const res = await fetch(url);
    // Read response as text first to detect HTML redirect/login pages
    const ct = res.headers.get('content-type') || '';
    const txt = await res.text();
    if (!ct.includes('application/json')) {
      // Likely the request was redirected to the login page (no session)
      console.error('fetchDatosFiltrados: respuesta no JSON del servidor. Posible redirección a login. Response snippet:\n', txt.slice(0,1000));
      throw new Error('La API no devolvió JSON (posible redirección a login).');
    }
    const data = JSON.parse(txt);

    // Actualizar KPIs principales
    const fmt = new Intl.NumberFormat('es-CL');
    const elArt = document.getElementById('articulosVendidos');
    const elProd = document.getElementById('productoMasVendido');
    const elVent = document.getElementById('ventasTotales');
    if (elArt) elArt.textContent = data.articulos_vendidos ?? 0;
    if (elProd) elProd.textContent = data.producto_mas_vendido ?? 'Sin datos';
    if (elVent) elVent.textContent = `$${fmt.format(data.ventas_totales ?? 0)}`;

    // Actualizar gráfico principal / totales
    const totalSalesEl = document.getElementById('totalSales');
    const growthEl = document.getElementById('growthPercentage');
    if (totalSalesEl) totalSalesEl.textContent = `$${fmt.format(data.ventas_totales ?? 0)}`;
    if (growthEl) {
      growthEl.textContent = `${data.ventas_cambio ?? 0}%`;
      growthEl.className = `text-sm font-medium ${ (data.ventas_cambio ?? 0) >= 0 ? 'text-green-500' : 'text-red-500'}`;
    }

    // Gráfico según filtro — usamos el renderizador DOM unificado
    if (rango === "hoy" || rango === "semana" || rango === "mes") {
      // For 'mes' we expect caller to provide mes/year; if not provided, default to previous calendar month
      if (rango === 'mes' && (mes === null || year === null)) {
        const now = new Date();
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        mes = lastMonth.getMonth();
        year = lastMonth.getFullYear();
        // Re-fetch with explicit month/year so backend gets correct range
        fetchDatosFiltrados('mes', boton, mes, year);
        return; // wait for the re-fetched response
      }
      renderBarsFromGrafico(data.grafico);
    }
    // En la función fetchDatosFiltrados, después de obtener los datos:
    console.log('Datos recibidos del backend:', data);
    console.log('Datos del gráfico:', data.grafico);

    aplicarEstiloActivo(boton);
    

    // Render Top/Low lists
    renderTopLowLists(data.productos_top || [], data.productos_low || []);
  } catch (error) {
    // Solo registrar errores que NO sean de red transitoria
    const isNetworkError = error.message === 'Failed to fetch' || 
                          error.message.includes('NetworkError') ||
                          error.message.includes('timeout');
    
    if (!isNetworkError && window.errorLogger) {
      window.errorLogger.error('Error al obtener datos filtrados', 'dashboard', String(error), error);
    }
    
    console.error('Error al cargar datos del dashboard:', error);
  }
}

// Attach event listeners for filter buttons and month navigator (if present)
filtros.forEach(boton => {
  boton.addEventListener('click', () => {
    if (boton.dataset.rango === "mes") {
      // Compute previous month automatically
      const now = new Date();
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const mesIndex = lastMonth.getMonth();
      const anio = lastMonth.getFullYear();
      fetchDatosFiltrados('mes', boton, mesIndex, anio);
    } else {
      fetchDatosFiltrados(boton.dataset.rango, boton);
    }
  });
});

// Month navigator removed: month is auto-detected as previous calendar month.

// Inicializa en "Hoy" cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Acquire DOM references
  filtros = Array.from(document.querySelectorAll('.filtro-fecha-btn')) || [];
  mesNavegador = document.getElementById('mes-navegador');
  mesLabel = document.getElementById('mes-label');
  btnMesBack = document.getElementById('btn-mes-back');
  btnMesNext = document.getElementById('btn-mes-next');
  chartContainer = document.getElementById('chartContainer');
  chartLabels = document.getElementById('chartLabels');

  // Hide month navigator UI and disable month navigation — we auto-detect the previous month
  if (mesNavegador) mesNavegador.classList.add('hidden');

  // Attach event listeners for filter buttons
  filtros.forEach(boton => {
    boton.addEventListener('click', () => {
      if (boton.dataset.rango === "mes") {
        // Compute previous month automatically
        const now = new Date();
        const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        const mesIndex = lastMonth.getMonth();
        const anio = lastMonth.getFullYear();
        fetchDatosFiltrados('mes', boton, mesIndex, anio);
      } else {
        fetchDatosFiltrados(boton.dataset.rango, boton);
      }
    });
  });

  // Inicializa en "Hoy" si hay filtros
  if (filtros.length > 0) {
    aplicarEstiloActivo(filtros[0]);
    fetchDatosFiltrados('hoy', filtros[0]);
  }
});

// Render barras tipo producto (hoy)
function renderBarsFromGrafico(grafico) {
  console.log('Renderizando gráfico con datos:', grafico);
  
  const chartContainer = document.getElementById('chartContainer');
  const chartLabels = document.getElementById('chartLabels');
  
  if (!chartContainer || !chartLabels) {
    console.error('Elementos del gráfico no encontrados en el DOM');
    return;
  }

  // Limpiar contenedores
  chartContainer.innerHTML = '';
  chartLabels.innerHTML = '';
  
  if (!grafico) {
    chartContainer.innerHTML = '<div class="text-center text-gray-400">Sin datos del gráfico</div>';
    return;
  }

  let items = [];
  
  // Manejar diferentes estructuras de datos
  if (grafico.productos && Array.isArray(grafico.productos)) {
    console.log('Usando estructura productos:', grafico.productos);
    items = grafico.productos.map(p => ({ 
      nombre: p.nombre || 'Sin nombre', 
      ventas: p.ventas || 0 
    }));
  } else if (grafico.labels && grafico.data) {
    console.log('Usando estructura labels/data:', grafico.labels, grafico.data);
    items = grafico.labels.map((lbl, i) => ({ 
      nombre: lbl || 'Sin nombre', 
      ventas: grafico.data[i] || 0 
    }));
  } else {
    console.warn('Estructura de gráfico no reconocida:', grafico);
    chartContainer.innerHTML = '<div class="text-center text-gray-400">Estructura de datos no válida</div>';
    return;
  }

  console.log('Items procesados:', items);

  if (!items.length) {
    chartContainer.innerHTML = '<div class="text-center text-gray-400">No hay datos para mostrar</div>';
    return;
  }

  const maxVentas = Math.max(...items.map(i => i.ventas || 0));
  console.log('Máximo de ventas:', maxVentas);

  items.forEach((it, index) => {
    const ventasValor = it.ventas || 0;
    let altura = maxVentas > 0 ? (ventasValor / maxVentas) * 100 : 0;

    // Asegurar altura mínima para visibilidad
    // Si ventas === 0, mostrar barra más grande para visibilidad (20%)
    if (ventasValor === 0) {
      altura = 4;
    } else {
      // Para valores pequeños pero mayores que cero, dar un mínimo pequeño (5%)
      if (altura <= 0) altura = 5;
    }
    
    console.log(`Producto ${index}: ${it.nombre}, Ventas: ${ventasValor}, Altura: ${altura}%`);

    const barraWrap = document.createElement('div');
    barraWrap.className = 'flex flex-col items-center justify-end w-full h-full';

    const barra = document.createElement('div');
    barra.className = `w-3/4 bg-blue-600 rounded-t-lg transition-all duration-500 hover:bg-blue-700 cursor-pointer min-h-[2px]`;
    barra.style.height = `${altura}%`;
    barra.title = `${it.nombre}: $${ventasValor}`;

    const label = document.createElement('div');
    label.textContent = it.nombre;
    label.className = 'text-center text-xs font-medium mt-1 truncate w-full px-1';

    barraWrap.appendChild(barra);
    chartContainer.appendChild(barraWrap);
    chartLabels.appendChild(label);
  });
  
  console.log('Gráfico renderizado correctamente');
}
function nombreMes(mes) {
  return ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][mes];
}

// Render Top/Low lists into templates in index.html
function renderTopLowLists(top, low) {
  const fmt = new Intl.NumberFormat('es-CL');
  const topContainer = document.querySelector('#top-ventas-list');
  const lowContainer = document.querySelector('#low-ventas-list');
  if (topContainer) {
    topContainer.innerHTML = '';
    top.forEach(p => {
      const div = document.createElement('div');
      div.className = 'grid grid-cols-3 text-sm';
      div.innerHTML = `
        <div class="p-4 font-medium text-neutral-900 dark:text-neutral-200">${p.nombre}</div>
        <div class="p-4 text-neutral-600 dark:text-neutral-400">${fmt.format(p.cantidad)}</div>
        <div class="p-4"><span class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400">${p.cantidad > 10 ? 'Alta' : 'Media'}</span></div>
      `;
      topContainer.appendChild(div);
    });
  }
  if (lowContainer) {
    lowContainer.innerHTML = '';
    low.forEach(p => {
      const div = document.createElement('div');
      div.className = 'grid grid-cols-3 text-sm';
      div.innerHTML = `
        <div class="p-4 font-medium text-neutral-900 dark:text-neutral-200">${p.nombre}</div>
        <div class="p-4 text-neutral-600 dark:text-neutral-400">${fmt.format(p.cantidad)}</div>
        <div class="p-4"><span class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400">${p.cantidad <= 2 ? 'Muy Baja' : 'Baja'}</span></div>
      `;
      lowContainer.appendChild(div);
    });
  }
}

// Expose the renderer globally so other legacy scripts can delegate to it without duplicating logic
try { window.renderBarsFromGrafico = renderBarsFromGrafico; } catch (e) { /* ignore in strict CSP contexts */ }

