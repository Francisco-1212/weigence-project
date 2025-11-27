// ============================================================
//  CHAT CORE — Capa WebSocket, sin UI
//  Responsable de:
//      - conectar/desconectar
//      - eventos del servidor
//      - envío de mensajes
//      - join/leave rooms
//      - callbacks globales
// ============================================================

const ChatCore = (() => {

    // ---------------------------------------------
    // Propiedades internas
    // ---------------------------------------------
    let socket = null;
    let conectado = false;
    let currentRoom = null;

    // Callbacks del UI
    let onMessageCallback = null;
    let onSeenCallback = null;
    let onJoinedCallback = null;
    let onErrorCallback = null;


    // ============================================================
    // INIT SOCKET
    // ============================================================

    function init() {
        if (socket) return socket;

        try {
            socket = io({
                transports: ["websocket"],
                reconnection: true,
            });

            // === eventos base ===
            socket.on("connect", () => {
                conectado = true;
                console.log("[WS] ✓ conectado");
            });

            socket.on("disconnect", () => {
                conectado = false;
                console.log("[WS] ✂ desconectado");
            });

            // === handshake backend ===
            socket.on("ws_connected", (data) => {
                console.log("[WS] sesión OK →", data);
            });

            // === mensajes nuevos ===
            socket.on("mensaje_nuevo", (msg) => {
                console.log("[WS] 📩 nuevo msg", msg);
                if (onMessageCallback) onMessageCallback(msg);
            });

            // === vistos ===
            socket.on("mensaje_visto", (data) => {
                console.log("[WS] 👀 visto", data);
                if (onSeenCallback) onSeenCallback(data);
            });

            // === join exitoso ===
            socket.on("joined", (data) => {
                console.log("[WS] 🚪 joined", data);
                if (onJoinedCallback) onJoinedCallback(data);
            });

            // === errores ===
            socket.on("error", (err) => {
                console.warn("[WS] ❗ error", err);
                if (onErrorCallback) onErrorCallback(err);
            });

        } catch (e) {
            console.error("[WS] FATAL init:", e);
        }

        return socket;
    }


    // ============================================================
    // JOIN ROOM
    // ============================================================

    function join(conversacion_id) {
        if (!socket) init();

        if (!conversacion_id) return;
        currentRoom = conversacion_id;

        socket.emit("join", { conversacion_id });
    }


    // ============================================================
    // SEND MESSAGE
    // ============================================================

    function send(texto) {
        if (!socket || !currentRoom) {
            console.warn("[WS] send > SIN ROOM O SOCKET");
            return;
        }

        socket.emit("send", {
            conversacion_id: currentRoom,
            contenido: texto,
        });
    }


    // ============================================================
    // MARK AS SEEN
    // ============================================================

    function seen(msg_id) {
        if (!socket || !currentRoom) return;

        socket.emit("seen", {
            conversacion_id: currentRoom,
            ultimo_id: msg_id,
        });
    }


    // ============================================================
    // UI CALLBACKS (inversión de control)
    // ============================================================

    function onMessage(cb) { onMessageCallback = cb; }
    function onSeen(cb) { onSeenCallback = cb; }
    function onJoined(cb) { onJoinedCallback = cb; }
    function onError(cb) { onErrorCallback = cb; }


    // ============================================================
    // API pública
    // ============================================================

    return {
        init,
        join,
        send,
        seen,

        onMessage,
        onSeen,
        onJoined,
        onError,
    };

})();
