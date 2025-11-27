console.log("[CHAT] Inicializando chat flotante...");

const ChatFloat = (() => {

    // ==============================
    // DOM
    // ==============================
    const btn     = document.getElementById("chat-float-btn");
    const panel   = document.getElementById("chat-mini-panel");
    const userView = document.getElementById("chat-user-view");
    const chatView = document.getElementById("chat-message-view");
    const closeBtn = document.getElementById("chat-close-btn");
    const backBtn  = document.getElementById("chat-back-btn");
    const chatBody = document.getElementById("chat-body");
    const chatInput= document.getElementById("chat-input");
    const targetName = document.getElementById("chat-target-name");

    let currentUser = null;
    let selectedUser = null;

    // ==============================
    // Abrir panel
    // ==============================
    function openPanel() {
        panel.classList.remove("hidden");
        btn.classList.add("hidden");
        loadUsers();
    }

    // ==============================
    // Cerrar panel
    // ==============================
    function closePanel() {
        panel.classList.add("hidden");
        btn.classList.remove("hidden");
        resetUI();
    }

    function resetUI() {
        userView.classList.remove("hidden");
        chatView.classList.add("hidden");
        chatBody.innerHTML = "";
        chatInput.value = "";
        selectedUser = null;
    }

    // ==============================
    // Cargar usuarios
    // ==============================
    async function loadUsers() {
        userView.innerHTML = `
            <div class="flex justify-center p-4 text-neutral-500 text-sm">
                Cargando usuarios...
            </div>
        `;

        try {
            const res = await fetch("/api/chat/users");
            const data = await res.json();

            if (!data.success) throw "error api";

            renderUsers(data.usuarios);

        } catch (err) {
            console.error("[CHAT] Error cargando usuarios:", err);

            userView.innerHTML = `
                <div class="p-3 text-center text-red-500">
                    Error cargando usuarios
                </div>
            `;
        }
    }

    // ==============================
    // Render usuarios
    // ==============================
    function renderUsers(lista) {
        userView.innerHTML = "";

        if (!lista.length) {
            userView.innerHTML = `
                <div class="p-3 text-center text-neutral-500">
                    No hay otros usuarios disponibles
                </div>
            `;
            return;
        }

        lista.forEach(u => {
            const card = document.createElement("div");
            card.className = `
                usuario-mini-item flex items-center justify-between
            `;
            card.innerHTML = `
                <div>
                    <p class="font-medium">${u.nombre}</p>
                    <p class="text-xs opacity-60">${u.rol}</p>
                </div>
            `;
            card.onclick = () => openChat(u);
            userView.appendChild(card);
        });
    }

    // ==============================
    // Abrir chat con usuario
    // ==============================
    function openChat(userObj) {
        selectedUser = userObj;
        targetName.textContent = userObj.nombre;

        userView.classList.add("hidden");
        chatView.classList.remove("hidden");

        chatBody.innerHTML = `
            <div class="p-4 text-center text-sm text-neutral-500">
                👋 Comienza a conversar con <b>${userObj.nombre}</b>
            </div>
        `;
    }

    // ==============================
    // Enviar mensaje (solo UI)
    // ==============================
    function sendMessage() {
        const txt = chatInput.value.trim();
        if (!txt) return;

        const el = document.createElement("div");
        el.className = "text-right";
        el.innerHTML = `
            <div class="inline-block bg-indigo-500 text-white px-3 py-2 rounded-lg mb-2">
                ${txt}
            </div>
        `;
        chatBody.appendChild(el);

        chatInput.value = "";
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // ==============================
    // Eventos
    // ==============================
    btn.addEventListener("click", openPanel);
    closeBtn.addEventListener("click", closePanel);
    backBtn.addEventListener("click", resetUI);

    chatInput.addEventListener("keydown", e => {
        if (e.key === "Enter") sendMessage();
    });

    // ==============================
    // Init
    // ==============================
    function init() {
        console.log("[CHAT] Chat flotante iniciado.");
    }

    return { init };

})();

document.addEventListener("DOMContentLoaded", ChatFloat.init);
