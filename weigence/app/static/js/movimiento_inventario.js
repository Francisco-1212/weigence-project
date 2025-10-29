document.addEventListener("DOMContentLoaded", () => {
  const detalle = document.getElementById("detalle-contextual");
  const contenedor = document.getElementById("timeline-container");
  const cerrarBtn = document.getElementById("cerrar-detalle");
  const movimientos = Array.isArray(window.MOVIMIENTOS) ? window.MOVIMIENTOS : [];

  const fTipo = document.getElementById("filter-type");
  const fUser = document.getElementById("filter-user");
  const fLoc  = document.getElementById("filter-location");
  const fDate = document.getElementById("filter-date");

  if (!detalle || !contenedor) return;

  // --- Click y Drag & Drop ---
  contenedor.addEventListener("click", (e) => {
    const item = e.target.closest(".timeline-item");
    if (!item) return;
    selectItem(item);
    renderDetalle(Number(item.dataset.index));
  });

  contenedor.addEventListener("dragstart", (e) => {
    const item = e.target.closest(".timeline-item");
    if (!item) return;
    const img = new Image();
    img.src =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAEklEQVR42mP8/5+hHgAHggJ/P6pHUgAAAABJRU5ErkJggg==";
    e.dataTransfer.setDragImage(img, 0, 0);
    e.dataTransfer.setData("text/plain", item.dataset.index);
    item.classList.add("dragging");
  });

  contenedor.addEventListener("dragend", (e) => {
    const item = e.target.closest(".timeline-item");
    if (item) item.classList.remove("dragging");
  });

  detalle.addEventListener("dragover", (e) => {
    e.preventDefault();
    detalle.classList.add("ring-2", "ring-primary-400/50");
  });
  detalle.addEventListener("dragleave", () => {
    detalle.classList.remove("ring-2", "ring-primary-400/50");
  });
  detalle.addEventListener("drop", (e) => {
    e.preventDefault();
    detalle.classList.remove("ring-2", "ring-primary-400/50");
    const i = Number(e.dataTransfer.getData("text/plain"));
    const el = contenedor.querySelector(`.timeline-item[data-index="${i}"]`);
    if (el) selectItem(el);
    renderDetalle(i);
  });

  if (cerrarBtn) cerrarBtn.addEventListener("click", resetDetalle);

  // --- Filtros dinámicos ---
  [fTipo, fUser, fLoc, fDate].forEach((el) => el && el.addEventListener("input", applyFilters));
  function applyFilters() {
    const t = fTipo?.value || "";
    const u = (fUser?.value || "").trim().toLowerCase();
    const l = (fLoc?.value || "").trim().toLowerCase();
    const d = fDate?.value || "";

    contenedor.querySelectorAll(".timeline-item").forEach((it) => {
      const okTipo = !t || it.dataset.tipo === t;
      const okUser = !u || it.dataset.user.includes(u);
      const okLoc  = !l || it.dataset.ubicacion.includes(l);
      const okDate = !d || it.dataset.fecha === d;
      it.classList.toggle("hidden", !(okTipo && okUser && okLoc && okDate));
    });
  }

  // --- Selección visual ---
  function selectItem(item) {
    contenedor.querySelectorAll(".timeline-item").forEach((el) => {
      el.classList.remove("item-activo", "ring-2", "ring-primary-400/50", "ring-primary-500/60", "selected");
    });

    item.classList.add(
      "item-activo",
      "ring-2",
      document.documentElement.classList.contains("dark")
        ? "ring-gray-500/60"
        : "ring-gray-500/60",
      "selected"
    );
  }


  // --- Render de detalle ---
  function renderDetalle(i) {
    const m = movimientos[i];
    if (!m) return;

    const tipo = {
      "Añadir": { icon: "south", color: "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/40" },
      "Retirar": { icon: "north", color: "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/40" },
      "Mover": { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" },
    }[m.tipo_evento] || { icon: "sync_alt", color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/40" };

    const relacionados = movimientos.filter(x => x.producto === m.producto).slice(0, 8);

    detalle.className = "min-h-[46vh] flex flex-col bg-[var(--card-bg-light)] dark:bg-[var(--card-sub-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg p-5 space-y-5 overflow-auto";

    detalle.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 flex items-center justify-center rounded-md ${tipo.color}">
            <span class="material-symbols-outlined text-[20px]">${tipo.icon}</span>
          </div>
          <div>
            <h2 class="text-[15px] font-semibold text-[var(--text-light)] dark:text-white leading-tight">${m.producto}</h2>
            <p class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)]">${m.timestamp}</p>
          </div>
        </div>
        <span class="px-2 py-[2px] text-[11px] font-medium rounded border border-neutral-300 dark:border-[var(--border-dark)] text-primary-600 dark:text-primary-400 bg-neutral-100 dark:bg-[var(--card-bg-dark)]">
          ${m.tipo_evento}
        </span>
      </div>

      <div class="grid grid-cols-2 gap-3">
        ${info("Cantidad", `${m.cantidad} kg`)}
        ${info("Ubicación", m.ubicacion || "—")}
        ${info("Usuario", m.usuario_nombre || "Desconocido")}
        ${info("RUT", m.rut_usuario || "—")}
      </div>

      <div class="bg-neutral-100 dark:bg-[var(--card-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg p-4">
        <p class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)] uppercase tracking-wide mb-1">Observación</p>
        <p class="text-[13px] text-neutral-800 dark:text-neutral-200 leading-snug">${m.observacion || "Sin observaciones."}</p>
      </div>

      <div>
        <p class="text-[13px] font-semibold text-[var(--text-light)] dark:text-white mb-2">Historial del producto</p>
        <div class="rounded-lg overflow-hidden border border-neutral-300 dark:border-[var(--border-dark)] divide-y divide-neutral-300 dark:divide-[var(--border-dark)]">
          ${relacionados.map(r => `
            <div class="flex justify-between items-center px-3 py-2 bg-neutral-50 dark:bg-[var(--card-bg-dark)] hover:bg-neutral-100 dark:hover:bg-neutral-800/50 transition-colors">
              <span class="flex items-center gap-2">
                <span class="material-symbols-outlined text-[14px] ${
                  r.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-400" :
                  r.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-400" : "text-blue-600 dark:text-blue-400"
                }">${r.tipo_evento === "Añadir" ? "south" : r.tipo_evento === "Retirar" ? "north" : "sync_alt"}</span>
                ${r.tipo_evento} • ${r.cantidad}kg
              </span>
              <span class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)]">${String(r.timestamp).slice(11,16)}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  function info(label, value) {
    return `
      <div class="bg-neutral-100 dark:bg-[var(--card-bg-dark)] border border-neutral-300 dark:border-[var(--border-dark)] rounded-lg p-3">
        <p class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)] uppercase tracking-wide">${label}</p>
        <p class="text-[14px] font-semibold text-[var(--text-light)] dark:text-white mt-1">${value || "—"}</p>
      </div>
    `;
  }

  function resetDetalle() {
    detalle.className = "min-h-[46vh] flex flex-col items-center justify-center border-2 border-dashed border-neutral-400/40 dark:border-[var(--border-dark)] rounded-lg text-center px-6 py-10";
    detalle.innerHTML = `
      <span class="material-symbols-outlined text-5xl text-neutral-400 dark:text-neutral-600">touch_app</span>
      <p class="mt-2 text-sm text-neutral-500">Selecciona o arrastra un movimiento para ver detalles</p>
      <p class="text-xs text-neutral-500">Historial, usuarios y observaciones aparecerán aquí</p>
    `;
  }

  // --- Estado inicial ---
  resetDetalle();
  applyFilters();
});
