function mostrarModal(peso, alerta, fecha) {
    document.getElementById("modal-peso").innerText = peso;
    document.getElementById("modal-alerta").innerText = alerta ? "Sí" : "No";
    document.getElementById("modal-fecha").innerText = fecha;
    document.getElementById("modal").style.display = "block";
}

// Cerrar modal
function cerrarModal() {
    document.getElementById("modal").style.display = "none";
}

// Eliminar fila con confirmación
function eliminarFila(boton) {
    if (!confirm("¿Estás seguro de eliminar esta fila?")) return;

    const fila = boton.closest("tr");
    fila.style.backgroundColor = "#ffdddd";
    fila.style.transition = "opacity 0.5s ease";
    fila.style.opacity = 0;

    setTimeout(() => fila.remove(), 500);
    mostrarToast("Fila eliminada correctamente", "eliminado");
}

// Descargar datos de la fila (puedes ajustar contenido)
function descargarDatos(peso, alerta, fecha) {
    const contenido = `Peso: ${peso}g\nAlerta: ${alerta ? "Sí" : "No"}\nFecha: ${fecha}`;
    const blob = new Blob([contenido], { type: "text/plain" });
    const enlace = document.createElement("a");

    enlace.href = URL.createObjectURL(blob);
    enlace.download = `pesaje_${fecha.replace(/[: ]/g, "_")}.txt`;
    enlace.click();

    mostrarToast("Archivo descargado", "descarga");
}

// Función simulada para botón simular alerta
function simularAlerta(boton) {
    const fila = boton.closest("tr");

    // Cambiar la clase para mostrar que tiene alerta
    fila.classList.add("alerta-true");
    fila.classList.remove("alerta-false");

    // Opcional: si tienes alguna columna que muestre el icono alerta, actualizarla
    // Por ejemplo, suponiendo que la columna 3 (index 3) es la de alerta:
    fila.children[3].innerText = "⚠️";

    mostrarToast("Alerta simulada correctamente", "info");
}



function mostrarToast(mensaje) {
    const toast = document.getElementById("toast");

    // Reinicia clases y aplica solo las necesarias
    toast.className = "toast";

    // Mostrar mensaje
    setTimeout(() => {
        toast.classList.add("show");
        toast.innerText = mensaje;
    }, 10);

    // Ocultar automáticamente después de 3 segundos
    setTimeout(() => {
        toast.className = "toast";
    }, 4010);
}
function marcarRevisada(boton) {
    const fila = boton.closest("tr");

    // Cambiar texto a "Sí" en columna Revisada (índice 5)
    fila.children[5].innerText = "Sí";

    // Cambiar botones en columna Acciones (índice 6)
    fila.children[6].innerHTML = `
        <button class="accion ver" onclick="mostrarModal('${fila.children[2].innerText}', true, '${fila.children[4].innerText}')">🔍</button>
        <button class="accion revisada" disabled>✔️ Revisada</button>
        <button class="accion eliminar" onclick="eliminarFila(this)">🗑️</button>
    `;

    mostrarToast("✔️ Alerta marcada como revisada");
}


function filtrarHistorial() {
    const productoFiltro = document.getElementById("filtro-producto").value.toLowerCase();
    const fechaInicio = document.getElementById("filtro-inicio").value;
    const fechaFin = document.getElementById("filtro-fin").value;
    const filas = document.querySelectorAll("#tabla-historial tbody tr");

    filas.forEach(fila => {
        const textoProducto = fila.children[0].innerText.toLowerCase();
        const fechaTexto = fila.children[3].innerText;

        const pasaFiltroTexto = textoProducto.includes(productoFiltro);

        const fechaFila = new Date(fechaTexto);
        const desde = fechaInicio ? new Date(fechaInicio) : null;
        const hasta = fechaFin ? new Date(fechaFin) : null;

        let pasaFiltroFecha = true;
        if (desde && fechaFila < desde) pasaFiltroFecha = false;
        if (hasta && fechaFila > hasta) pasaFiltroFecha = false;

        if (pasaFiltroTexto && pasaFiltroFecha) {
            fila.style.display = "";
        } else {
            fila.style.display = "none";
        }
    });

    mostrarToast("Filtro aplicado");
}
function limpiarFiltros() {
    document.getElementById("filtro-producto").value = "";
    document.getElementById("filtro-inicio").value = "";
    document.getElementById("filtro-fin").value = "";

    filtrarHistorial(); // vuelve a aplicar con campos vacíos
    mostrarToast("Filtros limpiados");
}
function filtrarAlertas() {
    const filtroRevisadas = document.getElementById("filtro-revisadas");
    if (!filtroRevisadas) return;  // Salir si no existe el filtro en esta página

    const seleccion = filtroRevisadas.value;
    const filas = document.querySelectorAll("#tabla-alertas tbody tr");

    filas.forEach(fila => {
        const textoRevisada = fila.children[5].innerText.trim();
        const revisada = textoRevisada.toLowerCase() === "sí";

        if (
            seleccion === "todas" ||
            (seleccion === "no-revisadas" && !revisada) ||
            (seleccion === "revisadas" && revisada)
        ) {
            fila.style.display = "";
        } else {
            fila.style.display = "none";
        }
    });
}
document.addEventListener('DOMContentLoaded', () => {
    filtrarAlertas();
});


document.addEventListener("DOMContentLoaded", () => {
  const btnPesajes = document.getElementById("btn-pesajes");
  const btnAlertas = document.getElementById("btn-alertas");
  const btnOcultar = document.getElementById("btn-ocultar");
  const chartSection = document.getElementById("chart-section");
  const ctx = document.getElementById("chart").getContext("2d");

  let chartInstance = null;

  const datosPesajes = {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct"],
    datasets: [{
      label: "Pesajes (g)",
      data: [1200, 1300, 1150, 1400, 1350, 1500, 1600, 1550, 1650, 1700],
      borderColor: "blue",
      backgroundColor: "rgba(0,0,255,0.1)",
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
    }]
  };

  const datosAlertas = {
    labels: ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct"],
    datasets: [{
      label: "Alertas activas",
      data: [3, 5, 2, 7, 6, 4, 8, 7, 5, 4],
      borderColor: "red",
      backgroundColor: "rgba(255,0,0,0.1)",
      fill: true,
      tension: 0.3,
      pointRadius: 4,
      pointHoverRadius: 6,
    }]
  };

  function mostrarGrafico(datos) {
    if (chartInstance) chartInstance.destroy();

    chartInstance = new Chart(ctx, {
      type: "line",
      data: datos,
      options: {
        responsive: true,
        plugins: {
          legend: { position: "top" }
        }
      }
    });

    chartSection.style.display = "block";
    btnOcultar.style.display = "inline-block";
  }

  function actualizarTabs(activo) {
    btnPesajes.classList.remove("active");
    btnAlertas.classList.remove("active");

    if (activo === "pesajes") btnPesajes.classList.add("active");
    if (activo === "alertas") btnAlertas.classList.add("active");
  }

  btnPesajes.addEventListener("click", () => {
    mostrarGrafico(datosPesajes);
    actualizarTabs("pesajes");
  });

  btnAlertas.addEventListener("click", () => {
    mostrarGrafico(datosAlertas);
    actualizarTabs("alertas");
  });

  btnOcultar.addEventListener("click", () => {
    if (chartInstance) {
      chartInstance.destroy();
      chartInstance = null;
    }
    chartSection.style.display = "none";
    btnOcultar.style.display = "none";

    btnPesajes.classList.remove("active");
    btnAlertas.classList.remove("active");
  });

  // Mostrar gráfico y activar pestaña "Pesajes" al cargar
  mostrarGrafico(datosPesajes);
  actualizarTabs("pesajes");
});


console.log("✅ JS cargado correctamente");
