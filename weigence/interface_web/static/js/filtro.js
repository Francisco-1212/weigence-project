document.addEventListener('DOMContentLoaded', () => {
  const filtros = document.querySelectorAll('.filtro-fecha-btn');
  function aplicarEstiloActivo(boton) {
    filtros.forEach(btn => btn.classList.remove('filtro-activo'));
    boton.classList.add('filtro-activo');
  }
  async function fetchDatosFiltrados(rango, boton) {
    try {
      const res = await fetch(`/api/dashboard_filtrado?rango=${rango}`);
      if (!res.ok) throw new Error('Error consultando datos');
      const data = await res.json();
      actualizarGrafico(data);
      aplicarEstiloActivo(boton);
    } catch (error) {
      alert('Error al obtener datos filtrados');
    }
  }
  filtros.forEach(boton => {
    boton.addEventListener('click', () => {
      fetchDatosFiltrados(boton.dataset.rango, boton);
    });
  });
  if (filtros.length > 0) {
    aplicarEstiloActivo(filtros[0]);
    fetchDatosFiltrados(filtros[0].dataset.rango, filtros[0]);
  }
});


// Render barras tipo producto (hoy)
function renderBarrasHoy(datos) {
  // Limpia otros gráficos
  canvas.style.display = 'none';
  chartContainer.innerHTML = '';
  chartLabels.innerHTML = '';
  chartContainer.style.display = '';
  chartLabels.style.display = '';
  if (!datos.grafico || !datos.grafico.productos) {
    chartContainer.innerHTML = '<div class="text-center text-gray-400">Sin datos hoy</div>';
    return;
  }
  const productos = datos.grafico.productos;
  const maxVentas = Math.max(...productos.map(p => p.ventas));
  productos.forEach(p => {
    const altura = maxVentas > 0 ? (p.ventas / maxVentas) * 100 : 10;
    const barra = document.createElement('div');
    barra.className = `w-full bg-blue-500/40 rounded-t-lg transition-all duration-500 hover:bg-blue-500 cursor-pointer`;
    barra.style.height = `${altura}%`;
    barra.title = `${p.nombre}: $${p.ventas.toFixed(0)}`;
    chartContainer.appendChild(barra);
    const label = document.createElement('div');
    label.textContent = p.nombre;
    label.className = 'text-center text-sm font-medium mt-1 truncate';
    chartLabels.appendChild(label);
  });
}
// Render base Chart.js (semana/mes)
function renderChartJs(labels, data) {
  chartContainer.style.display = 'none';
  chartLabels.style.display = 'none';
  canvas.style.display = '';
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(canvas.getContext('2d'), {
    type: 'bar',
    data: { labels, datasets: [{
      label: 'Ventas',
      data,
      backgroundColor: '#2563eb',
      borderRadius: 5,
    }]},
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false }, ticks: { color: '#a3a3a3', font: { weight: 'bold' } } },
        y: { grid: { color: '#222' }, ticks: { color: '#a3a3a3', precision: 0 } }
      }
    }
  });
}
async function fetchDatosFiltrados(rango, boton, mes = null, year = null) {
  try {
    let url = `/api/dashboard_filtrado?rango=${rango}`;
    if (rango === "mes" && mes !== null && year !== null)
      url += `&mes=${mes+1}&year=${year}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Error consultando datos');
    const data = await res.json();
    document.getElementById('totalSales').textContent = `$${data.ventas_totales ?? 0}`;
    document.getElementById('growthPercentage').textContent = `${data.ventas_cambio ?? 0}%`;
    document.getElementById('growthPercentage').className =
      `text-sm font-medium ${data.ventas_cambio >= 0 ? 'text-green-500' : 'text-red-500'}`;
    // Gráfico según filtro
    if (rango === "hoy") {
      mesNavegador.classList.add('hidden');
      renderBarrasHoy(data);
    } else if (rango === "semana") {
      mesNavegador.classList.add('hidden');
      renderChartJs(data.grafico.labels, data.grafico.data);
    } else if (rango === "mes") {
      mesNavegador.classList.remove('hidden');
      mesLabel.textContent = `${nombreMes(mes ?? mesActual)} ${year ?? yearActual}`;
      renderChartJs(data.grafico.labels, data.grafico.data);
    }
    aplicarEstiloActivo(boton);
  } catch (error) {
    alert('Error al obtener datos filtrados');
    console.error(error);
  }
}
function nombreMes(mes) {
  return ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"][mes];
}
filtros.forEach(boton => {
  boton.addEventListener('click', () => {
    if(boton.dataset.rango === "mes") {
      mesNavegador.classList.remove('hidden');
      fetchDatosFiltrados("mes", boton, mesActual, yearActual);
    } else {
      mesNavegador.classList.add('hidden');
      fetchDatosFiltrados(boton.dataset.rango, boton);
    }
  });
});
btnMesBack.addEventListener('click', () => {
  if (mesActual === 0) { mesActual = 11; yearActual--; }
  else mesActual--;
  const botonMes = document.querySelector('[data-rango="mes"]');
  fetchDatosFiltrados('mes', botonMes, mesActual, yearActual);
});
btnMesNext.addEventListener('click', () => {
  if (mesActual === 11) { mesActual = 0; yearActual++; }
  else mesActual++;
  const botonMes = document.querySelector('[data-rango="mes"]');
  fetchDatosFiltrados('mes', botonMes, mesActual, yearActual);
});
// Inicializa en "Hoy"
if (filtros.length > 0) {
  aplicarEstiloActivo(filtros[0]);
  fetchDatosFiltrados('hoy', filtros[0]);
}
  
