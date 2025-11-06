window.addEventListener("load", () => {
  const darkMode = document.documentElement.classList.contains("dark");
  const textColor = darkMode ? "#ddd" : "#222";
  const gridColor = darkMode ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";

  // === Gráfico 1 - Distribución de eventos ===
  new Chart(document.getElementById("chartEventos"), {
    type: "doughnut",
    data: {
      labels: ["Accesos", "Pesos", "Fallas"],
      datasets: [
        {
          data: [40, 35, 25],
          backgroundColor: ["#3b82f6", "#f59e0b", "#ef4444"],
          borderWidth: 0,
        },
      ],
    },
    options: {
      plugins: {
        legend: { labels: { color: textColor } },
      },
      cutout: "65%",
    },
  });

  // === Gráfico 2 - Incidencias semanales ===
  new Chart(document.getElementById("chartIncidencias"), {
    type: "bar",
    data: {
      labels: ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
      datasets: [
        {
          label: "Incidencias",
          data: [2, 3, 1, 4, 2, 3, 5],
          backgroundColor: "rgba(59,130,246,0.5)",
          borderRadius: 6,
        },
      ],
    },
    options: {
      scales: {
        x: { grid: { display: false }, ticks: { color: textColor } },
        y: { grid: { color: gridColor }, ticks: { color: textColor } },
      },
      plugins: { legend: { display: false } },
    },
  });

  // === Gráfico 3 - Actividad por hora ===
  new Chart(document.getElementById("chartActividad"), {
    type: "line",
    data: {
      labels: Array.from({ length: 24 }, (_, i) => i + ":00"),
      datasets: [
        {
          label: "Eventos por hora",
          data: [2, 3, 1, 2, 3, 4, 6, 8, 9, 7, 5, 4, 3, 6, 8, 9, 5, 4, 2, 2, 1, 1, 2, 3],
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59,130,246,0.2)",
          fill: true,
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    },
    options: {
      scales: {
        x: { grid: { display: false }, ticks: { color: textColor } },
        y: { grid: { color: gridColor }, ticks: { color: textColor } },
      },
      plugins: { legend: { display: false } },
    },
  });

  // === Ajustar tamaño tras carga inicial ===
  setTimeout(() => {
    Object.values(Chart.instances).forEach((instance) => instance.resize());
  }, 200);
});

const LABELS = {
  normal: "Normal",
  advertencia: "Advertencia",
  critico: "Crítico",
};

const auditoriaPanel = document.getElementById("ai-recs-list")?.closest(".ia-panel");

function procesarRespuesta(data) {
  if (!Array.isArray(data)) return [];
  return data
    .map((rec) => {
      if (typeof rec === "string") {
        return { mensaje: rec, nivel: "normal" };
      }
      const mensaje = (rec?.mensaje || "").toString().trim();
      if (!mensaje) return null;
      const nivel = (rec?.nivel || "normal").toLowerCase();
      return {
        mensaje,
        nivel: ["normal", "advertencia", "critico"].includes(nivel) ? nivel : "normal",
      };
    })
    .filter(Boolean);
}

function renderAuditoria(lista) {
  const ul = document.getElementById("ai-recs-list");
  if (!ul) return;
  const niveles = { normal: 0, advertencia: 1, critico: 2 };
  if (!lista.length) {
    ul.innerHTML = "<li class=\"leading-snug\">Sin recomendaciones por ahora.</li>";
    if (auditoriaPanel) auditoriaPanel.dataset.nivel = "normal";
    return;
  }
  const severidad = lista.reduce((nivel, rec) => {
    const valor = niveles[rec.nivel] ?? 0;
    return valor > (niveles[nivel] ?? 0) ? rec.nivel : nivel;
  }, "normal");
  ul.innerHTML = lista
    .map((rec) => {
      const nivel = rec.nivel || "normal";
      const etiqueta = LABELS[nivel] || LABELS.normal;
      return `
        <li class="leading-snug flex flex-col gap-1">
          <span class="ia-badge ia-badge--${nivel}">${etiqueta}</span>
          <span class="ia-mensaje">${rec.mensaje}</span>
        </li>`;
    })
    .join("");
  if (auditoriaPanel) auditoriaPanel.dataset.nivel = severidad;
}

setInterval(() => {
  fetch("/api/recomendaciones?contexto=auditoria")
    .then((r) => (r.ok ? r.json() : []))
    .then(procesarRespuesta)
    .then(renderAuditoria)
    .catch(() => {
      renderAuditoria([{ mensaje: "Error al actualizar recomendaciones.", nivel: "critico" }]);
    });
}, 60000);
