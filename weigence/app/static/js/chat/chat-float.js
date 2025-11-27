// ELEMENTOS
const btn = document.getElementById("chat-float-btn");
const panel = document.getElementById("chat-mini-panel");
const closeBtn = document.getElementById("chat-close-btn");

// Estado
let abierto = false;

// Mostrar panel
btn.addEventListener("click", () => {
    panel.classList.remove("hidden");
    btn.classList.add("hidden");
    abierto = true;
});

// Cerrar panel
closeBtn.addEventListener("click", () => {
    panel.classList.add("hidden");
    btn.classList.remove("hidden");
    abierto = false;
});
document.addEventListener("click", (e) => {
    if (!abierto) return;
    if (!panel.contains(e.target) && !btn.contains(e.target)) {
        panel.classList.add("hidden");
        btn.classList.remove("hidden");
        abierto = false;
    }
});
