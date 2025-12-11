
(() => {
    // DOM elements
    const btn = document.getElementById("chat-float-btn");
    const panel = document.getElementById("chat-mini-panel");
    const closeBtn = document.getElementById("chat-close-btn");

    if (!btn || !panel || !closeBtn) {
        console.warn("[CHAT] chat-float: elementos no encontrados, se omite binding");
        return;
    }

    let abierto = false;

    const bindOnce = (target, event, key, handler) => {
        if (!target) return;
        const flag = `__chatBound_${key}`;
        if (target[flag]) return;
        target.addEventListener(event, handler);
        target[flag] = true;
    };

    const open = () => {
        if (window.ChatFloat && typeof window.ChatFloat.openPanel === "function") {
            window.ChatFloat.openPanel();
        } else {
            panel.classList.remove("hidden");
            btn.classList.add("hidden");
        }
        abierto = true;
    };

    const close = () => {
        if (window.ChatFloat && typeof window.ChatFloat.closePanel === "function") {
            window.ChatFloat.closePanel();
        } else {
            panel.classList.add("hidden");
            btn.classList.remove("hidden");
        }
        abierto = false;
    };

    // Animación "viva" al hacer click (rebote extra)
    bindOnce(btn, "mousedown", "bounce", () => {
        btn.classList.remove("chat-float-btn-pressed");
        void btn.offsetWidth; // force reflow
        btn.classList.add("chat-float-btn-pressed");
        setTimeout(() => btn.classList.remove("chat-float-btn-pressed"), 350);
    });
    bindOnce(btn, "click", "open", open);
    bindOnce(closeBtn, "click", "close", close);
    bindOnce(document, "click", "outside", (e) => {
        if (!abierto) return;
        const target = e.target;
        if (!panel.contains(target) && !btn.contains(target)) {
            close();
        }
    });
})();
