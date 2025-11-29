import { useEffect, useRef, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import NotificationToast from "./NotificationToast";
import { useNotificationsStore } from "../stores/useNotificationsStore";

/**
 * Muestra popups apilados por ~10s cuando llegan notificaciones nuevas (WS).
 * - No inunda al montar: ignora las existentes al primer render.
 * - Evita duplicados con un Set de ids vistos.
 * - Máximo 4 concurrentes en pantalla (FIFO).
 */
export default function NotificationsToaster() {
    const navigate = useNavigate();
    const items = useNotificationsStore((s) => s.items);
    const markAsRead = useNotificationsStore((s) => s.markAsRead);

    const [toasts, setToasts] = useState([]); // [{id, notif}]
    const seenIdsRef = useRef(new Set());
    const timersRef = useRef(new Map()); // Map<id, timeoutId>
    const initializedRef = useRef(false);

    // Limpia un toast y su timer
    const closeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
        const timeoutId = timersRef.current.get(id);
        if (timeoutId) {
            clearTimeout(timeoutId);
            timersRef.current.delete(id);
        }
    }, []);

    // Lógica de navegación para "Ver más"
    const handleView = useCallback(
        async (notif) => {
            try {
                if (!notif.read && notif.id) {
                    await markAsRead(notif.id);
                }
            } catch {
                /* noop */
            }

            if (notif?.payload?.order_id) {
                navigate(`/cutting-orders/${notif.payload.order_id}`);
            } else if (notif?.target_url) {
                navigate(notif.target_url);
            } else {
                navigate("/notifications");
            }
        },
        [markAsRead, navigate]
    );

    // Al cambiar items del store, agrega toasts solo para nuevas notifs (post-mount)
    useEffect(() => {
        if (!initializedRef.current) {
            initializedRef.current = true;
            // marcar existentes como vistas (solo con id válido)
            for (const n of items) {
                if (n?.id != null) seenIdsRef.current.add(n.id);
            }
            return;
        }

        // Solo notifs con id y no vistas
        const fresh = items.filter((n) => n?.id != null && !seenIdsRef.current.has(n.id));
        if (fresh.length === 0) return;

        setToasts((prev) => {
            let next = [...prev];
            for (const n of fresh) {
                // Si por alguna razón el batch 'fresh' contiene duplicados con el mismo id,
                // evitamos añadirlos múltiples veces comprobando además el seenIdsRef.
                if (seenIdsRef.current.has(n.id)) continue;
                seenIdsRef.current.add(n.id);
                // push al frente para que la más nueva quede arriba (límite 4)
                next = [{ id: n.id, notif: n }, ...next].slice(0, 4);
            }
            return next;
        });
    }, [items]);

    // Timers de autocierre (~10s) para cada toast en pantalla
    useEffect(() => {
        for (const toast of toasts) {
            if (!timersRef.current.has(toast.id)) {
                const timeoutId = setTimeout(() => closeToast(toast.id), 10_000);
                timersRef.current.set(toast.id, timeoutId);
            }
        }
        // cleanup de timers huérfanos
        const idsInUi = new Set(toasts.map((t) => t.id));
        for (const [id, timeoutId] of timersRef.current.entries()) {
            if (!idsInUi.has(id)) {
                clearTimeout(timeoutId);
                timersRef.current.delete(id);
            }
        }
    }, [toasts, closeToast]);

    // Limpieza total al desmontar
    useEffect(() => {
        const timersMap = timersRef.current; // snapshot para el cleanup
        return () => {
            for (const timeoutId of timersMap.values()) clearTimeout(timeoutId);
            timersMap.clear();
        };
    }, []);

    if (toasts.length === 0) return null;

    return (
        <div className="fixed right-4 z-[9999] w-[min(420px,90vw)] top-20 md:top-24">
            {toasts.map(({ id, notif }) => (
                <NotificationToast
                    key={`${id}-${notif?.created_at ?? ""}`}
                    notif={notif}
                    onClose={() => closeToast(id)}
                    onView={() => {
                        closeToast(id);
                        handleView(notif);
                    }}
                />
            ))}
        </div>
    );
}
