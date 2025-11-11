// Inicializa el contexto de la IA para la página de ventas
document.addEventListener('DOMContentLoaded', () => {
  // Obtener todas las tarjetas IA de ventas
  const salesCards = document.querySelectorAll('[data-ia-card]');
  
  // Función para obtener datos de ventas
  const getSalesData = () => {
    const salesRows = document.querySelectorAll('[data-sale]');
    return Array.from(salesRows).map(sale => ({
      id: sale.dataset.sale,
      total: Number(sale.dataset.total),
      items: Number(sale.dataset.items),
      timestamp: sale.dataset.timestamp,
      status: sale.dataset.status
    }));
  };

  // Función para obtener datos de productos más vendidos
  const getTopProducts = () => {
    const products = document.querySelectorAll('[data-top-product]');
    return Array.from(products).map(product => ({
      id: product.dataset.productId,
      name: product.dataset.name,
      quantity: Number(product.dataset.quantity),
      revenue: Number(product.dataset.revenue),
      trend: product.dataset.trend
    }));
  };

  // Función para obtener métricas de ventas
  const getSalesMetrics = () => {
    const metrics = document.querySelectorAll('[data-sales-metric]');
    return Array.from(metrics).reduce((data, metric) => {
      const metricId = metric.dataset.metricId;
      data[metricId] = {
        value: Number(metric.dataset.value),
        previousValue: Number(metric.dataset.previousValue),
        trend: metric.dataset.trend,
        unit: metric.dataset.unit
      };
      return data;
    }, {});
  };

  // Función para obtener datos de gráficos
  const getChartData = () => {
    const charts = document.querySelectorAll('[data-sales-chart]');
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

  // Función para actualizar contexto
  const updateSalesContext = () => {
    const contextData = {
      sales: getSalesData(),
      topProducts: getTopProducts(),
      metrics: getSalesMetrics(),
      charts: getChartData(),
      timestamp: new Date().toISOString()
    };

    // Actualizar cada tarjeta con el nuevo contexto
    salesCards.forEach(card => {
      const iaCard = card.__iaCard;
      if (iaCard && iaCard.updateData) {
        iaCard.updateData(contextData);
      }
    });
  };

  // Actualizar contexto inicialmente y cada minuto
  updateSalesContext();
  setInterval(updateSalesContext, 60000);
});