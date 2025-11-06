(function () {
  function obtenerContexto() {
    const path = window.location.pathname.split("/").filter(Boolean);
    return path[0] || "dashboard";
  }

  function mostrarAuditoria(lista) {
    const ul = document.getElementById("ai-recs-list");
    if (!ul) return;
    if (!lista.length) {
      ul.innerHTML = "<li>No se encontraron recomendaciones.</li>";
      return;
    }
    ul.innerHTML = lista.map(r => `<li>${r}</li>`).join("");
    ul.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, fill: "forwards" });
  }

  // Rotación de mensajes en header
  function rotarMensajes(lista) {
    const el = document.getElementById("ai-recomendacion-text");
    if (!el || !lista.length) return;
    let idx = 0;
    const duracion = 10000; // 10 segundos

    function mostrar() {
      const msg = lista[idx];
      el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 600, fill: "forwards" })
        .onfinish = () => {
          el.textContent = msg;
          el.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, fill: "forwards" });
        };
      idx = (idx + 1) % lista.length;
    }

    mostrar();
    setInterval(mostrar, duracion);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const ctx = obtenerContexto();

    const pCtx = fetch(`/api/recomendaciones?contexto=${encodeURIComponent(ctx)}`)
      .then(r => (r.ok ? r.json() : []))
      .then(arr => arr[0] || null)
      .catch(() => null);

    const pGlobal = fetch("/api/ia/header")
      .then(r => (r.ok ? r.json() : []))
      .then(arr => (Array.isArray(arr) ? arr : []))
      .catch(() => []);

    Promise.all([pCtx, pGlobal]).then(([ctxMsg, globalArr]) => {
      const all = [ctxMsg, ...globalArr.filter(Boolean)];
      const mensajes = all.filter(Boolean).slice(0, 5);
      rotarMensajes(mensajes.length ? mensajes : ["No hay recomendaciones disponibles."]);
    });

    if (ctx === "auditoria") {
    fetch("/api/ia/auditoria")
        .then(r => r.ok ? r.json() : [])
        .then(data => {
        const ul = document.getElementById("ai-recs-list");
        if (!ul) return;
        ul.innerHTML = data.length
            ? data.map(r => `<li class="leading-snug">${r}</li>`).join("")
            : "<li>Sin análisis disponibles.</li>";
        })
        .catch(() => {
        const ul = document.getElementById("ai-recs-list");
        if (ul) ul.innerHTML = "<li>Error al cargar IA avanzada.</li>";
        });
    }
  });
})();
