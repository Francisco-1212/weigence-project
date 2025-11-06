document.addEventListener("DOMContentLoaded", () => {
  const detalle = document.getElementById("detalle-contextual");
  const contenedor = document.getElementById("timeline-container");
  const cerrarBtn = document.getElementById("cerrar-detalle");
  const movimientos = Array.isArray(window.MOVIMIENTOS) ? window.MOVIMIENTOS : [];

  console.log("Movimientos cargados:", movimientos); // Log 1: Ver si los movimientos se cargan

  const fTipo = document.getElementById("filter-type");
  const fUser = document.getElementById("filter-user");
  const fLoc = document.getElementById("filter-location");
  const fDate = document.getElementById("filter-date");

  console.log("Elementos DOM encontrados:", { // Log 2: Verificar elementos DOM
    detalle: !!detalle,
    contenedor: !!contenedor,
    cerrarBtn: !!cerrarBtn,
    fTipo: !!fTipo,
    fUser: !!fUser,
    fLoc: !!fLoc,
    fDate: !!fDate
  });

  if (!detalle || !contenedor) {
    console.error("Elementos requeridos no encontrados"); // Log 3: Error si faltan elementos
    return;
  }

  // Antes de renderizar
  console.log("Intentando renderizar movimientos:", { // Log 4: Pre-renderizado
    cantidadMovimientos: movimientos.length,
    primerMovimiento: movimientos[0]
  });

  // Renderizar movimientos
// Mostrar solo los 7 más recientes
const lista = movimientos.length > 7 ? movimientos.slice(0, 7) : movimientos;

contenedor.innerHTML = lista.map((m, i) => {
  const color = m.tipo_evento === "Añadir" ? "green"
              : m.tipo_evento === "Retirar" ? "red" : "blue";

  return `
    <div class="timeline-item relative pl-8 mb-4 cursor-pointer group"
         data-index="${i}" data-tipo="${m.tipo_evento}" draggable="true">
      <div class="absolute left-0 top-4 w-4 h-4 rounded-full bg-${color}-500 ring-4 ring-[var(--card-bg-light)] dark:ring-[var(--card-bg-dark)]"></div>
      <div class="ml-4 p-4 rounded-xl border border-neutral-300 dark:border-[var(--border-dark)] bg-[var(--card-bg-light)] dark:bg-[var(--card-bg-dark)] shadow-sm hover:border-primary-400 transition">
        <div class="flex items-start justify-between">
          <div>
            <p class="text-sm font-bold text-[var(--text-light)] dark:text-[var(--text-dark)]">
              ${m.tipo_evento === "Añadir" ? "➕" :
                m.tipo_evento === "Retirar" ? "➖" : "⟳"} ${m.producto}
            </p>
            <p class="text-xs text-neutral-600 dark:text-neutral-400 mt-1">
              ${m.ubicacion} • ${m.usuario_nombre}
            </p>
          </div>
          <div class="text-right">
            <p class="text-sm font-bold ${
              m.tipo_evento === "Añadir" ? "text-green-600"
              : m.tipo_evento === "Retirar" ? "text-red-500"
              : "text-blue-500"
            }">
              ${m.tipo_evento === "Añadir" ? "+" : m.tipo_evento === "Retirar" ? "-" : ""}${m.cantidad}kg
            </p>
            <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5">
              ${(m.timestamp || "").split(" ")[1]?.slice(0,5) || ""}
            </p>
          </div>
        </div>
      </div>
    </div>
  `;
}).join("");

// Agregar botón de historial si hay más de 7
if (movimientos.length > 7) {
  contenedor.innerHTML += `
    <div class="flex justify-center mt-4">
      <button class="btn-show-history text-sm text-primary-500 dark:text-primary-400 hover:underline underline-offset-2 focus:outline-none">
        Ver historial completo (${movimientos.length} registros)
      </button>
    </div>
  `;
}
// Reatacha el listener global para nuevos botones
document.querySelectorAll(".btn-show-history").forEach(btn => {
  btn.onclick = (e) => {
    e.preventDefault();
    openHistorialModal();
  };
});


  console.log("HTML generado:", contenedor.innerHTML.slice(0, 200) + "..."); // Log 6: Ver el HTML generado
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
      const okLoc = !l || it.dataset.ubicacion.includes(l);
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
            ${info("Cantidad", `${m.cantidad} unidades`)}
            ${info("Ubicación", m.ubicacion)}
            ${info("Usuario", m.usuario_nombre)}
            ${info("RUT", m.rut_usuario)}
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
                            <span class="material-symbols-outlined text-[14px] ${r.tipo_evento === "Añadir" ? "text-green-600 dark:text-green-400" :
        r.tipo_evento === "Retirar" ? "text-red-600 dark:text-red-400" :
          "text-blue-600 dark:text-blue-400"
      }">${r.tipo_evento === "Añadir" ? "south" :
        r.tipo_evento === "Retirar" ? "north" :
          "sync_alt"
      }</span>
                            ${r.tipo_evento} • ${r.cantidad} unidades • ${r.usuario_nombre}
                        </span>
                        <span class="text-[11px] text-neutral-600 dark:text-[var(--text-muted-dark)]">
                            ${String(r.timestamp).split(" ")[1]}
                        </span>
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

  // --- Modal de Nuevo Movimiento ---
  const modal = document.getElementById("modal-new-mov");
  const btnNew = document.getElementById("btn-new-mov");
  const form = document.getElementById("form-new-mov");

  // Abrir modal
  btnNew?.addEventListener("click", () => {
    modal?.classList.remove("hidden");
    cargarProductosYEstantes();
  });

  // Cerrar modal
  modal?.querySelectorAll(".close-modal").forEach(btn => {
    btn.addEventListener("click", () => modal.classList.add("hidden"));
  });

  // Evitar cierre al hacer click dentro del modal
  modal?.querySelector("div > div").addEventListener("click", e => e.stopPropagation());

  // Cerrar al hacer click fuera
  modal?.addEventListener("click", e => {
    if (e.target === modal) modal.classList.add("hidden");
  });

  // Función para cargar productos y estantes
  function cargarProductosYEstantes() {
    const tipoMovimiento = form.querySelector("[name=tipo_evento]").value;
    const estanteDiv = form.querySelector("[name=id_estante]").closest("div");
    const estanteNuevoDiv = document.getElementById("estante-nuevo-div");

    // Ocultar/mostrar campos según tipo de movimiento
    if (tipoMovimiento === "Mover") {
      estanteDiv.classList.remove("hidden");
      if (!estanteNuevoDiv) {
        const div = document.createElement("div");
        div.id = "estante-nuevo-div";
        div.innerHTML = `
                <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">Estante Nuevo</label>
                <select name="id_estante_nuevo" required class="w-full rounded-lg border border-neutral-300 dark:border-[var(--border-dark)] bg-white dark:bg-[var(--card-bg-dark)] px-3 py-2 text-sm">
                </select>
            `;
        estanteDiv.parentNode.insertBefore(div, estanteDiv.nextSibling);
      }
    } else {
      estanteDiv.classList.remove("hidden");
      estanteNuevoDiv?.remove();
    }

    // Cargar datos
    Promise.all([
      fetch("/api/productos").then(r => r.json()),
      fetch("/api/estantes").then(r => r.json())
    ]).then(([productos, estantes]) => {
      // Obtener el select de productos
      const selectProductos = form.querySelector("[name=idproducto]");
      if (!selectProductos) {
        console.error("No se encontró el select de productos");
        return;
      }

      // Llenar select de productos
      selectProductos.innerHTML = productos.map(p =>
        `<option value="${p.idproducto}">${p.nombre} (Stock: ${p.stock || 0} unidades)</option>`
      ).join("");

      // Llenar select de estantes
      const selectEstantes = form.querySelector("[name=id_estante]");
      if (!selectEstantes) {
        console.error("No se encontró el select de estantes");
        return;
      }

      selectEstantes.innerHTML = estantes.map(e =>
        `<option value="${e.id_estante}">${e.nombre || `Estante ${e.id_estante}`}</option>`
      ).join("");

      // Si es movimiento, llenar el segundo select de estantes
      if (tipoMovimiento === "Mover") {
        const selectEstanteNuevo = form.querySelector("[name=id_estante_nuevo]");
        if (selectEstanteNuevo) {
          selectEstanteNuevo.innerHTML = selectEstantes.innerHTML;
        }
      }
    }).catch(error => {
      console.error("Error cargando datos:", error);
    });
  }

  // Agregar event listener para cambios en tipo de movimiento
  form?.querySelector("[name=tipo_evento]").addEventListener("change", cargarProductosYEstantes);

  // Manejar envío del formulario
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();

    try {
      // Obtener los datos del formulario y validarlos
      const formData = new FormData(form);
      const datos = {};

      // Convertir y validar cada campo
      datos.tipo_evento = formData.get("tipo_evento");
      datos.idproducto = parseInt(formData.get("idproducto"));
      datos.id_estante = parseInt(formData.get("id_estante"));
      datos.cantidad = parseInt(formData.get("cantidad"));
      datos.observacion = formData.get("observacion") || "";

      // Validar que los campos numéricos sean válidos
      if (isNaN(datos.idproducto) || isNaN(datos.id_estante) || isNaN(datos.cantidad)) {
        throw new Error("Los campos numéricos son inválidos");
      }

      // Si es movimiento entre estantes
      if (datos.tipo_evento === "Mover" && formData.get("id_estante_nuevo")) {
        datos.estante_origen = datos.id_estante;
        datos.id_estante = parseInt(formData.get("id_estante_nuevo"));
      }

      console.log("Datos a enviar:", datos); // Para debugging

      const response = await fetch("/api/movimientos/nuevo", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(datos)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Error al guardar el movimiento");
      }

      const result = await response.json();

      // Mostrar mensaje de éxito
      alert(result.mensaje || "Movimiento registrado correctamente");

      // Cerrar el modal
      const modal = document.getElementById("modal-new-mov");
      modal?.classList.add("hidden");

      // Recargar la página
      window.location.reload();

    } catch (error) {
      console.error("Error detallado:", error);
      alert("Error al registrar el movimiento: " + error.message);
    }
  });

  // --- Estado inicial ---
  resetDetalle();
  applyFilters();
});
document.addEventListener("click", (e) => {
  const btn = e.target.closest("#btn-show-history");
  if (btn) {
    window.location.href = "/historial"; // Cambia por tu endpoint real
  }
});
