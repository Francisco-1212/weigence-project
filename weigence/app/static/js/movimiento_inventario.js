document.addEventListener("DOMContentLoaded", () => {
  const detalle = document.getElementById("detalle-contextual");
  const items = document.querySelectorAll(".timeline-item");
  const movimientos = window.MOVIMIENTOS || [];

  items.forEach((item, i) => {
    item.addEventListener("dragstart", e => e.dataTransfer.setData("text/plain", i));
    item.addEventListener("click", () => renderDetalle(i));
  });
  detalle.addEventListener("dragover", e => e.preventDefault());
  detalle.addEventListener("drop", e => {
    e.preventDefault();
    renderDetalle(Number(e.dataTransfer.getData("text/plain")));
  });

  function renderDetalle(i) {
    const m = movimientos[i];
    if (!m) return empty("No se pudo cargar el detalle.");

    const tipo = {
      "Añadir": { icon:"south", color:"text-green-400 bg-green-900/40" },
      "Retirar": { icon:"north", color:"text-red-400 bg-red-900/40" },
      "Mover": { icon:"sync_alt", color:"text-blue-400 bg-blue-900/40" }
    }[m.tipo_evento] || { icon:"sync_alt", color:"text-blue-400 bg-blue-900/40" };

    const relacionados = movimientos.filter(x => x.producto === m.producto).slice(0, 4);

    detalle.innerHTML = `
      <div class="p-4 space-y-4 text-neutral-300 text-sm leading-snug">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 flex items-center justify-center rounded-md ${tipo.color}">
              <span class="material-symbols-outlined text-[18px]">${tipo.icon}</span>
            </div>
            <div>
              <h3 class="text-base font-semibold text-white">${m.producto}</h3>
              <p class="text-[11px] text-[var(--text-muted-dark)]">${m.timestamp}</p>
            </div>
          </div>
          <span class="px-2 py-[1px] text-[11px] font-medium rounded bg-[var(--card-bg-dark)] text-primary-400 border border-[var(--border-dark)]">${m.tipo_evento}</span>
        </div>

        <div class="grid grid-cols-2 gap-2">
          ${info("Cantidad", m.cantidad + " kg")}
          ${info("Ubicación", m.ubicacion)}
          ${info("Usuario", m.usuario_nombre)}
          ${info("RUT", m.rut_usuario)}
        </div>

        <div class="bg-[var(--card-bg-dark)] border border-[var(--border-dark)] rounded-md p-3">
          <p class="text-[11px] text-[var(--text-muted-dark)] mb-1">Observación</p>
          <p class="text-neutral-200 text-[13px]">${m.observacion || "Sin observaciones."}</p>
        </div>

        <div>
          <p class="text-[13px] font-medium text-white mb-1">Historial del producto</p>
          <ul class="space-y-1">
            ${relacionados.map(r => {
              const t = {
                "Añadir": "text-green-400",
                "Retirar": "text-red-400",
                "Mover": "text-blue-400"
              }[r.tipo_evento] || "text-blue-400";
              return `
                <li class="flex justify-between items-center text-[12px] bg-[var(--card-bg-dark)] border border-[var(--border-dark)] rounded-md px-2 py-1">
                  <span class="flex items-center gap-1">
                    <span class="material-symbols-outlined text-[14px] ${t}">${r.tipo_evento=="Añadir"?"south":r.tipo_evento=="Retirar"?"north":"sync_alt"}</span>
                    ${r.tipo_evento} • ${r.cantidad}kg
                  </span>
                  <span class="text-[var(--text-muted-dark)]">${r.timestamp.slice(11,16)}</span>
                </li>`;
            }).join("")}
          </ul>
        </div>
      </div>
    `;
  }

  function info(label, value) {
    return `
      <div class="bg-[var(--card-bg-dark)] border border-[var(--border-dark)] rounded-lg p-3">
        <p class="text-xs text-[var(--text-muted-dark)]">${label}</p>
        <p class="text-sm font-semibold text-white mt-1">${value || "—"}</p>
      </div>
    `;
  }

  function empty(msg) {
    detalle.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full text-[var(--text-muted-dark)]">
        <span class="material-symbols-outlined text-5xl mb-2">error_outline</span>
        <p class="text-sm">${msg}</p>
      </div>`;
  }

  // Tabs simples
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("text-primary-600","dark:text-primary-400","border-primary"));
      btn.classList.add("text-primary-600","dark:text-primary-400","border-primary");

      const tab = btn.getAttribute("data-tab");
      document.querySelectorAll(".tab-content").forEach(c => c.classList.add("hidden"));
      document.getElementById(`tab-${tab}`).classList.remove("hidden");
    });
  });
});
