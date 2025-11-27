console.log("[CHAT] Inicializando chat flotante...");

const ChatFloat = (() => {
    const btn = document.getElementById("chat-float-btn");
    const panel = document.getElementById("chat-mini-panel");
    const userView = document.getElementById("chat-user-view");
    const chatView = document.getElementById("chat-message-view");
    const closeBtn = document.getElementById("chat-close-btn");
    const backBtn = document.getElementById("chat-back-btn");
    const chatBody = document.getElementById("chat-body");
    const chatInput = document.getElementById("chat-input");
    const targetName = document.getElementById("chat-target-name");

    if (!btn || !panel || !userView || !chatView || !chatBody || !chatInput) {
        console.warn("[CHAT] Elementos del chat no encontrados, se aborta inicializacion");
        return { init() {} };
    }

    const currentUser = window.CURRENT_USER || {};
    let selectedUser = null;
    let currentConversationId = null;
    const renderedMessageIds = new Set();
    let socketReady = false;

    function ensureSocket() {
        if (socketReady) return;
        if (typeof ChatCore === "undefined") {
            console.warn("[CHAT] ChatCore no disponible (socket.io no cargado)");
            return;
        }

        ChatCore.init();
        ChatCore.onMessage(handleIncomingMessage);
        ChatCore.onError((err) => console.warn("[CHAT] WS error", err));
        ChatCore.onJoined((data) => console.log("[CHAT] Unido a sala", data));
        socketReady = true;
    }

    function setPlaceholder(html) {
        chatBody.dataset.placeholder = "1";
        chatBody.innerHTML = html;
    }

    function clearPlaceholder() {
        if (chatBody.dataset.placeholder) {
            delete chatBody.dataset.placeholder;
            chatBody.innerHTML = "";
        }
    }

    function renderMessage(msg) {
        if (!msg || String(msg.conversacion_id) !== String(currentConversationId || "")) return;
        if (msg.id && renderedMessageIds.has(msg.id)) return;
        if (msg.id) renderedMessageIds.add(msg.id);
        clearPlaceholder();

        const isMine = msg.usuario_id === currentUser.id;
        const wrapper = document.createElement("div");
        wrapper.className = `flex ${isMine ? "justify-end" : "justify-start"}`;

        const bubble = document.createElement("div");
        bubble.className = `${isMine ? "bg-indigo-500 text-white" : "bg-neutral-200 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-50"} px-3 py-2 rounded-lg shadow-sm max-w-[85%] whitespace-pre-line break-words`;
        bubble.textContent = msg.contenido || "";

        const meta = document.createElement("div");
        meta.className = "text-[11px] opacity-60 mt-1";
        const ts = msg.fecha_envio ? new Date(msg.fecha_envio) : null;
        meta.textContent = ts ? ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";

        const inner = document.createElement("div");
        inner.appendChild(bubble);
        if (meta.textContent) inner.appendChild(meta);

        wrapper.appendChild(inner);
        chatBody.appendChild(wrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function openPanel() {
        ensureSocket();
        panel.classList.remove("hidden");
        btn.classList.add("hidden");
        loadUsers();
    }

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
        currentConversationId = null;
        renderedMessageIds.clear();
        if (typeof ChatCore !== "undefined") {
            ChatCore.leave();
        }
    }

    async function loadUsers() {
        userView.innerHTML = `
            <div class="flex justify-center p-4 text-neutral-500 text-sm">
                Cargando usuarios...
            </div>
        `;

        try {
            const res = await fetch("/api/chat/users");
            const data = await res.json();

            if (!data.success) throw new Error("error api");

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
            card.className = "usuario-mini-item flex items-center justify-between cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg px-2 py-3";
            card.innerHTML = `
                <div>
                    <p class="font-medium">${u.nombre}</p>
                    <p class="text-xs opacity-60">${u.rol}</p>
                </div>
                ${u.is_online ? '<span class="w-2 h-2 rounded-full bg-green-500"></span>' : ""}
            `;
            card.onclick = () => openChat(u);
            userView.appendChild(card);
        });
    }

    async function openChat(userObj) {
        ensureSocket();
        selectedUser = userObj;
        targetName.textContent = userObj.nombre;

        userView.classList.add("hidden");
        chatView.classList.remove("hidden");
        renderedMessageIds.clear();
        currentConversationId = null;

        setPlaceholder(`
            <div class="p-4 text-center text-sm text-neutral-500">
                Cargando conversacion con <b>${userObj.nombre}</b>...
            </div>
        `);

        try {
            const res = await fetch(`/api/chat/history/${encodeURIComponent(userObj.id)}`);
            const data = await res.json();
            if (!data.success) throw new Error(data.msg || "No se pudo cargar el historial");

            currentConversationId = data.conversacion_id;
            if (typeof ChatCore !== "undefined") {
                ChatCore.join(currentConversationId);
            }

            chatBody.innerHTML = "";
            if (!data.mensajes || !data.mensajes.length) {
                setPlaceholder(`
                    <div class="p-4 text-center text-sm text-neutral-500">
                        Sin mensajes. Escribe el primero para <b>${userObj.nombre}</b>.
                    </div>
                `);
            } else {
                data.mensajes.forEach(renderMessage);
            }
        } catch (err) {
            console.error("[CHAT] Error cargando historial:", err);
            setPlaceholder(`
                <div class="p-4 text-center text-sm text-red-500">
                    No se pudo cargar el chat. Intenta nuevamente.
                </div>
            `);
        }
    }

    async function sendMessage() {
        const txt = chatInput.value.trim();
        if (!txt || !selectedUser || !currentConversationId) return;

        chatInput.value = "";

        let sentViaWs = false;
        if (typeof ChatCore !== "undefined" && ChatCore.isConnected && ChatCore.currentRoom) {
            try {
                if (String(ChatCore.currentRoom()) !== String(currentConversationId)) {
                    ChatCore.join(currentConversationId);
                }
                if (ChatCore.isConnected()) {
                    ChatCore.send(txt);
                    sentViaWs = true;
                }
            } catch (err) {
                console.warn("[CHAT] No se pudo enviar por WS", err);
            }
        }

        if (sentViaWs) return;

        try {
            const res = await fetch("/api/chat/send", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    conversacion_id: currentConversationId,
                    destinatario_id: selectedUser.id,
                    contenido: txt,
                }),
            });

            const data = await res.json();
            if (!data.success) throw new Error(data.msg || "No se pudo enviar");

            currentConversationId = data.conversacion_id || currentConversationId;
            renderMessage(data.mensaje);
        } catch (err) {
            console.error("[CHAT] Error enviando mensaje:", err);
            chatBody.insertAdjacentHTML("beforeend", `
                <div class="p-2 text-xs text-red-500 text-center">
                    ${err?.message || "No se pudo enviar el mensaje"}
                </div>
            `);
        }
    }

    btn.addEventListener("click", openPanel);
    closeBtn.addEventListener("click", closePanel);
    backBtn.addEventListener("click", resetUI);

    chatInput.addEventListener("keydown", e => {
        if (e.key === "Enter") sendMessage();
    });

    function handleIncomingMessage(msg) {
        if (!msg) return;
        if (String(msg.conversacion_id) !== String(currentConversationId || "")) return;
        renderMessage(msg);
    }

    function init() {
        ensureSocket();
        console.log("[CHAT] Chat flotante iniciado.");
    }

    return { init, openPanel, closePanel };

})();

if (typeof window !== "undefined") {
    window.ChatFloat = ChatFloat;
}

document.addEventListener("DOMContentLoaded", ChatFloat.init);
