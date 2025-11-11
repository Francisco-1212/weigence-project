// Inicializa el contexto de la IA para el dashboard
document.addEventListener('DOMContentLoaded', () => {
  // Obtener todas las tarjetas IA del dashboard
  const dashboardCards = document.querySelectorAll('[data-ia-card]');
  
  // Función para obtener datos de gráficos
  const getChartData = () => {
    const charts = document.querySelectorAll('[data-chart]');
    return Array.from(charts).reduce((data, chart) => {
      const chartId = chart.id;
      const chartInstance = Chart.getChart(chartId);
      if (chartInstance) {
        data[chartId] = {
          datasets: chartInstance.data.datasets.map(ds => ({
            data: ds.data,
            label: ds.label
          }))
        };
      }
      return data;
    }, {});
  };

  // Función para obtener datos de KPIs
  const getKPIData = () => {
    const kpis = document.querySelectorAll('[data-kpi]');
    return Array.from(kpis).reduce((data, kpi) => {
      const kpiId = kpi.dataset.kpi;
      data[kpiId] = {
        value: kpi.dataset.value,
        trend: kpi.dataset.trend
      };
      return data;
    }, {});
  };

  // Función para actualizar contexto
  const updateDashboardContext = () => {
    const contextData = {
      charts: getChartData(),
      kpis: getKPIData()
    };

    // Actualizar cada tarjeta con el nuevo contexto
    dashboardCards.forEach(card => {
      const iaCard = card.__iaCard;
      if (iaCard && iaCard.updateData) {
        iaCard.updateData(contextData);
      }
    });
  };

  // Actualizar contexto inicialmente y cada minuto
  updateDashboardContext();
  setInterval(updateDashboardContext, 60000);
});