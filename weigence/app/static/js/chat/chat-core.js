// ============================================================
//  CHAT CORE - WebSocket layer (no UI)
//  Responsible for:
//      - connect/disconnect
//      - server events
//      - send messages
//      - join/leave rooms
//      - UI callbacks
// ============================================================

const ChatCore = (() => {

    // Internal state
    let socket = null;
    let conectado = false;
    let currentRoom = null;
    let loadingClient = false;
    const pendingReplyTo = new Map(); // Guardar reply_to temporalmente: conversacion_id -> reply_to_id

    // UI callbacks
    let onMessageCallback = null;
    let onSeenCallback = null;
    let onJoinedCallback = null;
    let onErrorCallback = null;
    let onReactionCallback = null;
    let onDeleteCallback = null;
    let onPinCallback = null;
    let onUnpinCallback = null;


    // ============================================================
    // INIT SOCKET
    // ============================================================

    function ensureClientLoaded() {
        if (typeof io !== "undefined") return true;
        if (loadingClient) return false;

        loadingClient = true;
        const script = document.createElement("script");
        script.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";
        script.crossOrigin = "anonymous";
        script.onload = () => {
            console.log("[WS] socket.io client cargado desde CDN");
            loadingClient = false;
            init();
        };
        script.onerror = () => {
            console.warn("[WS] No se pudo cargar socket.io client (CDN)");
            loadingClient = false;
        };
        document.head.appendChild(script);
        return false;
    }

    function init() {
        if (socket) return socket;

        if (typeof io === "undefined") {
            console.warn("[WS] socket.io client no encontrado, cargando CDN...");
            if (!ensureClientLoaded()) return null;
        }

        try {
            socket = io({
                // Forzamos polling para evitar errores cuando el servidor no soporta WebSocket (e.g. livereload)
                transports: ["polling"],
                upgrade: false,
                reconnection: true,
                reconnectionDelay: 1000,
                reconnectionDelayMax: 5000,
                reconnectionAttempts: 5,
                timeout: 10000,
                // Evitar auto-conectar si la sesión no es válida
                autoConnect: true,
                forceNew: false
            });

            // Base events
            socket.on("connect", () => {
                conectado = true;
                console.log("[WS] conectado");

                // Auto rejoin if room was selected before reconnect
                if (currentRoom) {
                    socket.emit("join", { conversacion_id: currentRoom });
                }
            });

            socket.on("disconnect", (reason) => {
                conectado = false;
                console.log("[WS] desconectado:", reason);
                
                // Si la desconexión fue por error de transporte o sesión inválida, no intentar reconectar automáticamente
                if (reason === 'io server disconnect' || reason === 'transport close') {
                    console.warn("[WS] Desconexión por servidor, esperando reconexión manual");
                }
            });
            
            socket.on("connect_error", (error) => {
                console.warn("[WS] Error de conexión:", error.message);
                // No hacer nada especial, socket.io manejará los reintentos automáticamente
            });
            
            socket.on("reconnect_attempt", (attempt) => {
                console.log(`[WS] Intento de reconexión ${attempt}/5`);
            });
            
            socket.on("reconnect_failed", () => {
                console.error("[WS] Reconexión fallida después de varios intentos");
                conectado = false;
            });

            // Backend handshake
            socket.on("ws_connected", (data) => {
                console.log("[WS] sesion OK", data);
            });

            // New messages
            socket.on("mensaje_nuevo", (msg) => {
                console.log("[WS] nuevo mensaje", msg);
                
                // Si hay un reply_to pendiente para esta conversación y el mensaje no lo trae, agregarlo
                if (msg.conversacion_id && pendingReplyTo.has(msg.conversacion_id)) {
                    if (!msg.reply_to && msg.usuario_id === (window.CURRENT_USER?.id)) {
                        msg.reply_to = pendingReplyTo.get(msg.conversacion_id);
                        console.log('[WS] ✨ Reply_to inyectado al mensaje:', msg.reply_to);
                    }
                    // Limpiar después de usar
                    pendingReplyTo.delete(msg.conversacion_id);
                }
                
                if (onMessageCallback) onMessageCallback(msg);
            });

            // Seen
            socket.on("mensaje_visto", (data) => {
                console.log("[WS] mensaje visto", data);
                if (onSeenCallback) onSeenCallback(data);
            });

            // Join success
            socket.on("joined", (data) => {
                console.log("[WS] joined", data);
                if (onJoinedCallback) onJoinedCallback(data);
            });

            // Reacción agregada
            socket.on("reaccion_agregada", (data) => {
                console.log("[WS] reacción agregada", data);
                if (onReactionCallback) onReactionCallback(data);
            });

            // Mensaje eliminado
            socket.on("mensaje_eliminado", (data) => {
                console.log("[WS] mensaje eliminado", data);
                if (onDeleteCallback) onDeleteCallback(data);
            });

            // Mensaje fijado
            socket.on("mensaje_fijado", (data) => {
                console.log("[WS] mensaje fijado", data);
                if (onPinCallback) onPinCallback(data);
            });

            // Mensaje desfijado
            socket.on("mensaje_desfijado", (data) => {
                console.log("[WS] mensaje desfijado", data);
                if (onUnpinCallback) onUnpinCallback(data);
            });

            // Errors
            socket.on("error", (err) => {
                console.warn("[WS] error", err);
                
                // No reiniciar el socket por errores de sesión inválida
                // El servidor ya rechazó la conexión, simplemente loguear
                const errorMsg = String(err.message || err).toLowerCase();
                if (errorMsg.includes("invalid session") || errorMsg.includes("session not found")) {
                    console.warn("[WS] Sesión inválida detectada - El servidor rechazó la conexión");
                    conectado = false;
                    // No llamar a init() aquí, dejar que el usuario refresque la página
                    return;
                }
                
                if (onErrorCallback) onErrorCallback(err);
            });

        } catch (e) {
            console.error("[WS] FATAL init:", e);
        }

        return socket;
    }


    // ============================================================
    // JOIN / LEAVE ROOM
    // ============================================================

    function join(conversacionId) {
        if (!socket) init();
        if (!conversacionId) {
            console.warn("[WS] join > conversacion_id invalido");
            return;
        }

        // Normalizar a string para comparaciones consistentes
        currentRoom = String(conversacionId);

        if (!conectado) {
            console.warn("[WS] join > sin conexion, se reintentara al reconectar");
            return;
        }

        socket.emit("join", { conversacion_id: conversacionId });
    }

    function leave() {
        if (!socket || !currentRoom) return;

        try {
            socket.emit("leave", { conversacion_id: currentRoom });
        } catch (err) {
            console.warn("[WS] leave > error", err);
        }

        currentRoom = null;
    }


    // ============================================================
    // SEND MESSAGE
    // ============================================================

    function send(texto, replyTo = null) {
        const contenido = (texto || "").trim();
        if (!contenido) {
            console.warn("[WS] send > texto vacio");
            return;
        }

        if (!socket || !conectado || !currentRoom) {
            console.warn("[WS] send > sin room o sin conexion");
            return;
        }

        const payload = {
            conversacion_id: currentRoom,
            contenido,
        };

        // Agregar reply_to si existe
        if (replyTo) {
            payload.reply_to = replyTo;
            // Guardar temporalmente para inyectar cuando llegue la respuesta
            pendingReplyTo.set(currentRoom, replyTo);
            console.log('[WS] 💾 Reply_to guardado temporalmente:', replyTo);
        }

        socket.emit("send", payload);
    }


    // ============================================================
    // MARK AS SEEN
    // ============================================================

    function seen(msgId) {
        if (!socket || !conectado || !currentRoom) return;
        if (!msgId) return;

        socket.emit("seen", {
            conversacion_id: currentRoom,
            ultimo_id: msgId,
        });
    }


    // ============================================================
    // UI CALLBACKS (inversion de control)
    // ============================================================

    function onMessage(cb) { onMessageCallback = cb; }
    function onSeen(cb) { onSeenCallback = cb; }
    function onJoined(cb) { onJoinedCallback = cb; }
    function onError(cb) { onErrorCallback = cb; }
    function onReaction(cb) { onReactionCallback = cb; }
    function onDelete(cb) { onDeleteCallback = cb; }
    function onPin(cb) { onPinCallback = cb; }
    function onUnpin(cb) { onUnpinCallback = cb; }


    // ============================================================
    // Public API
    // ============================================================

    return {
        init,
        join,
        leave,
        send,
        seen,

        isConnected: () => conectado,
        currentRoom: () => currentRoom,

        onMessage,
        onSeen,
        onJoined,
        onError,
        onReaction,
        onDelete,
        onPin,
        onUnpin,
    };

})();

if (typeof window !== "undefined") {
    window.ChatCore = ChatCore;
}
