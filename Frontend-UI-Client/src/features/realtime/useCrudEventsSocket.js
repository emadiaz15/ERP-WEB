import { useEffect, useRef } from "react";
import { getAccessToken } from "@/utils/sessionUtils";
import { getIsDev, getWsUrlCrudEvents, getApiBaseUrl } from "@/features/notifications/hooks/wsEnv";
import { WSClient } from "@/lib/wsClient";

export function useCrudEventsSocket(onMessage, { enabled = true } = {}) {
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

    const normalizeWsOrigin = (raw, fallbackPath) => {
      if (!raw) return null;
      let out = raw.trim();
      // quita barra final
      out = out.replace(/\/$/, "");
      try {
        const u = new URL(out, window.location.origin);
        // Si vino http/https, convertir a ws/wss
        if (u.protocol === "http:" || u.protocol === "https:") {
          const wsProto = u.protocol === "https:" ? "wss" : "ws";
          return `${wsProto}://${u.host}${u.pathname || ''}`.replace(/\/$/, "");
        }
        // Si ya es ws/wss, devolver host + path normalizado
        if (u.protocol === "ws:" || u.protocol === "wss:") {
          return `${u.protocol}//${u.host}${u.pathname || ''}`.replace(/\/$/, "");
        }
        // Si por algún motivo no hay protocolo, asume según location
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        return `${wsProto}://${u.host}${u.pathname || ''}`.replace(/\/$/, "");
      } catch {
        // Si es un string sin protocolo ni host, asume mismo host
        const wsProto = window.location.protocol === "https:" ? "wss" : "ws";
        if (out.startsWith("/")) return `${wsProto}://${window.location.host}${out}`.replace(/\/$/, "");
        // Si es solo host:puerto
        return `${wsProto}://${out}`.replace(/\/$/, "");
      }
    };

    const computeWsBase = () => {
      const rawWs = getWsUrlCrudEvents();
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

    const buildUrlWithToken = (t) => {
      const base = computeWsBase();
      // Asegurar protocolo ws/wss aunque env pase http(s)
      const safeBase = normalizeWsOrigin(base);
      const endsWithWSPath = /\/ws\/crud-events$/.test(safeBase);
      const urlBase = endsWithWSPath ? safeBase : `${safeBase}/ws/crud-events`;
      const u = new URL(urlBase);
      u.searchParams.set("token", t);
      return u.toString();
    };

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
  if (isDev || WS_DEBUG) console.log(`[WS-CRUD] 🔁 Reintentando en ${Math.round(delay / 1000)}s...`);
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

    if (!enabled) {
      closedByUserRef.current = true;
      cleanup();
      return () => {
        closedByUserRef.current = true;
        cleanup();
      };
    }

    const client = new WSClient({
      url: buildUrlWithToken(''),
      getToken: () => getAccessToken(),
      maxRetries: 3,
      baseDelayMs: 1000,
      onOpen: () => { if (isDev || WS_DEBUG) console.log('[WS-CRUD] ✅ Conectado'); startHeartbeat(); },
      onMessage: (data) => {
        if (data && typeof data === 'object' && (data.type === 'pong' || data.type === '__pong__')) return;
        handlerRef.current?.(data);
      },
      onClose: (evt) => { clearHeartbeat(); if (isDev || WS_DEBUG) console.warn(`[WS-CRUD] 🔌 Cerrado (code=${evt.code}, reason=${evt.reason})`); }
    });
    wsRef.current = client;
    client.connect();

    return () => {
      closedByUserRef.current = true;
      try { wsRef.current?.shutdown?.(); } catch(_) {}
      cleanup();
    };
  }, [enabled]);
}
