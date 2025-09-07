  const ctx = document.getElementById('salesTrendChart');
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