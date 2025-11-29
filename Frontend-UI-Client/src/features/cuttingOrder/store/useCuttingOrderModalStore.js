// src/features/cuttingOrder/store/useCuttingOrderModalStore.js
import { create } from "zustand";
import { getCuttingOrder } from "@/features/cuttingOrder/services/cuttingOrders";

export const useCuttingOrderModalStore = create((set) => ({
  isOpen: false,
  order: null,
  loading: false,
  open: async (orderOrId) => {
    set({ loading: true, isOpen: true });
    let order = orderOrId;
    if (typeof orderOrId === "number" || typeof orderOrId === "string") {
      try {
        order = await getCuttingOrder(orderOrId);
      } catch (e) {
        order = null;
      }
    }
    set({ order, isOpen: true, loading: false });
  },
  close: () => set({ isOpen: false, order: null, loading: false }),
}));
