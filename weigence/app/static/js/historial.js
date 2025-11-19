(function () {
  // Prevenir ejecución múltiple
  if (window.__HISTORIAL_INITIALIZED__) {
    console.log('Historial ya inicializado, saltando...');
    return;
  }
  window.__HISTORIAL_INITIALIZED__ = true;

  async function openHistorialModal() {
    try {
      const response = await fetch("/historial", { cache: "no-store" });
      if (!response.ok) throw new Error('Error al cargar historial');
      
      const html = await response.text();
      const wrap = document.createElement("div");
      wrap.innerHTML = html.trim();
      const modal = wrap.firstElementChild;
      
      if (!modal || modal.id !== "historial-modal") {
        console.error('Modal de historial no encontrado en la respuesta');
        return;
      }
      
      document.body.appendChild(modal);
      initModal(modal);
    } catch (error) {
      console.error('Error al abrir modal de historial:', error);
    }
  }

  function initModal(root) {
    // Cierre del modal
    const close = () => {
      root.style.animation = 'fadeOut 0.2s ease-out';
      setTimeout(() => root.remove(), 200);
    };
    
    root.querySelector("[data-close]")?.addEventListener("click", close);
    root.addEventListener("click", (e) => { 
      if (e.target === root) close(); 
    });
    
    document.addEventListener("keydown", function escHandler(e) { 
      if (e.key === "Escape") {
        close();
        document.removeEventListener("keydown", escHandler);
      }
    });

    // Tabs
    const tabs = root.querySelectorAll(".tab-btn");
    const panels = { 
      mov: root.querySelector("#panel-mov"), 
      err: root.querySelector("#panel-err") 
    };
    
    const setActive = (key) => {
      tabs.forEach(b => {
        const active = b.dataset.tab === key;
        b.setAttribute("aria-selected", active);
      });
      Object.entries(panels).forEach(([k, el]) => {
        if (el) el.classList.toggle("hidden", k !== key);
      });
    };
    
    tabs.forEach(b => b.addEventListener("click", () => setActive(b.dataset.tab)));
    setActive("mov"); // Por defecto movimientos
    
    // Animación de entrada
    root.style.animation = 'fadeIn 0.2s ease-out';
  }

  // Exponer función globalmente
  window.openHistorialModal = openHistorialModal;

  // Event delegation para manejar clicks en botones dinámicos también
  document.addEventListener("click", (e) => {
    const historialBtn = e.target.closest(".btn-show-history, #btn-show-history");
    if (historialBtn) {
      e.preventDefault();
      e.stopPropagation();
      openHistorialModal();
    }
  });

  // Agregar estilos de animación
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes fadeOut {
      from { opacity: 1; }
      to { opacity: 0; }
    }
  `;
  document.head.appendChild(style);
})();

