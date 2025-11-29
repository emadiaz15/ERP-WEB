// src/features/notifications/components/NotificationsBridge.jsx
import { useNotificationsSocket } from "@/features/notifications/hooks/useNotificationsSocket";
import { useNotificationsStore } from "@/features/notifications/stores/useNotificationsStore";
import { getIsDev } from "@/features/notifications/hooks/wsEnv";

export default function NotificationsBridge() {
    const pushFromWS = useNotificationsStore((s) => s.pushFromWS);

    useNotificationsSocket((payload) => {
        if (!payload) return;

        // 👀 Debug en DEV para ver exactamente qué llega
    if (getIsDev()) {
            // Evitamos ruido con pings
            if (!((payload && payload.type === "pong") || (payload && payload.type === "__pong__"))) {
                // eslint-disable-next-line no-console
                console.log("[WS][msg]", payload);
            }
        }

        // Aceptamos varios formatos comunes
        // 1) Array de notificaciones
        if (Array.isArray(payload)) {
            payload.forEach((n) => pushFromWS(n));
            return;
        }

        // 2) { notification: {...} }
        if (payload.notification) {
            pushFromWS(payload.notification);
            return;
        }

        // 3) { data: {...} }  ← nuevo soporte
        if (payload.data) {
            pushFromWS(payload.data);
            return;
        }

        // 4) Objeto crudo que ya es la notificación
        pushFromWS(payload);

        // Broadcast para otras features (ej: Cutting Orders)
        try {
            if (typeof window !== "undefined") {
                if (payload?.type === "cutting_order_status" && payload?.order_id) {
                    window.dispatchEvent(new CustomEvent("cuttingOrder:status", { detail: payload }));
                }
            }
        } catch {
            // noop
        }
    });

    return null; // Se monta una sola vez post-auth
}
