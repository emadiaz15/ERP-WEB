import React, { useEffect, useRef, useState, useCallback } from "react";
import SuccessMessage from "@/components/common/SuccessMessage";

// Muestra pequeños toasts de éxito cuando llegan eventos CRUD relevantes por WebSocket
// Actualmente: CuttingOrder create
export default function RealtimeToaster() {
  const [toasts, setToasts] = useState([]); // [{key, message}]
  const seenRef = useRef(new Set()); // evita duplicados por StrictMode o reintentos

  const closeToast = useCallback((key) => {
    setToasts((prev) => prev.filter((t) => t.key !== key));
  }, []);

  useEffect(() => {
    function handler(e) {
      const msg = e?.detail;
      if (!msg || !msg.model || !msg.event) return;

      // Solo interesa creación de órdenes de corte
      if (msg.model === "CuttingOrder" && msg.event === "create") {
        const id = msg?.payload?.id;
        const unique = `cutting:create:${id ?? "_"}`;
        if (seenRef.current.has(unique)) return;
        seenRef.current.add(unique);

        const message = id
          ? `Orden #${id} creada correctamente`
          : "Orden de corte creada correctamente";

        setToasts((prev) => [{ key: unique, message }, ...prev].slice(0, 4));
      }
    }

    window.addEventListener("realtime-crud-event", handler);
    return () => window.removeEventListener("realtime-crud-event", handler);
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-20 right-5 z-[10000] w-[min(420px,90vw)]">
      {toasts.map((t) => (
        <div key={t.key} className="mb-2">
          <SuccessMessage message={t.message} onClose={() => closeToast(t.key)} />
        </div>
      ))}
    </div>
  );
}
