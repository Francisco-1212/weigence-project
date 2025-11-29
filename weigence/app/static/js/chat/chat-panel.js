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
    const unreadBadge = document.getElementById("chat-unread-badge");

    if (!btn || !panel || !userView || !chatView || !chatBody || !chatInput) {
        console.warn("[CHAT] Elementos del chat no encontrados, se aborta inicializacion");
        return { init() {} };
    }

    const currentUser = window.CURRENT_USER || {};
    let selectedUser = null;
    let currentConversationId = null;
    const renderedMessageIds = new Set();
    let socketReady = false;
    let unreadInterval = null;

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
        // Actualizar contador al abrir
        updateUnreadCount();
    }

    function closePanel() {
        panel.classList.add("hidden");
        btn.classList.remove("hidden");
        resetUI();
        // Actualizar contador al cerrar
        updateUnreadCount();
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
        // Actualizar contador al volver a la lista
        updateUnreadCount();
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

    async function renderUsers(lista) {
        userView.innerHTML = "";

        if (!lista.length) {
            userView.innerHTML = `
                <div class="p-3 text-center text-neutral-500">
                    No hay otros usuarios disponibles
                </div>
            `;
            return;
        }

        // Obtener conversaciones para mostrar mensajes no leídos
        let conversaciones = [];
        try {
            const res = await fetch("/api/chat/conversaciones");
            const data = await res.json();
            if (data.success) {
                conversaciones = data.lista;
            }
        } catch (err) {
            console.warn("[CHAT] Error cargando conversaciones para badges:", err);
        }

        lista.forEach(u => {
            // Buscar si hay conversación con este usuario
            const conv = conversaciones.find(c => c.usuario && c.usuario.rut_usuario === u.id);
            const unread = conv ? (conv.unread || 0) : 0;

            const card = document.createElement("div");
            card.className = "usuario-mini-item flex items-center justify-between cursor-pointer hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg px-2 py-3 relative";
            card.innerHTML = `
                <div class="flex-1">
                    <p class="font-medium flex items-center gap-2">
                        ${u.nombre}
                        ${unread > 0 ? `<span class="inline-flex items-center justify-center bg-red-500 text-white text-[10px] font-bold rounded-full w-5 h-5">${unread > 99 ? '99+' : unread}</span>` : ''}
                    </p>
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
                
                // Marcar mensajes como leídos
                const ultimoMensaje = data.mensajes[data.mensajes.length - 1];
                if (ultimoMensaje && ultimoMensaje.id) {
                    try {
                        if (typeof ChatCore !== "undefined" && ChatCore.seen) {
                            ChatCore.seen(ultimoMensaje.id);
                        }
                        // Actualizar el contador de no leídos
                        updateUnreadCount();
                    } catch (e) {
                        console.warn("[CHAT] Error marcando mensajes como leídos:", e);
                    }
                }
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
        
        // Si el mensaje es para la conversación actual, renderizarlo y marcarlo como leído
        if (String(msg.conversacion_id) === String(currentConversationId || "")) {
            renderMessage(msg);
            
            // Marcar como leído si el chat está abierto y visible
            if (msg.id && !panel.classList.contains("hidden")) {
                try {
                    if (typeof ChatCore !== "undefined" && ChatCore.seen) {
                        ChatCore.seen(msg.id);
                    }
                } catch (e) {
                    console.warn("[CHAT] Error marcando mensaje como leído:", e);
                }
            }
        }
        
        // Actualizar el contador cuando llega un mensaje nuevo
        updateUnreadCount();
    }

    // =============================================
    // CONTADOR DE MENSAJES NO LEÍDOS
    // =============================================

    async function updateUnreadCount() {
        if (!unreadBadge) return;

        try {
            const res = await fetch("/api/chat/conversaciones");
            const data = await res.json();

            if (!data.success) {
                unreadBadge.classList.add("hidden");
                return;
            }

            // Sumar todos los mensajes no leídos
            const total = data.lista.reduce((sum, conv) => sum + (conv.unread || 0), 0);

            // Solo mostrar badge si hay mensajes no leídos
            if (total > 0) {
                unreadBadge.textContent = total > 99 ? "99+" : total;
                unreadBadge.classList.remove("hidden");
            } else {
                unreadBadge.classList.add("hidden");
            }
        } catch (err) {
            console.warn("[CHAT] Error actualizando contador de no leídos:", err);
            unreadBadge.classList.add("hidden");
        }
    }

    function startUnreadPolling() {
        // Actualizar inmediatamente
        updateUnreadCount();

        // Actualizar cada 30 segundos
        if (unreadInterval) clearInterval(unreadInterval);
        unreadInterval = setInterval(updateUnreadCount, 30000);
    }

    function stopUnreadPolling() {
        if (unreadInterval) {
            clearInterval(unreadInterval);
            unreadInterval = null;
        }
    }

    // =============================================
    // DETECTOR DE PANEL DE NOTIFICACIONES
    // =============================================

    function setupNotificationObserver() {
        const notifPanel = document.getElementById("notification-panel");
        const chatContainer = document.getElementById("chat-float-container");
        
        if (!chatContainer) return;

        // 1. Observar panel lateral de notificaciones (header)
        if (notifPanel) {
            const panelObserver = new MutationObserver(() => {
                const isOpen = !notifPanel.classList.contains("translate-x-full");
                
                if (isOpen) {
                    chatContainer.classList.add("notification-open");
                } else {
                    chatContainer.classList.remove("notification-open");
                }
            });

            panelObserver.observe(notifPanel, {
                attributes: true,
                attributeFilter: ["class"]
            });
        }

        // 2. Observar notificaciones inline (como en auditoría)
        // Buscar específicamente las notificaciones tipo toast
        let checkInterval = setInterval(() => {
            let hasInlineNotif = false;
            
            // Buscar notificaciones en la parte inferior derecha (bottom-4 right-4)
            const toastElements = document.querySelectorAll('.fixed');
            
            toastElements.forEach(el => {
                // Ignorar el panel de notificaciones del header y el chat mismo
                if (el.id === 'notification-panel' || 
                    el.id === 'notification-backdrop' ||
                    el.id === 'chat-float-container' ||
                    el.closest('#chat-float-container')) {
                    return;
                }
                
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                const classes = el.className || '';
                
                // Verificar si es un toast visible en la parte inferior derecha
                const isBottomRight = classes.includes('bottom') || classes.includes('right');
                const isVisible = style.display !== 'none' && 
                                 style.visibility !== 'hidden' && 
                                 parseFloat(style.opacity) > 0 &&
                                 rect.height > 0 &&
                                 rect.width > 0;
                
                // Si está en la parte inferior de la pantalla
                const isAtBottom = rect.bottom > window.innerHeight - 150;
                
                if (isVisible && isBottomRight && isAtBottom) {
                    hasInlineNotif = true;
                }
            });
            
            const wasOpen = chatContainer.classList.contains("notification-open");
            
            if (hasInlineNotif && !wasOpen) {
                chatContainer.classList.add("notification-open");
                console.log("[CHAT] 📢 Notificación detectada - Moviendo chat hacia arriba");
            } else if (!hasInlineNotif && wasOpen && (!notifPanel || notifPanel.classList.contains("translate-x-full"))) {
                chatContainer.classList.remove("notification-open");
                console.log("[CHAT] ✅ Notificación cerrada - Volviendo chat a posición normal");
            }
        }, 5); // Verificar cada 5ms para detección instantánea

        console.log("[CHAT] Observador de notificaciones configurado");
    }

    function init() {
        ensureSocket();
        startUnreadPolling();
        setupNotificationObserver();
        console.log("[CHAT] Chat flotante iniciado.");
    }

    return { init, openPanel, closePanel, updateUnreadCount };

})();

if (typeof window !== "undefined") {
    window.ChatFloat = ChatFloat;
}

document.addEventListener("DOMContentLoaded", ChatFloat.init);
