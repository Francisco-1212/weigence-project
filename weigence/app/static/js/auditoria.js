window.addEventListener("load", () => {
  const darkMode = document.documentElement.classList.contains('dark');
  const textColor = darkMode ? '#ddd' : '#222';
  const gridColor = darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)';

  // Gráfico 1 - Donut
  new Chart(document.getElementById("chartEventos"), {
    type: "doughnut",
    data: {
      labels: ["Accesos", "Pesos", "Fallas"],
      datasets: [{
        data: [40, 35, 25],
        backgroundColor: ["#3b82f6", "#f59e0b", "#ef4444"],
        borderWidth: 0
      }]
    },
    options: {
      plugins: { legend: { labels: { color: textColor } } },
      cutout: "65%"
    }
  });

  // Gráfico 2 - Barras
  new Chart(document.getElementById("chartIncidencias"), {
    type: "bar",
    data: {
      labels: ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"],
      datasets: [{
        label: "Incidencias",
        data: [2,3,1,4,2,3,5],
        backgroundColor: "rgba(59,130,246,0.5)",
        borderRadius: 6
      }]
    },
    options: {
      scales: {
        x: { grid: { display:false }, ticks:{ color:textColor } },
        y: { grid:{ color:gridColor }, ticks:{ color:textColor } }
      },
      plugins: { legend: { display: false } }
    }
  });

  // Gráfico 3 - Línea (actividad 24h)
  new Chart(document.getElementById("chartActividad"), {
    type: "line",
    data: {
      labels: Array.from({length:24},(_,i)=>i+":00"),
      datasets: [{
        label: "Eventos por hora",
        data: [2,3,1,2,3,4,6,8,9,7,5,4,3,6,8,9,5,4,2,2,1,1,2,3],
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59,130,246,0.2)",
        fill: true,
        tension: 0.3,
        pointRadius: 0
      }]
    },
    options: {
      scales: {
        x: { grid:{ display:false }, ticks:{ color:textColor } },
        y: { grid:{ color:gridColor }, ticks:{ color:textColor } }
      },
      plugins: { legend:{ display:false } }
    }
  });
});
setTimeout(() => {
  Chart.helpers.each(Chart.instances, function(instance) {
    instance.resize();
  });
}, 200);
