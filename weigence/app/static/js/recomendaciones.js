(function () {
  const headerPanel = document.getElementById("ai-recomendacion-header");
  const headerText = document.getElementById("ai-recomendacion-text");
  const auditoriaPanel = document.getElementById("ai-recs-list")?.closest(".ia-panel");
  let rotationTimer = null;

  const LABELS = {
    normal: "Normal",
    advertencia: "Advertencia",
    critico: "Crítico",
  };

  function obtenerContexto() {
    const path = window.location.pathname.split("/").filter(Boolean);
    return path[0] || "dashboard";
  }

  function normalizar(rec) {
    if (!rec) return null;
    if (typeof rec === "string") {
      return { mensaje: rec, nivel: "normal", categoria: null };
    }
    const mensaje = (rec.mensaje || "").toString().trim();
    if (!mensaje) return null;
    const nivel = (rec.nivel || "normal").toLowerCase();
    return {
      mensaje,
      nivel: ["normal", "advertencia", "critico"].includes(nivel) ? nivel : "normal",
      categoria: rec.categoria || null,
    };
  }

  function aplicarSeveridad(nivel) {
    if (!headerPanel) return;
    headerPanel.dataset.nivel = nivel || "normal";
  }

  function crearItemLista(rec) {
    const nivel = rec.nivel || "normal";
    const etiqueta = LABELS[nivel] || LABELS.normal;
    return `
      <li class="leading-snug flex flex-col gap-1">
        <span class="ia-badge ia-badge--${nivel}">${etiqueta}</span>
        <span class="ia-mensaje">${rec.mensaje}</span>
      </li>
    `;
  }

  function mostrarAuditoria(lista) {
    const ul = document.getElementById("ai-recs-list");
    if (!ul) return;
    const niveles = { normal: 0, advertencia: 1, critico: 2 };
    if (!lista.length) {
      ul.innerHTML = "<li class=\"leading-snug\">No se encontraron recomendaciones.</li>";
      if (auditoriaPanel) auditoriaPanel.dataset.nivel = "normal";
      return;
    }
    const severidad = lista.reduce((nivel, rec) => {
      const valor = niveles[rec.nivel] ?? 0;
      return valor > (niveles[nivel] ?? 0) ? rec.nivel : nivel;
    }, "normal");
    ul.innerHTML = lista.map(crearItemLista).join("");
    ul.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 500, fill: "forwards" });
    if (auditoriaPanel) auditoriaPanel.dataset.nivel = severidad;
  }

  function rotarMensajes(lista) {
    if (!headerText || !headerPanel || !lista.length) return;
    if (rotationTimer) {
      clearInterval(rotationTimer);
    }

    let indice = 0;
    const duracion = 10000;

    const mostrar = () => {
      const rec = lista[indice];
      const nivel = rec?.nivel || "normal";
      headerText.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 400, fill: "forwards" }).onfinish = () => {
        headerText.textContent = rec?.mensaje || "";
        aplicarSeveridad(nivel);
        headerText.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 400, fill: "forwards" });
      };
      indice = (indice + 1) % lista.length;
    };

    mostrar();
    rotationTimer = setInterval(mostrar, duracion);
  }

  function procesarRespuesta(data) {
    if (!Array.isArray(data)) return [];
    return data.map(normalizar).filter(Boolean);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const contexto = obtenerContexto();

    const pContexto = fetch(`/api/recomendaciones?contexto=${encodeURIComponent(contexto)}`)
      .then((r) => (r.ok ? r.json() : []))
      .then(procesarRespuesta)
      .catch(() => []);

    const pGlobal = fetch("/api/ia/header")
      .then((r) => (r.ok ? r.json() : []))
      .then(procesarRespuesta)
      .catch(() => []);

    Promise.all([pContexto, pGlobal]).then(([ctxArr, globalArr]) => {
      const mensajes = [...ctxArr, ...globalArr];
      if (!mensajes.length) {
        mensajes.push({ mensaje: "No hay recomendaciones disponibles.", nivel: "normal" });
      }
      rotarMensajes(mensajes);
    });

    if (contexto === "auditoria") {
      const cargarAuditoria = () => {
        fetch("/api/ia/auditoria")
          .then((r) => (r.ok ? r.json() : []))
          .then(procesarRespuesta)
          .then(mostrarAuditoria)
          .catch(() => {
            mostrarAuditoria([
              { mensaje: "Error al cargar IA avanzada.", nivel: "critico" },
            ]);
          });
      };

      cargarAuditoria();

      const boton = document.getElementById("btn-refresh-auditoria");
      if (boton) {
        boton.addEventListener("click", (ev) => {
          ev.preventDefault();
          cargarAuditoria();
        });
      }
    }
  });
})();
