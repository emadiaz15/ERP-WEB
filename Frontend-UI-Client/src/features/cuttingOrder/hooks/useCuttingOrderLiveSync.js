import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Hook para escuchar eventos de workflow_status de órdenes de corte por WebSocket
 * e invalidar automáticamente las queries de TanStack Query.
 */
export function useCuttingOrderLiveSync() {
  const queryClient = useQueryClient();

  useEffect(() => {
    function handler(ev) {
      const msg = ev?.detail;
      if (msg?.order_id) {
        queryClient.invalidateQueries({ queryKey: ["cuttingOrders"] });
        queryClient.invalidateQueries({ queryKey: ["cuttingOrder", msg.order_id] });
      }
    }
    window.addEventListener("cuttingOrder:status", handler);
    return () => window.removeEventListener("cuttingOrder:status", handler);
  }, [queryClient]);
}
