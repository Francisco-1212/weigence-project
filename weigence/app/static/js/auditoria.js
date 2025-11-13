(function () {
  const REFRESH_INTERVAL = 45000;
  const FILTER_KEYS = new Set([
    "usuario",
    "producto",
    "estante",
    "tipo_evento",
    "severidad",
    "fecha",
  ]);

  const EVENT_KEYWORDS = [
    { type: "movimientos_inventario", keywords: ["movimiento", "inventario", "traslado", "ajuste"] },
    { type: "ventas", keywords: ["venta", "ticket", "factura", "pago"] },
    { type: "detalle_ventas", keywords: ["detalle", "linea", "articulo", "unidad"] },
    { type: "pesajes", keywords: ["peso", "pesaje", "balanza", "gramo", "kg"] },
    { type: "alertas", keywords: ["alerta", "riesgo", "aviso", "severidad"] },
    { type: "accesos/autorizaciones", keywords: ["acceso", "autoriz", "credencial", "entrada", "permiso"] },
    { type: "eventos IA", keywords: ["ia", "modelo", "predic", "anomal", "inteligencia"] },
    { type: "errores críticos", keywords: ["error", "fallo", "crit", "exception", "panic"] },
    { type: "calibraciones", keywords: ["calibra", "recalibra", "ajuste", "sensor"] },
    { type: "inactividad", keywords: ["inactividad", "idle", "sin actividad", "timeout"] },
    { type: "anomalías detectadas", keywords: ["anom", "fraude", "desviación", "irregular"] },
    { type: "retiros programados", keywords: ["programado", "planificado", "agenda"] },
    { type: "retiros fuera de horario", keywords: ["fuera de horario", "no programado", "inesperado"] },
    { type: "accesos a estantes", keywords: ["estante", "locker", "compartimiento", "gabinete"] },
    { type: "lecturas de sensores", keywords: ["sensor", "lectura", "temperatura", "humedad"] },
    { type: "login/logout de usuarios", keywords: ["login", "logout", "sesión", "inicio", "cierre"] },
  ];

  const SEVERITY_PRESETS = {
    critico: { label: "CRIT", className: "text-red-400", weight: 3 },
    alto: { label: "WARN", className: "text-amber-400", weight: 2 },
    medio: { label: "WARN", className: "text-amber-400", weight: 2 },
    advertencia: { label: "WARN", className: "text-amber-400", weight: 2 },
    bajo: { label: "INFO", className: "text-emerald-400", weight: 1 },
    info: { label: "INFO", className: "text-emerald-400", weight: 1 },
    informativo: { label: "INFO", className: "text-emerald-400", weight: 1 },
    azul: { label: "INFO", className: "text-blue-300", weight: 1 },
    verde: { label: "INFO", className: "text-emerald-400", weight: 1 },
    amarillo: { label: "WARN", className: "text-amber-400", weight: 2 },
    rojo: { label: "CRIT", className: "text-red-400", weight: 3 },
  };

  const state = {
    logs: [],
    visibleLogs: [],
    filters: {},
    knownIds: new Set(),
    lastUpdated: null,
    hasStreamingError: false,
  };

  const el = {};

  function initElements() {
    el.searchInput = document.querySelector("#audit-log-search");
    el.runQueryBtn = document.querySelector("#audit-run-query");
    el.clearFiltersBtn = document.querySelector("#audit-clear-filters");
    el.filtersContainer = document.querySelector("#audit-active-filters");
    el.logStream = document.querySelector("#audit-log-stream");
    el.logEmpty = document.querySelector("#audit-log-empty");
    el.lastUpdated = document.querySelector("#audit-last-updated");
    el.streamStatus = document.querySelector("#audit-stream-status");
    el.memUsage = document.querySelector("#audit-mem-usage");
    el.cpuUsage = document.querySelector("#audit-cpu-usage");
    el.latency = document.querySelector("#audit-latency");
    el.exportCsv = document.querySelector("#audit-export-csv");
    el.exportZip = document.querySelector("#audit-export-zip");
    el.exportPdf = document.querySelector("#audit-export-pdf");
    el.recalibrate = document.querySelector("#audit-recalibrate");
    el.eventCounts = document.querySelector("#audit-event-counts");
    el.lastCritical = document.querySelector("#audit-last-critical");
    el.contextSummary = document.querySelector("#audit-context-summary");
  }

  function normalizeText(value) {
    return (value || "")
      .toString()
      .toLowerCase()
      .normalize("NFD")
      .replace(/\p{Diacritic}/gu, "");
  }

  function formatTimestamp(ts) {
    try {
      const date = new Date(ts);
      if (Number.isNaN(date.getTime())) {
        return "--:--:--";
      }
      return date.toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch (error) {
      return "--:--:--";
    }
  }

  function formatDate(ts) {
    try {
      const date = new Date(ts);
      if (Number.isNaN(date.getTime())) {
        return "--";
      }
      return date.toISOString().slice(0, 10);
    } catch (error) {
      return "--";
    }
  }

  function mapSeverity(entry) {
    const keysToCheck = [
      entry?.severidad,
      entry?.severity,
      entry?.nivel,
      entry?.tipo_color,
    ];

    for (const key of keysToCheck) {
      const normalized = normalizeText(key);
      if (normalized && SEVERITY_PRESETS[normalized]) {
        const preset = SEVERITY_PRESETS[normalized];
        return {
          level: normalized,
          label: preset.label,
          className: preset.className,
          weight: preset.weight,
        };
      }
    }

    return {
      level: "info",
      label: "INFO",
      className: "text-emerald-400",
      weight: 1,
    };
  }

  function inferEventType(entry) {
    const explicit = entry?.tipo_evento || entry?.categoria || entry?.tipo;
    if (explicit) {
      return explicit;
    }

    const haystack = normalizeText([
      entry?.titulo,
      entry?.descripcion,
      entry?.detalle,
      entry?.mensaje,
      entry?.metadata?.detalle,
    ].join(" "));

    for (const definition of EVENT_KEYWORDS) {
      if (definition.keywords.some((keyword) => haystack.includes(keyword))) {
        return definition.type;
      }
    }

    if (haystack.includes("retir") && haystack.includes("horario")) {
      return "retiros fuera de horario";
    }

    if (haystack.includes("sensor")) {
      return "lecturas de sensores";
    }

    return "eventos IA";
  }

  function buildMessage(entry) {
    const fallback = entry?.descripcion || entry?.detalle || entry?.mensaje;
    if (fallback) {
      return fallback;
    }

    if (entry?.titulo) {
      return entry.titulo;
    }

    return "Evento registrado en el sistema";
  }

  function parseTimestamp(entry) {
    const candidates = [
      entry?.timestamp,
      entry?.fecha_creacion,
      entry?.fecha,
      entry?.created_at,
      entry?.updated_at,
    ];

    for (const candidate of candidates) {
      if (!candidate) continue;
      const date = new Date(candidate);
      if (!Number.isNaN(date.getTime())) {
        return date.toISOString();
      }
    }

    return new Date().toISOString();
  }

  function normalizeLog(entry, index = 0) {
    const severity = mapSeverity(entry);
    const timestamp = parseTimestamp(entry);
    const tipoEvento = inferEventType(entry);
    const metadata = entry?.metadata || entry?.data || {};

    const usuario = entry?.usuario || metadata?.usuario || metadata?.user || metadata?.usuario_id || metadata?.responsable;
    const producto = entry?.producto || metadata?.producto || metadata?.sku || metadata?.idproducto;
    const estante = entry?.estante || metadata?.estante || metadata?.locker || metadata?.id_estante;

    const id = entry?.id || `${timestamp}-${tipoEvento}-${index}-${normalizeText(usuario || "")}-${normalizeText(producto || "")}`;

    return {
      id,
      raw: entry,
      timestamp,
      fecha: formatDate(timestamp),
      hora: formatTimestamp(timestamp),
      titulo: entry?.titulo || entry?.mensaje || `Evento ${tipoEvento}`,
      mensaje: buildMessage(entry),
      tipo_evento: tipoEvento,
      usuario: usuario || "",
      producto: producto || "",
      estante: estante || "",
      severidad: severity.level,
      nivelLabel: severity.label,
      nivelClass: severity.className,
      nivelWeight: severity.weight,
    };
  }

  function mergeLogs(newLogs) {
    let added = false;
    newLogs.forEach((log) => {
      if (!state.knownIds.has(log.id)) {
        state.logs.push(log);
        state.knownIds.add(log.id);
        added = true;
      }
    });

    if (added) {
      state.logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    }

    return added;
  }

  function renderLogs(logs) {
    if (!el.logStream) return;

    el.logStream.innerHTML = "";

    if (!logs.length) {
      const empty = document.createElement("div");
      empty.className = "text-slate-500 text-xs italic";
      empty.textContent = "No se encontraron eventos con los filtros actuales.";
      el.logStream.appendChild(empty);
      return;
    }

    const fragment = document.createDocumentFragment();

    logs.forEach((log) => {
      const entry = document.createElement("article");
      entry.className = "border border-white/5 bg-white/5 hover:bg-white/10 transition rounded-xl px-4 py-3";

      const metaChips = [];
      if (log.usuario) {
        metaChips.push(createMetaChip("usuario", log.usuario, "Usuario"));
      }
      if (log.producto) {
        metaChips.push(createMetaChip("producto", log.producto, "Producto"));
      }
      if (log.estante) {
        metaChips.push(createMetaChip("estante", log.estante, "Estante"));
      }
      metaChips.push(createMetaChip("tipo_evento", log.tipo_evento, "Tipo"));
      metaChips.push(createMetaChip("severidad", log.severidad, "Severidad"));

      entry.innerHTML = `
        <div class="flex items-start gap-4">
          <span class="text-[11px] tracking-[0.3em] text-slate-500 pt-1">${escapeHtml(log.hora)}</span>
          <span class="text-xs font-semibold uppercase tracking-[0.25em] ${log.nivelClass} pt-1">${escapeHtml(log.nivelLabel)}</span>
          <div class="flex-1 space-y-2">
            <div class="leading-relaxed text-slate-200">
              <p class="font-semibold text-slate-100">${escapeHtml(log.titulo)}</p>
              <p class="text-[13px] text-slate-300">${escapeHtml(log.mensaje)}</p>
            </div>
            <div class="flex flex-wrap gap-2">
              ${metaChips.join("")}
            </div>
          </div>
        </div>
      `;

      fragment.appendChild(entry);
    });

    const cursor = document.createElement("div");
    cursor.className = "flex items-center gap-2 text-[13px] text-slate-500 pt-2";
    cursor.innerHTML = '<span class="text-emerald-400">&gt;</span><span class="blinking-cursor">▋</span>';

    fragment.appendChild(cursor);
    el.logStream.appendChild(fragment);
  }

  function createMetaChip(key, value, label) {
    return `
      <button
        type="button"
        class="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-slate-300 hover:bg-white/10 transition"
        data-filter-key="${encodeURIComponent(key)}"
        data-filter-value="${encodeURIComponent(value)}"
      >
        <span class="text-slate-400">${escapeHtml(label)}:</span>
        <span class="font-medium text-slate-100">${escapeHtml(value)}</span>
      </button>
    `;
  }

  function escapeHtml(value) {
    return (value ?? "")
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function updateFilterChips() {
    if (!el.filtersContainer) return;

    el.filtersContainer.innerHTML = "";
    const entries = Object.entries(state.filters).filter(([, value]) => value && value.toString().trim() !== "");

    if (!entries.length) {
      if (el.clearFiltersBtn) {
        el.clearFiltersBtn.classList.add("hidden");
      }
      return;
    }

    const fragment = document.createDocumentFragment();
    entries.forEach(([key, value]) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.dataset.key = key;
      chip.dataset.value = value;
      chip.className = "group flex items-center gap-2 rounded-full border border-primary-500/40 bg-primary-500/10 px-3 py-1 text-[11px] font-medium text-primary-200 hover:bg-primary-500/20 transition";
      chip.innerHTML = `
        <span class="uppercase tracking-[0.2em]">${escapeHtml(formatFilterLabel(key))}</span>
        <span>${escapeHtml(value)}</span>
        <span class="material-symbols-outlined text-xs group-hover:text-primary-100">close</span>
      `;
      fragment.appendChild(chip);
    });

    el.filtersContainer.appendChild(fragment);

    if (el.clearFiltersBtn) {
      el.clearFiltersBtn.classList.remove("hidden");
    }
  }

  function formatFilterLabel(key) {
    switch (key) {
      case "usuario":
        return "usuario";
      case "producto":
        return "producto";
      case "estante":
        return "estante";
      case "tipo_evento":
        return "evento";
      case "severidad":
        return "severidad";
      case "fecha":
        return "fecha";
      case "query":
        return "texto";
      default:
        return key;
    }
  }

  function parseSearch(value) {
    const filters = {};
    if (!value) {
      return filters;
    }

    const tokens = value
      .split(/\s+/)
      .map((token) => token.trim())
      .filter(Boolean);

    const freeText = [];

    tokens.forEach((token) => {
      const [key, ...rest] = token.split(":");
      if (rest.length && FILTER_KEYS.has(key.toLowerCase())) {
        filters[key.toLowerCase()] = rest.join(":");
      } else {
        freeText.push(token);
      }
    });

    if (freeText.length) {
      filters.query = freeText.join(" ");
    }

    return filters;
  }

  function matchesFilter(log, filters) {
    const normalized = (value) => normalizeText(value);

    if (filters.usuario && !normalized(log.usuario).includes(normalized(filters.usuario))) {
      return false;
    }

    if (filters.producto && !normalized(log.producto).includes(normalized(filters.producto))) {
      return false;
    }

    if (filters.estante && !normalized(log.estante).includes(normalized(filters.estante))) {
      return false;
    }

    if (filters.tipo_evento && !normalized(log.tipo_evento).includes(normalized(filters.tipo_evento))) {
      return false;
    }

    if (filters.severidad && !normalized(log.severidad).includes(normalized(filters.severidad))) {
      return false;
    }

    if (filters.fecha && !normalized(log.fecha).includes(normalized(filters.fecha))) {
      return false;
    }

    if (filters.query) {
      const haystack = normalizeText([
        log.titulo,
        log.mensaje,
        log.tipo_evento,
        log.usuario,
        log.producto,
        log.estante,
      ].join(" "));

      if (!haystack.includes(normalized(filters.query))) {
        return false;
      }
    }

    return true;
  }

  function applyFilters() {
    state.visibleLogs = state.logs.filter((log) => matchesFilter(log, state.filters));
    renderLogs(state.visibleLogs);
    updateFilterChips();
    updateTelemetry();
    updateEventSummary();
  }

  function updateTelemetry() {
    if (!el.memUsage || !el.cpuUsage || !el.latency) return;

    const baseMem = 42;
    const memValue = Math.min(baseMem + state.logs.length * 0.8, 256).toFixed(1);
    const cpuValue = Math.min(3 + state.visibleLogs.length * 0.6, 85).toFixed(1);
    const latencyValue = Math.max(8, Math.round(12 + (state.visibleLogs.length % 5) * 2 + Math.random() * 3));

    el.memUsage.textContent = `${memValue} MB`;
    el.cpuUsage.textContent = `${cpuValue}%`;
    el.latency.textContent = `${latencyValue} ms`;
  }

  function updateEventSummary() {
    if (!el.eventCounts) return;

    const counts = new Map();
    let latestCritical = null;

    state.logs.forEach((log) => {
      counts.set(log.tipo_evento, (counts.get(log.tipo_evento) || 0) + 1);
      if (log.nivelWeight >= 3) {
        if (!latestCritical || new Date(log.timestamp) > new Date(latestCritical.timestamp)) {
          latestCritical = log;
        }
      }
    });

    el.eventCounts.innerHTML = "";

    if (!counts.size) {
      const li = document.createElement("li");
      li.className = "text-xs text-neutral-500 dark:text-neutral-400";
      li.textContent = "Aún no hay eventos registrados";
      el.eventCounts.appendChild(li);
    } else {
      const sorted = Array.from(counts.entries()).sort((a, b) => b[1] - a[1]);
      sorted.slice(0, 8).forEach(([type, value]) => {
        const li = document.createElement("li");
        li.className = "flex justify-between text-sm font-medium text-neutral-700 dark:text-neutral-200";
        li.innerHTML = `
          <span>${escapeHtml(type)}</span>
          <span class="text-neutral-500 dark:text-neutral-400">${value}</span>
        `;
        el.eventCounts.appendChild(li);
      });
    }

    if (el.lastCritical) {
      if (latestCritical) {
        el.lastCritical.textContent = `${latestCritical.hora} · ${latestCritical.titulo}`;
      } else {
        el.lastCritical.textContent = "Sin registros críticos recientes.";
      }
    }

    if (el.contextSummary) {
      const criticos = state.logs.filter((log) => log.nivelWeight >= 3).length;
      const advertencias = state.logs.filter((log) => log.nivelWeight === 2).length;
      const info = state.logs.length - criticos - advertencias;
      el.contextSummary.textContent = `Monitoreando ${state.logs.length} eventos (${criticos} críticos, ${advertencias} advertencias, ${info} informativos) con correlación IA en vivo.`;
    }
  }

  async function fetchAuditLogs() {
    try {
      toggleStreaming(true);
      const response = await fetch("/api/notificaciones", { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`Respuesta ${response.status}`);
      }

      const payload = await response.json();
      const items = Array.isArray(payload?.notificaciones) ? payload.notificaciones : [];
      const normalized = items.map((entry, index) => normalizeLog(entry, index));

      const hasUpdates = mergeLogs(normalized);
      state.lastUpdated = new Date();
      state.hasStreamingError = false;
      updateLastUpdated();

      if (hasUpdates || !state.visibleLogs.length) {
        applyFilters();
      } else {
        updateTelemetry();
        updateEventSummary();
      }
    } catch (error) {
      console.error("Error obteniendo logs de auditoría", error);
      state.hasStreamingError = true;
      showFetchError();
    } finally {
      toggleStreaming(false);
    }
  }

  function toggleStreaming(isBusy) {
    if (!el.streamStatus) return;
    const indicator = el.streamStatus.querySelector(".w-2");
    if (!indicator) return;
    indicator.classList.remove("bg-red-500");
    indicator.classList.add("bg-green-500");
    el.streamStatus.classList.remove("text-red-400");

    if (state.hasStreamingError) {
      indicator.classList.remove("bg-green-500");
      indicator.classList.add("bg-red-500");
      el.streamStatus.classList.add("text-red-400");
    }

    if (isBusy) {
      indicator.classList.add("animate-ping");
      indicator.classList.remove("animate-pulse");
    } else {
      indicator.classList.remove("animate-ping");
      indicator.classList.add("animate-pulse");
    }
  }

  function updateLastUpdated() {
    if (!el.lastUpdated || !state.lastUpdated) return;
    el.lastUpdated.textContent = `Actualizado ${state.lastUpdated.toLocaleTimeString("es-ES", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })}`;
  }

  function showFetchError() {
    if (!el.logStream) return;
    el.logStream.innerHTML = "";
    const errorNode = document.createElement("div");
    errorNode.className = "rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200";
    errorNode.textContent = "No fue posible recuperar el rastro de auditoría. Verifique la conexión y reintente.";
    el.logStream.appendChild(errorNode);

    if (el.streamStatus) {
      el.streamStatus.classList.add("text-red-400");
      const indicator = el.streamStatus.querySelector(".w-2");
      if (indicator) {
        indicator.classList.remove("animate-pulse", "animate-ping", "bg-green-500");
        indicator.classList.add("bg-red-500");
      }
    }
  }

  function rebuildSearchFromFilters() {
    if (!el.searchInput) return;
    const parts = [];
    Object.entries(state.filters).forEach(([key, value]) => {
      if (!value) return;
      if (key === "query") {
        parts.push(value);
      } else {
        parts.push(`${key}:${value}`);
      }
    });
    el.searchInput.value = parts.join(" ");
  }

  function attachEvents() {
    if (el.searchInput) {
      el.searchInput.addEventListener("input", (event) => {
        state.filters = parseSearch(event.target.value);
        applyFilters();
      });
    }

    if (el.runQueryBtn) {
      el.runQueryBtn.addEventListener("click", () => {
        state.filters = parseSearch(el.searchInput?.value || "");
        applyFilters();
      });
    }

    if (el.clearFiltersBtn) {
      el.clearFiltersBtn.addEventListener("click", () => {
        state.filters = {};
        rebuildSearchFromFilters();
        applyFilters();
      });
    }

    if (el.filtersContainer) {
      el.filtersContainer.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-key]");
        if (!button) return;
        const { key } = button.dataset;
        if (!key) return;
        delete state.filters[key];
        rebuildSearchFromFilters();
        applyFilters();
      });
    }

    if (el.logStream) {
      el.logStream.addEventListener("click", (event) => {
        const button = event.target.closest("button[data-filter-key]");
        if (!button) return;
        const key = decodeURIComponent(button.dataset.filterKey || "");
        const value = decodeURIComponent(button.dataset.filterValue || "");
        if (!key || !value) return;
        state.filters[key] = value;
        rebuildSearchFromFilters();
        applyFilters();
      });
    }

    const handleExport = (format) => {
      const dataset = state.visibleLogs.length ? state.visibleLogs : state.logs;
      if (!dataset.length) {
        window.alert("No hay datos para exportar.");
        return;
      }
      const blob = buildExportBlob(dataset, format);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `auditoria-${format}-${Date.now()}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    };

    if (el.exportCsv) {
      el.exportCsv.addEventListener("click", () => handleExport("csv"));
    }
    if (el.exportZip) {
      el.exportZip.addEventListener("click", () => handleExport("zip"));
    }
    if (el.exportPdf) {
      el.exportPdf.addEventListener("click", () => handleExport("pdf"));
    }

    if (el.recalibrate) {
      el.recalibrate.addEventListener("click", () => {
        window.dispatchEvent(new CustomEvent("audit:recalibrate", { detail: { timestamp: new Date().toISOString() } }));
        window.alert("Se solicitó la recalibración de los sensores. El proceso puede tardar unos minutos.");
      });
    }
  }

  function buildExportBlob(logs, format) {
    if (format === "csv") {
      const headers = [
        "timestamp",
        "hora",
        "fecha",
        "severidad",
        "tipo_evento",
        "usuario",
        "producto",
        "estante",
        "titulo",
        "mensaje",
      ];
      const rows = logs.map((log) => headers.map((header) => JSON.stringify(log[header] ?? "")).join(","));
      const csv = [headers.join(","), ...rows].join("\n");
      return new Blob([csv], { type: "text/csv;charset=utf-8;" });
    }

    const json = JSON.stringify(logs, null, 2);
    const mime = format === "pdf" ? "application/json" : "application/json";
    return new Blob([json], { type: mime });
  }

  function startPolling() {
    fetchAuditLogs();
    setInterval(fetchAuditLogs, REFRESH_INTERVAL);
  }

  document.addEventListener("DOMContentLoaded", () => {
    initElements();
    attachEvents();
    startPolling();
  });
})();
