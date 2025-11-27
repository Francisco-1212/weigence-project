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

    // UI callbacks
    let onMessageCallback = null;
    let onSeenCallback = null;
    let onJoinedCallback = null;
    let onErrorCallback = null;


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

            socket.on("disconnect", () => {
                conectado = false;
                console.log("[WS] desconectado");
            });

            // Backend handshake
            socket.on("ws_connected", (data) => {
                console.log("[WS] sesion OK", data);
            });

            // New messages
            socket.on("mensaje_nuevo", (msg) => {
                console.log("[WS] nuevo mensaje", msg);
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

            // Errors
            socket.on("error", (err) => {
                console.warn("[WS] error", err);
                // Si la sesion es invalida, reiniciamos el socket completo
                if (err && String(err.message || err).toLowerCase().includes("invalid session")) {
                    try {
                        socket.disconnect();
                    } catch (_) {}
                    socket = null;
                    conectado = false;
                    init();
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

    function send(texto) {
        const contenido = (texto || "").trim();
        if (!contenido) {
            console.warn("[WS] send > texto vacio");
            return;
        }

        if (!socket || !conectado || !currentRoom) {
            console.warn("[WS] send > sin room o sin conexion");
            return;
        }

        socket.emit("send", {
            conversacion_id: currentRoom,
            contenido,
        });
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
    };

})();

if (typeof window !== "undefined") {
    window.ChatCore = ChatCore;
}
