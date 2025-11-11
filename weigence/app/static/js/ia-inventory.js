// Inicializa el contexto de la IA para la página de inventario
document.addEventListener('DOMContentLoaded', () => {
  // Obtener todas las tarjetas IA del inventario
  const inventoryCards = document.querySelectorAll('[data-ia-card]');
  
  // Función para obtener datos de productos
  const getProductData = () => {
    const products = document.querySelectorAll('[data-product]');
    return Array.from(products).map(product => ({
      id: product.dataset.product,
      name: product.dataset.name,
      stock: Number(product.dataset.stock),
      weight: Number(product.dataset.weight),
      lastUpdate: product.dataset.lastUpdate,
      hasAlert: product.classList.contains('has-alert')
    }));
  };

  // Función para obtener datos de alertas
  const getAlertData = () => {
    const alerts = document.querySelectorAll('[data-inventory-alert]');
    return Array.from(alerts).map(alert => ({
      type: alert.dataset.type,
      severity: alert.dataset.severity,
      message: alert.textContent,
      timestamp: alert.dataset.timestamp
    }));
  };

  // Función para obtener métricas generales
  const getMetrics = () => {
    const metrics = document.querySelectorAll('[data-metric]');
    return Array.from(metrics).reduce((data, metric) => {
      const metricId = metric.dataset.metric;
      data[metricId] = {
        value: metric.dataset.value,
        trend: metric.dataset.trend,
        unit: metric.dataset.unit
      };
      return data;
    }, {});
  };

  // Función para actualizar contexto
  const updateInventoryContext = () => {
    const contextData = {
      products: getProductData(),
      alerts: getAlertData(),
      metrics: getMetrics(),
      timestamp: new Date().toISOString()
    };

    // Actualizar cada tarjeta con el nuevo contexto
    inventoryCards.forEach(card => {
      const iaCard = card.__iaCard;
      if (iaCard && iaCard.updateData) {
        iaCard.updateData(contextData);
      }
    });
  };

  // Actualizar contexto inicialmente y cada minuto
  updateInventoryContext();
  setInterval(updateInventoryContext, 60000);
});