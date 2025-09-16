// Configuración de Tailwind
tailwind.config = {
  darkMode: 'class'
};

// Funciones de utilidad
function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    
    toast.className = "toast";
    
    setTimeout(() => {
        toast.classList.add("show");
        toast.innerText = mensaje;
    }, 10);

    setTimeout(() => {
        toast.className = "toast";
    }, 3000);
}

// Funciones de modal
function mostrarModal(peso, alerta, fecha) {
    const modal = document.getElementById("modal");
    if (!modal) return;
    
    document.getElementById("modal-peso").innerText = peso;
    document.getElementById("modal-alerta").innerText = alerta ? "Sí" : "No";
    document.getElementById("modal-fecha").innerText = fecha;
    modal.style.display = "block";
}

function cerrarModal() {
    const modal = document.getElementById("modal");
    if (modal) modal.style.display = "none";
}

// Funciones de tabla
function eliminarFila(boton) {
    if (!confirm("¿Estás seguro de eliminar esta fila?")) return;

    const fila = boton.closest("tr");
    fila.style.backgroundColor = "#ffdddd";
    fila.style.transition = "opacity 0.5s ease";
    fila.style.opacity = 0;

    setTimeout(() => fila.remove(), 500);
    mostrarToast("Fila eliminada correctamente");
}

// Inicialización de la aplicación
function inicializarAplicacion() {
    console.log("✅ JS cargado correctamente");

    // Toggle del menú móvil
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('overlay');
    
    if (menuToggle && sidebar && overlay) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
        });
        
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('open');
        });
    }
    
    // Toggle del tema
    const themeToggle = document.getElementById('theme-toggle');
    
    if (themeToggle) {
        // Comprobar preferencia del usuario
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
            document.documentElement.classList.add('dark');
            themeToggle.checked = true;
        }
        
        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    
    // Navegación del sidebar
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
            }
            
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
            
            // En móvil, cerrar el sidebar después de hacer clic
            if (window.innerWidth < 1024) {
                sidebar.classList.remove('open');
                overlay.classList.remove('open');
            }
        });
    });
    
    // Selectores de período para gráficos
    const periodSelectors = document.querySelectorAll('input[name="periodo-graficos"]');
    
    periodSelectors.forEach(selector => {
        selector.addEventListener('change', function() {
            console.log('Período seleccionado:', this.value, 'días');
            // Aquí puedes añadir lógica para actualizar gráficos
        });
    });
}

// tendencia de ventas por día
async function crearGraficoVentas() {
    const ctx = document.getElementById("tendenciaVentas").getContext("2d");

    // Detectar modo oscuro/claro
    const isDarkMode = document.documentElement.classList.contains('dark');

    // Traer datos desde API
    const res = await fetch("/api/tendencia_ventas");
    const data = await res.json();

    const ventas = data.data_ventas;

    // Calcular cambio porcentual
    const totalHoy = ventas[ventas.length - 1] || 0;
    const totalAyer = ventas[ventas.length - 2] || 0;
    const cambio = totalAyer > 0 ? ((totalHoy - totalAyer) / totalAyer * 100).toFixed(1) : 0;
    const totalIcon = document.getElementById("totalVentasIcon");
    totalIcon.innerText = `${cambio > 0 ? '+' : ''}${cambio}%`;
    totalIcon.classList.toggle('text-green-500', cambio >= 0);
    totalIcon.classList.toggle('text-red-500', cambio < 0);

    // Crear gradiente lineal para línea
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, isDarkMode ? 'rgba(0,255,128,0.7)' : 'rgba(0,128,0,0.7)');
    gradient.addColorStop(1, isDarkMode ? 'rgba(255,0,0,0.7)' : 'rgba(255,0,0,0.3)');

    // Configuración Chart.js
    new Chart(ctx, {
        type: "line",
        data: {
            labels: data.labels,
            datasets: [{
                label: "Total Ventas",
                data: ventas,
                fill: true,
                backgroundColor: gradient,
                borderColor: isDarkMode ? 'rgba(0,255,128,1)' : 'rgba(0,128,0,1)',
                borderWidth: 3,
                tension: 0.3,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: isDarkMode ? 'rgba(0,255,128,1)' : 'rgba(0,128,0,1)',
                pointBorderColor: isDarkMode ? '#000' : '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: isDarkMode ? '#222' : '#fff',
                    titleColor: isDarkMode ? '#fff' : '#000',
                    bodyColor: isDarkMode ? '#fff' : '#000',
                    borderColor: isDarkMode ? '#444' : '#ccc',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: isDarkMode ? '#fff' : '#000' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: isDarkMode ? '#fff' : '#000' },
                    beginAtZero: true
                }
            }
        }
    });
}

// Ejecutar al cargar la página
document.addEventListener('DOMContentLoaded', crearGraficoVentas);



// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializarAplicacion);

console.log("✅ script.js cargado correctamente");