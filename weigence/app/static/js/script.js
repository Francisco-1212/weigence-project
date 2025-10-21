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
    
    const themeToggle = document.getElementById('theme-toggle');

    if (themeToggle) {
        // Comprobar preferencia del usuario
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            document.documentElement.classList.add('dark');
            themeToggle.checked = true;  // ¡Sincroniza switch!
        } else {
            document.documentElement.classList.remove('dark');
            themeToggle.checked = false;
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

    const nav = document.getElementById('sidebar-nav');
    const profilePanel = document.getElementById('sidebar-profile');
    const trigger = document.getElementById('profile-trigger');
    const backBtn = document.getElementById('profile-back');

    trigger.addEventListener('click', () => {
    nav.classList.add('hidden');
    profilePanel.classList.remove('hidden');
    trigger.classList.add('hidden');
    });

    backBtn.addEventListener('click', () => {
    profilePanel.classList.add('hidden');
    nav.classList.remove('hidden');
    trigger.classList.remove('hidden');
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

async function cargarVentasPorProducto() {
    try {
        const response = await fetch('/api/ventas_por_producto');
        if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

        const data = await response.json();

        if (!data.productos || data.productos.length === 0) {
            mostrarEstado('No hay datos de ventas disponibles');
            return;
        }

        actualizarGrafico(data);
    } catch (error) {
        console.error('Error:', error);
        mostrarEstado('Error al cargar los datos: ' + error.message);
    }
}

function actualizarGrafico(data) {
    const productos = data.productos.slice(0, 6); // Top 8
    const totalVentas = productos.reduce((sum, p) => sum + p.ventas, 0);
    const crecimientoTotal = data.crecimiento;

    // Actualizar totales
    document.getElementById('totalSales').textContent = `$${totalVentas.toFixed(0)}`;
    const growthEl = document.getElementById('growthPercentage');
    growthEl.textContent = `${crecimientoTotal >= 0 ? '+' : ''}${crecimientoTotal}%`;
    growthEl.className = `text-sm font-medium ${crecimientoTotal >= 0 ? 'text-green-500' : 'text-red-500'}`;

    // Generar gráfico
    generarBarras(productos);
}

function generarBarras(productos) {
    // Prefer the unified renderer from filtro.js if present
    if (typeof window.renderBarsFromGrafico === 'function') {
        try {
            const grafico = { productos: productos.map(p => ({ nombre: p.nombre || p.name || '', ventas: p.ventas || p.sales || 0 })) };
            window.renderBarsFromGrafico(grafico);
            return;
        } catch (e) {
            console.warn('generarBarras: renderBarsFromGrafico delegation failed, falling back', e);
        }
    }

    const chartContainer = document.getElementById('chartContainer');
    const chartLabels = document.getElementById('chartLabels');
    if (!chartContainer || !chartLabels) {
        console.debug('generarBarras: chart containers not found, skipping');
        return;
    }
    chartContainer.innerHTML = '';
    chartLabels.innerHTML = '';

    const maxVentas = Math.max(...productos.map(p => (p.ventas || p.sales || 0)));
    productos.forEach(p => {
        const value = p.ventas || p.sales || 0;
        let altura = maxVentas > 0 ? (value / maxVentas) * 100 : 0;
        if (!isFinite(altura) || altura <= 0) altura = 10;
        const barra = document.createElement('div');
        barra.className = `w-full bg-blue-600 rounded-t-lg transition-all duration-500 hover:bg-blue-700 cursor-pointer`;
        barra.style.height = `${altura}%`;
        barra.title = `${p.nombre || p.name}: $${(value).toFixed ? value.toFixed(0) : value}`;
        chartContainer.appendChild(barra);

        const label = document.createElement('div');
        label.textContent = p.nombre || p.name;
        label.className = 'text-center text-sm font-medium mt-1 truncate';
        chartLabels.appendChild(label);
    });
}


function mostrarEstado(msg) {
    const chartContainer = document.getElementById('chartContainer');
    const chartLabels = document.getElementById('chartLabels');
    chartContainer.innerHTML = '';
    chartLabels.innerHTML = '';
    chartContainer.innerHTML = `<div class="col-span-full text-center py-8 text-gray-500">${msg}</div>`;
}

const topSales = [
      { name: "Producto A", sales: 150, rotation: "Alta", tagClass: "tag-green" },
      { name: "Producto B", sales: 120, rotation: "Media", tagClass: "tag-blue" },
      { name: "Producto C", sales: 100, rotation: "Media", tagClass: "tag-blue" },
      { name: "Producto D", sales: 95, rotation: "Media", tagClass: "tag-blue" },
      { name: "Producto E", sales: 80, rotation: "Media", tagClass: "tag-blue" }
    ];

    const lowSales = [
      { name: "Producto X", sales: 10, rotation: "Baja", tagClass: "tag-red" },
      { name: "Producto Y", sales: 15, rotation: "Baja", tagClass: "tag-red" },
      { name: "Producto Z", sales: 20, rotation: "Baja", tagClass: "tag-red" },
      { name: "Producto W", sales: 25, rotation: "Muy Baja", tagClass: "tag-yellow" },
      { name: "Producto V", sales: 30, rotation: "Muy Baja", tagClass: "tag-yellow" }
    ];

        function renderProducts(containerId, products) {
            const container = document.getElementById(containerId);
            const template = document.getElementById("product-card-template");
            if (!container) {
                console.debug(`renderProducts: container "${containerId}" not found, skipping`);
                return;
            }
            if (!template) {
                console.debug('renderProducts: product-card-template not found, skipping');
                return;
            }
            container.innerHTML = "";
            products.forEach(({ name, sales, rotation, tagClass }) => {
                const clone = template.content.cloneNode(true);
                const firstDiv = clone.querySelector("div:nth-child(1)");
                const secondDiv = clone.querySelector("div:nth-child(2)");
                if (firstDiv) firstDiv.textContent = name;
                if (secondDiv) secondDiv.textContent = sales;
                const span = clone.querySelector("span");
                if (span) {
                    span.textContent = rotation;
                    span.className = tagClass;
                }
                container.appendChild(clone);
            });
        }

        document.addEventListener('DOMContentLoaded', () => {
            // Only render sample top/low lists if the corresponding containers exist.
            if (document.getElementById('top-sales-container')) {
                renderProducts('top-sales-container', topSales);
            }
            if (document.getElementById('low-sales-container')) {
                renderProducts('low-sales-container', lowSales);
            }
        });


// Note: automatic loading of ventas por producto is disabled so the filter
// controls in filtro.js own the dashboard chart rendering. If you need to
// debug raw ventas_por_producto data, call cargarVentasPorProducto() manually.
// document.addEventListener('DOMContentLoaded', cargarVentasPorProducto);

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', inicializarAplicacion);

console.log("✅ script.js cargado correctamente");