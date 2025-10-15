document.addEventListener('DOMContentLoaded', () => {
  try {
    const canvas = document.getElementById('salesTrendChart');
    if (!canvas) return; // nothing to render on this page
    const ctx = canvas.getContext ? canvas.getContext('2d') : null;
    if (!ctx) return;

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],
        datasets: [{
          label: 'Sales',
          data: [120, 150, 130, 170, 180, 160, 200],
          borderColor: '#3B82F6',
          backgroundColor: 'rgba(59,130,246,0.2)',
          tension: 0.4,
          fill: true
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } } }
    });
  } catch (e) {
    // Fail silently in dashboards that don't include this chart
    console.warn('charts.js: could not initialize salesTrendChart', e);
  }
});