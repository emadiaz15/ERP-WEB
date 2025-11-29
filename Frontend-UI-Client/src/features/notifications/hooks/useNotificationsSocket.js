
import { useEffect, useRef } from "react";
import { getAccessToken } from "@/utils/sessionUtils";
import { getIsDev, getWsUrlNotifications, getApiBaseUrl } from "@/features/notifications/hooks/wsEnv";
import { WSClient } from "@/lib/wsClient";

export function useNotificationsSocket(onMessage) {
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const heartbeatTimerRef = useRef(null);
  const connectingRef = useRef(false);
  const closedByUserRef = useRef(false);
  const backoffRef = useRef(0);
  const handlerRef = useRef(onMessage);

  useEffect(() => {
    handlerRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    const isDev = getIsDev();
    const WS_DEBUG = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_WS_DEBUG === 'true');

    const normalizeWsOrigin = (raw) => {
      if (!raw) return null;
      let out = raw.trim();
      out = out.replace(/\/$/, "");
      try {
        const u = new URL(out, window.location.origin);
        if (u.protocol === "http:" || u.protocol === "https:") {
          const wsProto = u.protocol === "https:" ? "wss" : "ws";
          return `${wsProto}://${u.host}${u.pathname || ''}`.replace(/\/$/, "");
        }
        if (u.protocol === "ws:" || u.protocol === "wss:") {
          return `${u.protocol}//${u.host}${u.pathname || ''}`.replace(/\/$/, "");
        }
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        return `${wsProto}://${u.host}${u.pathname || ''}`.replace(/\/$/, "");
      } catch {
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        if (out.startsWith("/")) return `${wsProto}://${window.location.host}${out}`.replace(/\/$/, "");
        return `${wsProto}://${out}`.replace(/\/$/, "");
      }
    };

    const computeWsBase = () => {
      const rawWs = getWsUrlNotifications();
      if (rawWs) return normalizeWsOrigin(rawWs);
      const api = getApiBaseUrl();
      if (api) {
        try {
          const u = new URL(api, window.location.origin);
          const proto = u.protocol === "https:" ? "wss" : "ws";
          return `${proto}://${u.host}`;
        } catch {}
      }
      const proto = window.location.protocol === "https:" ? "wss" : "ws";
      return `${proto}://${window.location.host}`;
    };

    // Construye la URL con token fresco y sin barra final
    function buildUrlWithToken(t) {
      const base = computeWsBase();
      const safeBase = normalizeWsOrigin(base);
      const endsWithWSPath = /\/ws\/notifications$/.test(safeBase);
      const urlBase = endsWithWSPath ? safeBase : `${safeBase}/ws/notifications`;
      const u = new URL(urlBase);
      u.searchParams.set("token", t); // middleware lee ?token=
      return u.toString();
    }

    function clearHeartbeat() {
      if (heartbeatTimerRef.current) {
        clearInterval(heartbeatTimerRef.current);
        heartbeatTimerRef.current = null;
      }
    }

    function cleanup() {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      clearHeartbeat();
      if (wsRef.current) {
        try {
          const st = wsRef.current.readyState;
          if (st === WebSocket.OPEN || st === WebSocket.CONNECTING) {
            wsRef.current.close(1000, "unmount");
          }
        } catch {}
        wsRef.current = null;
      }
      connectingRef.current = false;
    }

    function scheduleReconnect() {
      if (closedByUserRef.current) return;
      const tries = backoffRef.current;
      const delay =
        Math.min(30000, 1000 * Math.pow(2, tries)) + Math.floor(Math.random() * 300);
      reconnectTimerRef.current = setTimeout(connect, delay);
      backoffRef.current = Math.min(tries + 1, 10);
  if (isDev || WS_DEBUG) console.log(`[WS] 🔁 Reintentando en ${Math.round(delay / 1000)}s...`);
    }

    function startHeartbeat() {
      clearHeartbeat();
      heartbeatTimerRef.current = setInterval(() => {
        try {
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "ping" }));
          }
        } catch {}
      }, 25000);
    }

    function safeLogUrl(u) {
      // Log sin token (enmascara el query param)
      try {
        const parsed = new URL(u, window.location.origin);
        if (parsed.searchParams.has("token")) {
          parsed.searchParams.set("token", "…token…");
          return parsed.toString();
        }
        return parsed.toString();
      } catch {
        return u.replace(/(token=)[^&]+/, "$1…token…");
      }
    }

    // Simplified: use generic WSClient
    const client = new WSClient({
      url: buildUrlWithToken(''), // token appended dynamically each connect
      getToken: () => getAccessToken(),
      maxRetries: 3,
      baseDelayMs: 1000,
      onOpen: () => { if (isDev || WS_DEBUG) console.log('[WS] ✅ Conectado'); startHeartbeat(); },
      onMessage: (data) => {
        if (data && typeof data === 'object' && (data.type === 'pong' || data.type === '__pong__')) return;
        handlerRef.current?.(data);
      },
      onClose: (evt) => {
        clearHeartbeat();
        if (isDev || WS_DEBUG) console.warn(`[WS] 🔌 Cerrado (code=${evt.code}, reason=${evt.reason})`);
      }
    });
    wsRef.current = client; // reuse ref for shutdown compatibility
    client.connect();

    return () => {
      closedByUserRef.current = true;
      try { wsRef.current?.shutdown?.(); } catch(_) {}
      cleanup();
    };
  }, []);
}
