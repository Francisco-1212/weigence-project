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
    const pinnedContainer = document.getElementById("chat-pinned-container");

    if (!btn || !panel || !userView || !chatView || !chatBody || !chatInput) {
        console.warn("[CHAT] Elementos del chat no encontrados, se aborta inicializacion");
        return { init() {} };
    }

    const currentUser = window.CURRENT_USER || {};
    let selectedUser = null;
    let currentConversationId = null;
    const renderedMessageIds = new Set();
    const messageCache = new Map(); // Cache global de mensajes
    const conversationCaches = new Map(); // Cache por conversación
    let socketReady = false;
    let unreadInterval = null;

    // Función para guardar mensaje en cache
    function saveToCache(msg) {
        if (!msg || !msg.id) return;
        
        const conversationId = String(msg.conversacion_id);
        
        // Crear cache para esta conversación si no existe
        if (!conversationCaches.has(conversationId)) {
            conversationCaches.set(conversationId, new Map());
        }
        
        const cache = conversationCaches.get(conversationId);
        const msgData = {
            contenido: msg.contenido,
            usuario_id: msg.usuario_id,
            usuario_nombre: msg.usuario_nombre || selectedUser?.nombre,
            fecha_envio: msg.fecha_envio
        };
        
        cache.set(msg.id, msgData);
        messageCache.set(msg.id, msgData); // También en cache global
    }

    // Función para obtener mensaje del cache
    function getFromCache(messageId, conversationId = null) {
        // Intentar desde cache de conversación específica primero
        if (conversationId) {
            const convCache = conversationCaches.get(String(conversationId));
            if (convCache && convCache.has(messageId)) {
                return convCache.get(messageId);
            }
        }
        
        // Fallback a cache global
        return messageCache.get(messageId);
    }

    // Función para obtener mensaje original del backend
    async function fetchOriginalMessage(messageId) {
        try {
            const res = await fetch(`/api/chat/mensajes/${messageId}`);
            const data = await res.json();
            
            if (data.success && data.mensaje) {
                // Guardar en cache
                saveToCache(data.mensaje);
                return data.mensaje;
            }
        } catch (err) {
            console.warn('[CHAT] Error obteniendo mensaje original:', err);
        }
        return null;
    }

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
        ChatCore.onReaction(handleIncomingReaction);
        ChatCore.onDelete(handleMessageDeleted);
        ChatCore.onPin(handleMessagePinned);
        ChatCore.onUnpin(handleMessageUnpinned);
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
        if (msg.id) {
            renderedMessageIds.add(msg.id);
            saveToCache(msg); // Usar nueva función de cache
        }
        clearPlaceholder();

        const isMine = msg.usuario_id === currentUser.id;
        const wrapper = document.createElement("div");
        wrapper.className = `message-wrapper ${isMine ? "mine" : "other"}`;
        wrapper.dataset.messageId = msg.id;

        const inner = document.createElement("div");
        inner.className = "flex flex-col";
        inner.style.maxWidth = "280px";
        inner.style.position = "relative";

        // Botones de acción (emoji, responder, más) - en columna vertical
        const actions = document.createElement("div");
        actions.className = "message-actions";
        
        const emojiBtn = document.createElement("button");
        emojiBtn.className = "message-action-btn emoji-btn";
        emojiBtn.title = "Reaccionar";
        emojiBtn.innerHTML = '<span style="font-size: 18px;">😊</span>';
        emojiBtn.onclick = (e) => {
            e.stopPropagation();
            toggleEmojiPicker(emojiBtn, msg);
        };

        const replyBtn = document.createElement("button");
        replyBtn.className = "message-action-btn";
        replyBtn.title = "Responder";
        replyBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px; color: #6b7280;">reply</span>';
        replyBtn.onclick = (e) => {
            e.stopPropagation();
            replyToMessage(msg);
        };

        const moreBtn = document.createElement("button");
        moreBtn.className = "message-action-btn more-btn";
        moreBtn.title = "Más opciones";
        moreBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px; color: #6b7280;">more_horiz</span>';
        moreBtn.onclick = (e) => {
            e.stopPropagation();
            toggleMoreMenu(moreBtn, msg, isMine);
        };

        actions.appendChild(emojiBtn);
        actions.appendChild(replyBtn);
        actions.appendChild(moreBtn);

        const bubble = document.createElement("div");
        bubble.className = `message-bubble ${isMine ? "message-bubble-mine" : "message-bubble-other"}`;
        
        // Si es una respuesta, mostrar el contexto
        if (msg.reply_to) {
            const replyContext = document.createElement("div");
            replyContext.className = `reply-context ${isMine ? "reply-mine" : "reply-other"}`;
            
            let replyContent = '[Mensaje]';
            let replyAuthor = "un mensaje";
            
            // 1. Intentar usar datos del backend
            if (msg.reply_to_content) {
                replyContent = msg.reply_to_content;
                replyAuthor = msg.reply_to_user_id === currentUser.id 
                    ? "tu mensaje" 
                    : (msg.reply_to_user_name || "un mensaje");
            } 
            // 2. Intentar desde cache
            else {
                const cachedMsg = getFromCache(msg.reply_to, currentConversationId);
                if (cachedMsg) {
                    replyContent = cachedMsg.contenido;
                    replyAuthor = cachedMsg.usuario_id === currentUser.id 
                        ? "tu mensaje" 
                        : (cachedMsg.usuario_nombre || "un mensaje");
                }
                // 3. Si no está en cache, obtener del backend
                else {
                    fetchOriginalMessage(msg.reply_to).then(originalMsg => {
                        if (originalMsg) {
                            const authorSpan = replyContext.querySelector('.reply-author');
                            const contentSpan = replyContext.querySelector('.reply-content');
                            
                            if (authorSpan && contentSpan) {
                                const author = originalMsg.usuario_id === currentUser.id 
                                    ? 'tu mensaje' 
                                    : (originalMsg.usuario_nombre || 'un mensaje');
                                authorSpan.textContent = `Respondiendo a ${author}`;
                                contentSpan.textContent = originalMsg.contenido.substring(0, 50) + (originalMsg.contenido.length > 50 ? '...' : '');
                            }
                        }
                    });
                }
            }
            
            replyContext.innerHTML = `
                <div class="flex items-start gap-2 mb-2 pb-2 border-b ${isMine ? 'border-indigo-400/30' : 'border-neutral-300 dark:border-neutral-600'}">
                    <span class="material-symbols-outlined text-xs opacity-60">reply</span>
                    <div class="flex-1 text-xs opacity-80">
                        <div class="font-semibold reply-author">Respondiendo a ${replyAuthor}</div>
                        <div class="opacity-70 mt-0.5 reply-content">${replyContent.substring(0, 50)}${replyContent.length > 50 ? '...' : ''}</div>
                    </div>
                </div>
            `;
            bubble.appendChild(replyContext);
        }
        
        const content = document.createElement("div");
        content.textContent = msg.contenido || "";
        bubble.appendChild(content);

        // Agregar reacción si existe
        if (msg.reaction) {
            const reaction = document.createElement("div");
            reaction.className = "message-reaction";
            reaction.innerHTML = `
                <span>${msg.reaction}</span>
                <span class="message-reaction-count">1</span>
            `;
            bubble.style.position = "relative";
            bubble.appendChild(reaction);
        }

        const meta = document.createElement("div");
        meta.className = `text-[10px] opacity-60 mt-1 px-1 ${isMine ? "text-right" : "text-left"}`;
        const ts = msg.fecha_envio ? new Date(msg.fecha_envio) : null;
        meta.textContent = ts ? ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "";

        inner.appendChild(bubble);
        if (meta.textContent) inner.appendChild(meta);

        wrapper.appendChild(inner);
        wrapper.appendChild(actions);
        chatBody.appendChild(wrapper);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function toggleEmojiPicker(btn, msg) {
        // Cerrar otros pickers abiertos
        document.querySelectorAll('.emoji-picker, .more-menu').forEach(el => el.remove());

        const picker = document.createElement("div");
        picker.className = "emoji-picker";
        
        const emojis = ['❤️', '😂', '😮', '😔', '👍'];
        emojis.forEach(emoji => {
            const option = document.createElement("button");
            option.className = "emoji-option";
            option.textContent = emoji;
            option.onclick = (e) => {
                e.stopPropagation();
                addReaction(msg, emoji);
                picker.remove();
            };
            picker.appendChild(option);
        });

        document.body.appendChild(picker);

        // Posicionar el picker cerca del botón
        const rect = btn.getBoundingClientRect();
        const pickerWidth = picker.offsetWidth || 220;
        const isMine = btn.closest('.message-wrapper').classList.contains('mine');
        
        let left = isMine ? rect.left - pickerWidth - 8 : rect.right + 8;
        let top = rect.top;
        
        // Ajustar si se sale por la derecha
        if (left + pickerWidth > window.innerWidth) {
            left = window.innerWidth - pickerWidth - 16;
        }
        
        // Ajustar si se sale por la izquierda
        if (left < 16) {
            left = 16;
        }
        
        picker.style.left = left + 'px';
        picker.style.top = top + 'px';

        // Cerrar al hacer click fuera
        setTimeout(() => {
            document.addEventListener('click', function closePickerHandler(e) {
                if (!picker.contains(e.target)) {
                    picker.remove();
                    document.removeEventListener('click', closePickerHandler);
                }
            });
        }, 0);
    }

    function toggleMoreMenu(btn, msg, isMine) {
        // Cerrar otros menús abiertos
        document.querySelectorAll('.emoji-picker, .more-menu').forEach(el => el.remove());

        const menu = document.createElement("div");
        menu.className = "more-menu";
        
        if (isMine) {
            const cancelItem = document.createElement("button");
            cancelItem.className = "more-menu-item danger";
            cancelItem.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px;">cancel</span> Anular envío';
            cancelItem.onclick = (e) => {
                e.stopPropagation();
                deleteMessage(msg);
                menu.remove();
            };
            menu.appendChild(cancelItem);
        }

        const forwardItem = document.createElement("button");
        forwardItem.className = "more-menu-item";
        forwardItem.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px;">forward</span> Reenviar';
        forwardItem.onclick = (e) => {
            e.stopPropagation();
            forwardMessage(msg);
            menu.remove();
        };
        menu.appendChild(forwardItem);

        const pinItem = document.createElement("button");
        pinItem.className = "more-menu-item";
        pinItem.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px;">push_pin</span> Fijar';
        pinItem.onclick = (e) => {
            e.stopPropagation();
            pinMessage(msg);
            menu.remove();
        };
        menu.appendChild(pinItem);

        document.body.appendChild(menu);

        // Posicionar el menú cerca del botón
        const rect = btn.getBoundingClientRect();
        const menuWidth = 160;
        const menuHeight = menu.offsetHeight || 120;
        
        // Calcular posición
        let left = isMine ? rect.left - menuWidth - 8 : rect.right + 8;
        let top = rect.top;
        
        // Ajustar si se sale por la derecha
        if (left + menuWidth > window.innerWidth) {
            left = window.innerWidth - menuWidth - 16;
        }
        
        // Ajustar si se sale por la izquierda
        if (left < 16) {
            left = 16;
        }
        
        // Ajustar si se sale por abajo
        if (top + menuHeight > window.innerHeight) {
            top = window.innerHeight - menuHeight - 16;
        }
        
        menu.style.left = left + 'px';
        menu.style.top = top + 'px';

        // Cerrar al hacer click fuera
        setTimeout(() => {
            document.addEventListener('click', function closeMenuHandler(e) {
                if (!menu.contains(e.target)) {
                    menu.remove();
                    document.removeEventListener('click', closeMenuHandler);
                }
            });
        }, 0);
    }

    async function addReaction(msg, emoji) {
        try {
            const res = await fetch(`/api/chat/mensajes/${msg.id}/reaccion`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emoji })
            });

            if (res.ok) {
                // Actualizar UI localmente
                const wrapper = document.querySelector(`[data-message-id="${msg.id}"]`);
                if (wrapper) {
                    const bubble = wrapper.querySelector('.message-bubble');
                    let reaction = bubble.querySelector('.message-reaction');
                    
                    if (!reaction) {
                        reaction = document.createElement('div');
                        reaction.className = 'message-reaction';
                        bubble.style.position = 'relative';
                        bubble.appendChild(reaction);
                    }
                    
                    reaction.innerHTML = `
                        <span>${emoji}</span>
                        <span class="message-reaction-count">1</span>
                    `;
                }
                console.log(`[CHAT] Reacción ${emoji} agregada al mensaje ${msg.id}`);
            }
        } catch (err) {
            console.error('[CHAT] Error al agregar reacción:', err);
        }
    }

    async function deleteMessage(msg) {
        if (!confirm('¿Anular el envío de este mensaje?')) return;

        try {
            const res = await fetch(`/api/chat/mensajes/${msg.id}`, {
                method: 'DELETE'
            });

            if (res.ok) {
                // Remover mensaje de la UI
                const wrapper = document.querySelector(`[data-message-id="${msg.id}"]`);
                if (wrapper) {
                    wrapper.remove();
                }
                console.log(`[CHAT] Mensaje ${msg.id} eliminado`);
            }
        } catch (err) {
            console.error('[CHAT] Error al eliminar mensaje:', err);
        }
    }

    async function forwardMessage(msg) {
        // Cerrar chat actual y mostrar lista de usuarios para reenviar
        resetUI();
        
        // Guardar mensaje para reenviar
        sessionStorage.setItem('forwardMessage', JSON.stringify({
            contenido: msg.contenido,
            originalId: msg.id
        }));
        
        // Mostrar indicador
        const indicator = document.createElement('div');
        indicator.className = 'bg-indigo-100 dark:bg-indigo-900 p-3 rounded-lg mb-3 text-sm';
        indicator.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <span class="material-symbols-outlined" style="font-size: 16px;">forward</span>
                    <span class="ml-2">Selecciona un usuario para reenviar</span>
                </div>
                <button onclick="sessionStorage.removeItem('forwardMessage'); this.parentElement.parentElement.remove();" class="text-red-500">
                    <span class="material-symbols-outlined" style="font-size: 18px;">close</span>
                </button>
            </div>
            <div class="mt-2 pl-6 text-xs opacity-70">"${msg.contenido.substring(0, 50)}${msg.contenido.length > 50 ? '...' : ''}"</div>
        `;
        userView.insertBefore(indicator, userView.firstChild);
        
        console.log(`[CHAT] Preparado para reenviar mensaje ${msg.id}`);
    }

    async function pinMessage(msg) {
        try {
            const res = await fetch(`/api/chat/mensajes/${msg.id}/fijar`, {
                method: 'POST'
            });

            if (res.ok) {
                showPinnedMessage(msg);
                console.log(`[CHAT] Mensaje ${msg.id} fijado`);
            }
        } catch (err) {
            console.error('[CHAT] Error al fijar mensaje:', err);
        }
    }

    function showPinnedMessage(msg) {
        if (!pinnedContainer) return;

        const isMine = msg.usuario_id === currentUser.id;
        const authorName = isMine ? 'Tú' : (msg.usuario_nombre || selectedUser?.nombre || 'Usuario');
        
        pinnedContainer.innerHTML = `
            <div class="flex items-start gap-3 p-3">
                <span class="material-symbols-outlined text-amber-600 dark:text-amber-400" style="font-size: 20px;">push_pin</span>
                <div class="flex-1 min-w-0">
                    <div class="text-xs font-semibold text-amber-700 dark:text-amber-300 mb-0.5">Mensaje fijado</div>
                    <div class="text-sm text-neutral-700 dark:text-neutral-300">
                        <span class="font-medium">${authorName}:</span> ${msg.contenido}
                    </div>
                </div>
                <button 
                    class="text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200 transition-colors" 
                    onclick="ChatFloat.unpinMessage(${msg.id})"
                    title="Despinear mensaje">
                    <span class="material-symbols-outlined" style="font-size: 18px;">close</span>
                </button>
            </div>
        `;
        
        pinnedContainer.classList.remove('hidden');
        
        // Agregar ícono al mensaje original en el chat
        const wrapper = document.querySelector(`[data-message-id="${msg.id}"]`);
        if (wrapper) {
            const bubble = wrapper.querySelector('.message-bubble');
            if (!bubble.querySelector('.pin-icon')) {
                const pinIcon = document.createElement('span');
                pinIcon.className = 'material-symbols-outlined absolute top-1 right-1 text-amber-500 pin-icon';
                pinIcon.style.fontSize = '14px';
                pinIcon.textContent = 'push_pin';
                bubble.style.position = 'relative';
                bubble.appendChild(pinIcon);
            }
        }
    }

    async function unpinMessage(messageId) {
        try {
            const res = await fetch(`/api/chat/mensajes/${messageId}/desfijar`, {
                method: 'POST'
            });

            if (res.ok) {
                hidePinnedMessage();
                
                // Remover ícono del mensaje original
                const wrapper = document.querySelector(`[data-message-id="${messageId}"]`);
                if (wrapper) {
                    const pinIcon = wrapper.querySelector('.pin-icon');
                    if (pinIcon) pinIcon.remove();
                }
                
                console.log(`[CHAT] Mensaje ${messageId} desfijado`);
            }
        } catch (err) {
            console.error('[CHAT] Error al desfijar mensaje:', err);
        }
    }

    function hidePinnedMessage() {
        if (!pinnedContainer) return;
        pinnedContainer.classList.add('hidden');
        pinnedContainer.innerHTML = '';
    }

    function replyToMessage(msg) {
        // Agregar indicador de respuesta sobre el input
        let replyIndicator = document.getElementById('reply-indicator');
        
        if (!replyIndicator) {
            replyIndicator = document.createElement('div');
            replyIndicator.id = 'reply-indicator';
            replyIndicator.className = 'bg-neutral-100 dark:bg-neutral-800 border-l-4 border-indigo-500 p-2 text-sm';
            chatInput.parentElement.insertBefore(replyIndicator, chatInput.parentElement.firstChild);
        }
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'text-neutral-500 hover:text-neutral-700';
        closeBtn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 18px;">close</span>';
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            e.preventDefault();
            document.getElementById('reply-indicator').remove();
            delete window.replyingTo;
        };
        
        replyIndicator.innerHTML = '';
        const content = document.createElement('div');
        content.className = 'flex items-center justify-between';
        content.innerHTML = `
            <div>
                <div class="text-xs text-indigo-500 font-semibold">Respondiendo a:</div>
                <div class="text-xs opacity-70 mt-1">${msg.contenido.substring(0, 50)}${msg.contenido.length > 50 ? '...' : ''}</div>
            </div>
        `;
        content.appendChild(closeBtn);
        replyIndicator.appendChild(content);
        
        window.replyingTo = msg.id;
        chatInput.focus();
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
        hidePinnedMessage();
        // NO limpiar messageCache ni conversationCaches - mantener historial para referencias
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
            // Llamadas paralelas para mayor velocidad
            const [usersRes, convsRes] = await Promise.all([
                fetch("/api/chat/users"),
                fetch("/api/chat/conversaciones")
            ]);

            const usersData = await usersRes.json();
            const convsData = await convsRes.json();

            if (!usersData.success) throw new Error("error api usuarios");

            renderUsers(usersData.usuarios, convsData.success ? convsData.lista : []);

        } catch (err) {
            console.error("[CHAT] Error cargando usuarios:", err);

            userView.innerHTML = `
                <div class="p-3 text-center text-red-500">
                    Error cargando usuarios
                </div>
            `;
        }
    }

    function renderUsers(lista, conversaciones = []) {
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
                // Guardar TODOS los mensajes en cache antes de renderizar
                data.mensajes.forEach(msg => {
                    if (msg.id) {
                        saveToCache(msg);
                    }
                });
                
                // Ahora renderizar
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

            // Cargar mensaje fijado si existe
            if (data.mensaje_fijado) {
                showPinnedMessage(data.mensaje_fijado);
            }

            // Verificar si hay un mensaje pendiente para reenviar
            checkForwardMessage();
        } catch (err) {
            console.error("[CHAT] Error cargando historial:", err);
            setPlaceholder(`
                <div class="p-4 text-center text-sm text-red-500">
                    No se pudo cargar el chat. Intenta nuevamente.
                </div>
            `);
        }
    }

    function checkForwardMessage() {
        const forwardData = sessionStorage.getItem('forwardMessage');
        if (!forwardData) return;

        try {
            const { contenido, originalId } = JSON.parse(forwardData);
            
            // Prellenar el input con el mensaje a reenviar
            chatInput.value = contenido;
            chatInput.focus();
            
            // Limpiar sessionStorage
            sessionStorage.removeItem('forwardMessage');
            
            console.log(`[CHAT] Mensaje ${originalId} listo para reenviar a ${selectedUser.nombre}`);
        } catch (err) {
            console.error('[CHAT] Error procesando mensaje para reenviar:', err);
            sessionStorage.removeItem('forwardMessage');
        }
    }

    async function sendMessage() {
        const txt = chatInput.value.trim();
        if (!txt || !selectedUser || !currentConversationId) return;

        chatInput.value = "";

        // Preparar datos del mensaje con respuesta si existe
        const messageData = {
            conversacion_id: currentConversationId,
            destinatario_id: selectedUser.id,
            contenido: txt,
        };

        // Si está respondiendo a un mensaje, agregar el ID
        let replyToId = null;
        if (window.replyingTo) {
            messageData.reply_to = window.replyingTo;
            replyToId = window.replyingTo;
            console.log('[CHAT] Enviando respuesta a mensaje ID:', replyToId);
        }

        // Limpiar indicador de respuesta
        const replyIndicator = document.getElementById('reply-indicator');
        if (replyIndicator) {
            replyIndicator.remove();
        }
        delete window.replyingTo;

        let sentViaWs = false;
        if (typeof ChatCore !== "undefined" && ChatCore.isConnected && ChatCore.currentRoom) {
            try {
                if (String(ChatCore.currentRoom()) !== String(currentConversationId)) {
                    ChatCore.join(currentConversationId);
                }
                if (ChatCore.isConnected()) {
                    // Enviar con reply_to si existe
                    ChatCore.send(txt, messageData.reply_to || null);
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
                body: JSON.stringify(messageData),
            });

            const data = await res.json();
            if (!data.success) throw new Error(data.msg || "No se pudo enviar");

            currentConversationId = data.conversacion_id || currentConversationId;
            
            // Si había un reply_to, agregarlo manualmente al mensaje antes de renderizar
            if (replyToId && data.mensaje) {
                data.mensaje.reply_to = replyToId;
                console.log('[CHAT] Mensaje recibido del backend:', data.mensaje);
            }
            
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

    function handleIncomingReaction(data) {
        if (!data || !data.mensaje_id) return;
        
        console.log('[CHAT] 🎭 Reacción recibida por WS:', data);
        
        // Buscar el mensaje en el DOM y actualizar la reacción
        const wrapper = document.querySelector(`[data-message-id="${data.mensaje_id}"]`);
        if (wrapper) {
            const bubble = wrapper.querySelector('.message-bubble');
            let reaction = bubble.querySelector('.message-reaction');
            
            if (!reaction) {
                reaction = document.createElement('div');
                reaction.className = 'message-reaction';
                bubble.style.position = 'relative';
                bubble.appendChild(reaction);
            }
            
            reaction.innerHTML = `
                <span>${data.emoji}</span>
                <span class="message-reaction-count">1</span>
            `;
            
            console.log('[CHAT] ✅ Reacción actualizada en UI');
        }
    }

    function handleMessageDeleted(data) {
        if (!data || !data.mensaje_id) return;
        
        console.log('[CHAT] 🗑️ Mensaje eliminado por WS:', data);
        
        const wrapper = document.querySelector(`[data-message-id="${data.mensaje_id}"]`);
        if (wrapper) {
            wrapper.remove();
            renderedMessageIds.delete(data.mensaje_id);
            messageCache.delete(data.mensaje_id);
            console.log('[CHAT] ✅ Mensaje removido de UI');
        }
    }

    function handleMessagePinned(data) {
        if (!data || !data.mensaje_id) return;
        
        console.log('[CHAT] 📌 Mensaje fijado por WS:', data);
        
        // Obtener datos del mensaje desde cache o DOM
        let msgData = getFromCache(data.mensaje_id, currentConversationId);
        
        if (!msgData) {
            // Intentar obtener del DOM
            const wrapper = document.querySelector(`[data-message-id="${data.mensaje_id}"]`);
            if (wrapper) {
                const bubble = wrapper.querySelector('.message-bubble');
                const content = bubble.querySelector('div:not(.reply-context):not(.message-reaction)');
                msgData = {
                    id: data.mensaje_id,
                    contenido: content?.textContent || '[Mensaje]',
                    usuario_id: data.usuario_id,
                    usuario_nombre: data.usuario_nombre,
                    conversacion_id: currentConversationId
                };
            }
        } else {
            msgData.id = data.mensaje_id;
            msgData.conversacion_id = currentConversationId;
        }
        
        if (msgData) {
            showPinnedMessage(msgData);
            console.log('[CHAT] ✅ Mensaje fijado mostrado arriba');
        }
    }

    function handleMessageUnpinned(data) {
        if (!data || !data.mensaje_id) return;
        
        console.log('[CHAT] 📌 Mensaje desfijado por WS:', data);
        
        hidePinnedMessage();
        
        // Remover ícono del mensaje original
        const wrapper = document.querySelector(`[data-message-id="${data.mensaje_id}"]`);
        if (wrapper) {
            const pinIcon = wrapper.querySelector('.pin-icon');
            if (pinIcon) pinIcon.remove();
        }
        
        console.log('[CHAT] ✅ Mensaje desfijado de UI');
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

        // 2. Observar notificaciones inline (como en auditoría) - OPTIMIZADO CON MUTATIONOBSERVER
        function checkToastNotifications() {
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
        }

        // Usar MutationObserver en lugar de setInterval para mejor rendimiento
        const bodyObserver = new MutationObserver(() => {
            // Debounce: ejecutar después de 10ms de inactividad
            if (bodyObserver.timeout) clearTimeout(bodyObserver.timeout);
            bodyObserver.timeout = setTimeout(checkToastNotifications, 10);
        });

        bodyObserver.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });

        // Verificación inicial
        checkToastNotifications();

        console.log("[CHAT] Observador de notificaciones configurado (optimizado con MutationObserver)");
    }

    function init() {
        ensureSocket();
        startUnreadPolling();
        setupNotificationObserver();
        console.log("[CHAT] Chat flotante iniciado.");
    }

    return { init, openPanel, closePanel, updateUnreadCount, unpinMessage };

})();

if (typeof window !== "undefined") {
    window.ChatFloat = ChatFloat;
}

document.addEventListener("DOMContentLoaded", ChatFloat.init);
