(function () {
  async function openHistorialModal() {
    const html = await fetch("/historial", { cache: "no-store" }).then(r => r.text());
    const wrap = document.createElement("div");
    wrap.innerHTML = html.trim();
    const modal = wrap.firstElementChild;
    if (!modal || modal.id !== "historial-modal") return;
    document.body.appendChild(modal);
    initModal(modal);
  }

  function initModal(root) {
    // --- cierre modal
    const close = () => root.remove();
    root.querySelector("[data-close]")?.addEventListener("click", close);
    root.addEventListener("click", (e) => { if (e.target === root) close(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });

    // --- tabs
    const tabs = root.querySelectorAll(".tab-btn");
    const panels = { mov: root.querySelector("#panel-mov"), err: root.querySelector("#panel-err") };
    const setActive = (key) => {
      tabs.forEach(b => {
        const active = b.dataset.tab === key;
        b.classList.toggle("bg-primary-500", active);
        b.classList.toggle("text-white", active);
        b.classList.toggle("shadow-sm", active);
        b.setAttribute("aria-selected", active);
      });
      Object.entries(panels).forEach(([k, el]) => el.classList.toggle("hidden", k !== key));
    };
    tabs.forEach(b => b.addEventListener("click", () => setActive(b.dataset.tab)));
    setActive("mov"); // por defecto movimientos
  }

  window.openHistorialModal = openHistorialModal;

    // Detecta todos los botones que abren el modal
    document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".btn-show-history").forEach(btn => {
        btn.addEventListener("click", (e) => {
        e.preventDefault();
        openHistorialModal();
        });
    });
    });
})();
