// ===============================================================
//  AUDITORÍA · TERMINAL + LIVE TRAIL
// ===============================================================
(() => {
  const API_LOGS = "/api/auditoria/logs";
  const API_LIVE = "/api/auditoria/live-trail";
  const API_EXPORT = "/api/auditoria/export";
  const API_RECALIBRAR = "/api/auditoria/recalibrar";

  const REFRESH_INTERVAL = 45000;

  // -----------------------------------------------------------
  //  ELEMENTOS
  // -----------------------------------------------------------
  const el = {
    terminal: document.getElementById("audit-terminal-output"),
    search: document.getElementById("audit-log-search"),
    runQuery: document.getElementById("audit-run-query"),
    filters: document.getElementById("audit-active-filters"),
    logStream: document.getElementById("audit-log-stream"),
    empty: document.getElementById("audit-log-empty"),
    streamStatus: document.getElementById("audit-stream-status"),
    lastUpdated: document.getElementById("audit-last-updated"),
    mem: document.getElementById("audit-mem-usage"),
    cpu: document.getElementById("audit-cpu-usage"),
    latency: document.getElementById("audit-latency"),
    exportCsv: document.getElementById("audit-export-csv"),
    exportCsvFooter: document.getElementById("audit-export-csv-footer"),
    exportZip: document.getElementById("audit-export-zip"),
    exportPdf: document.getElementById("audit-export-pdf"),
    recalibrate: document.getElementById("audit-recalibrate"),
    clearFilters: document.getElementById("audit-clear-filters"),
  };
  
  let state = {
    filtros: {},
    logs: [],
  };

  // ===========================================================
  //  NORMALIZADORES
  // ===========================================================
  const sev = {
    info: { label: "INFO", class: "text-green-400" },
    warning: { label: "WARN", class: "text-yellow-400" },
    critical: { label: "CRIT", class: "text-red-500" },
    error: { label: "CRIT", class: "text-red-500" },
  };

  function normalize(entry) {
    const fecha = entry.fecha || entry.timestamp.slice(0, 10);
    const hora = entry.hora || entry.timestamp.slice(11, 19);
    const nivel = (entry.severidad || "info").toLowerCase();
    const preset = sev[nivel] || sev.info;

    return {
      id: entry.id,
      fecha,
      hora,
      mensaje: entry.mensaje,
      usuario: entry.usuario,
      producto: entry.producto,
      estante: entry.estante,
      tipo_evento: entry.tipo_evento,
      nivel: preset.label,
      nivelClass: preset.class,
    };
  }

  // ===========================================================
  //  TERMINAL SUPERIOR
  // ===========================================================
  function pushTerminal(msg) {
      if (!el.terminal) return;
      const p = document.createElement("p");
      p.textContent = msg;
      el.terminal.appendChild(p);
      el.terminal.scrollTop = el.terminal.scrollHeight;
  }

  // ===========================================================
  //  LIVE AUDIT TRAIL (LISTA INFERIOR)
  // ===========================================================
  function renderLogs() {
      const cont = el.logStream;
      if (!cont) return;

      cont.innerHTML = "";

      if (!state.logs.length) {
          el.empty.classList.remove("hidden");
          return;
      }

      el.empty.classList.add("hidden");

      const ordered = [...state.logs].reverse();

      ordered.forEach(log => {
          const hora = log.hora || "--:--:--";
          const msg = resumirMensaje(log.mensaje);

          let badgeColor = "var(--log-info)";
          if (log.nivel === "WARN") badgeColor = "var(--log-warn)";
          if (log.nivel === "CRIT") badgeColor = "var(--log-crit)";

          const item = document.createElement("p");
          item.className = "flex items-center gap-3 whitespace-nowrap";

          item.innerHTML = `
              <span style="color:var(--text-muted-dark);" class="dark:text-[var(--text-muted-light)]">${hora}</span>

              <span class="px-2 py-[2px] text-xs rounded font-medium"
                  style="background-color: color-mix(in srgb, ${badgeColor} 15%, transparent);
                        color: ${badgeColor};">
                  ${log.nivel}
              </span>

              <span>${msg}</span>
          `;

          cont.appendChild(item);
      });

      cont.scrollTop = cont.scrollHeight;
  }



  function logColor(level) {
  const l = level.toUpperCase();
  if (l === "INFO")  return "text-[var(--log-info-light)] dark:text-[var(--log-info-dark)]";
  if (l === "WARN")  return "text-[var(--log-warn-light)] dark:text-[var(--log-warn-dark)]";
  if (l === "CRIT")  return "text-[var(--log-crit-light)] dark:text-[var(--log-crit-dark)]";
  return "text-[var(--log-text-light)] dark:text-[var(--log-text-dark)]";
}

function renderLogs() {
  const cont = el.logStream;
  if (!cont) return;

  cont.innerHTML = "";

  if (!state.logs.length) {
    el.empty.classList.remove("hidden");
    return;
  }

  el.empty.classList.add("hidden");

  // Mostrar newest ↓ abajo
  const ordered = [...state.logs].reverse();

  ordered.forEach((log) => {
    let msg = log.mensaje || "";
    if (msg.length > 70) msg = msg.slice(0, 70) + "…";

    const line = document.createElement("div");
    line.className =
      "text-sm font-mono whitespace-pre leading-[1.4] flex gap-2";

    line.innerHTML = `
      <span class="opacity-60">${log.hora}</span>
      <span class="${logColor(log.nivel)} font-bold">[${log.nivel}]</span>
      <span>${msg}</span>
    `;

    cont.appendChild(line);
  });

  cont.scrollTop = cont.scrollHeight;
}

  function resumirMensaje(msg) {
    if (!msg) return "";

    const lower = msg.toLowerCase();

    // Resumen por patrones comunes
    if (lower.includes("flujo en piso bajo")) {
        return "Flujo bajo en estantes. Inactividad prolongada.";
    }
    if (lower.includes("peso") && lower.includes("lectura")) {
        return "Discrepancia en lectura de peso detectada.";
    }
    if (lower.includes("venta")) {
        return "Venta registrada.";
    }
    if (lower.includes("retiro")) {
        return "Movimiento de retiro ejecutado.";
    }
    if (lower.includes("error")) {
        return "Error del sistema detectado.";
    }

    // Si no es ningún caso especial → recorte clásico
    return msg.length > 90 ? msg.slice(0, 90) + "…" : msg;
}

  // ===========================================================
  //  CARGA DE LOGS
  // ===========================================================
  async function loadLogs() {
    pushTerminal("Sincronizando eventos…");

    const params = new URLSearchParams(state.filtros).toString();
    const url = params ? `${API_LOGS}?${params}` : API_LOGS;

    try {
      const res = await fetch(url);
      const data = await res.json();

      if (!data.ok) {
        pushTerminal("Error cargando eventos.");
        return;
      }

      state.logs = data.logs.map(normalize);

      if (data.meta?.system) {
        el.mem.textContent = data.meta.system.mem;
        el.cpu.textContent = data.meta.system.cpu;
        el.latency.textContent = data.meta.system.latency;
      }

      el.lastUpdated.textContent = "Actualizado";

      renderLogs();
    } catch (err) {
      pushTerminal("Fallo conexión backend.");
    }
  }

  // ===========================================================
  //  FILTROS
  // ===========================================================
  function applySearch() {
    const q = el.search.value.trim();
    if (q) state.filtros.search = q;
    else delete state.filtros.search;

    renderFilterChips();
    loadLogs();
  }

  function renderFilterChips() {
    const box = el.filters;
    if (!box) return;

    box.innerHTML = "";

    Object.entries(state.filtros).forEach(([k, v]) => {
      if (!v) return;
      const chip = document.createElement("span");
      chip.className =
        "px-2 py-1 bg-primary/20 border border-primary/40 text-primary text-xs rounded-full flex items-center gap-1";

      chip.innerHTML = `
        ${k}: ${v}
        <button class="material-symbols-outlined text-xs text-primary">close</button>
      `;

      chip.querySelector("button").onclick = () => {
        delete state.filtros[k];
        renderFilterChips();
        loadLogs();
      };

      box.appendChild(chip);
    });
  }

  // ===========================================================
  //  EXPORTACIONES
  // ===========================================================
  async function exportFormato(formato) {
    pushTerminal(`Exportando en formato ${formato}…`);

    const payload = {
      formato,
      filtros: state.filtros,
      limit: 600,
    };

    const res = await fetch(API_EXPORT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `auditoria.${formato}`;
    a.click();

    URL.revokeObjectURL(url);
  }

  // ===========================================================
  //  RECALIBRAR
  // ===========================================================
  async function recalibrarSensores() {
    pushTerminal("Enviando secuencia de recalibración…");

    const res = await fetch(API_RECALIBRAR, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ detalle: "Recalibración solicitada desde UI" }),
    });

    const data = await res.json();
    pushTerminal(data.mensaje || "Recalibrado.");
    loadLogs();
  }

  // ===========================================================
  //  EVENTOS
  // ===========================================================
  if (el.runQuery) el.runQuery.onclick = applySearch;
  if (el.search) el.search.onkeydown = (e) => e.key === "Enter" && applySearch();

  if (el.clearFilters)
    el.clearFilters.onclick = () => {
      state.filtros = {};
      renderFilterChips();
      loadLogs();
    };

  if (el.exportCsv) el.exportCsv.onclick = () => exportFormato("csv");
  if (el.exportCsvFooter) el.exportCsvFooter.onclick = () => exportFormato("csv");
  if (el.exportZip) el.exportZip.onclick = () => exportFormato("zip");
  if (el.exportPdf) el.exportPdf.onclick = () => exportFormato("pdf");

  if (el.recalibrate) el.recalibrate.onclick = recalibrarSensores;

  // ===========================================================
  //  ARRANQUE
  // ===========================================================
  loadLogs();
  setInterval(loadLogs, REFRESH_INTERVAL);
})();
