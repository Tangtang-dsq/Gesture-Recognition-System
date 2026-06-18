export function createGestureSocket({ onResult, onStatus }) {
  const protocol = location.protocol === "https:" ? "wss" : "ws";
  const explicit = import.meta.env.VITE_WS_URL;
  const url = explicit ?? `${protocol}://${location.host}/ws/recognize`;
  let ws;
  let closed = false;
  let retry = 0;

  function connect() {
    onStatus?.("connecting");
    ws = new WebSocket(url);
    ws.onopen = () => {
      retry = 0;
      onStatus?.("connected");
    };
    ws.onmessage = (event) => onResult?.(JSON.parse(event.data));
    ws.onerror = () => onStatus?.("error");
    ws.onclose = () => {
      if (closed) return;
      onStatus?.("reconnecting");
      window.setTimeout(connect, Math.min(8000, 500 * 2 ** retry));
      retry += 1;
    };
  }

  connect();

  return {
    send(message) {
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
      }
    },
    close() {
      closed = true;
      ws?.close();
    },
  };
}
