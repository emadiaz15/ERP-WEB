import { create } from "zustand";
import { persist } from "zustand/middleware";
import {
  fetchNotifications,
  markNotificationRead,
  markAllNotificationsRead,
} from "../services/notifications.api";
import { getAccessToken } from "@/utils/sessionUtils";

// ✅ Booleano robusto
const toBool = (v) => {
  if (typeof v === "boolean") return v;
  if (typeof v === "number") return v !== 0;
  if (typeof v === "string") {
    const s = v.trim().toLowerCase();
    if (s === "true" || s === "1") return true;
    if (s === "false" || s === "0" || s === "") return false;
  }
  return Boolean(v);
};

const normalizeNotif = (raw = {}) => {
  // ✅ Aceptar múltiples alias de ID provenientes del backend/WS
  const rawId =
    raw.id ?? raw.uuid ?? raw.notification_id ?? raw.notificationId ?? raw.pk ?? raw._id;
  // ❌ Sin id, descartamos (no podremos deduplicar ni marcar leída)
  if (rawId == null) return null;

  const readRaw = raw.read ?? raw.is_read;
  const read = readRaw == null ? false : toBool(readRaw);

  // created_at con fallback y normalizado a ISO
  const created_at_raw =
    raw.created_at ?? raw.createdAt ?? raw.timestamp ?? raw.created ?? Date.now();
  const created_at = (() => {
    if (typeof created_at_raw === "number") return new Date(created_at_raw).toISOString();
    const d = new Date(created_at_raw);
    return isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString();
  })();

  return {
    // Forzamos 'id' normalizado para el store y UI
    ...raw,
    id: rawId,
    read,
    created_at,
    type: raw.type ?? raw.notif_type ?? "generic",
    notif_type: raw.notif_type ?? raw.type ?? "generic",
  };
};

// 🔁 Inserta o actualiza una notificación en lista
function upsert(list, notif) {
  const n = normalizeNotif(notif);
  if (!n) return list; // ← ignoramos sin id
  const index = list.findIndex((x) => String(x.id) === String(n.id));
  if (index === -1) return [n, ...list];
  const next = [...list];
  next[index] = { ...next[index], ...n };
  return next;
}

// 🧹 Elimina duplicados por ID, preservando orden
function dedupe(list) {
  const map = new Map();
  for (const raw of list) {
    const n = normalizeNotif(raw);
    if (!n) continue; // ← ignoramos sin id
    const k = String(n.id);
    if (!map.has(k)) map.set(k, n);
  }
  return Array.from(map.values());
}

// 🧮 Recalcula el número de no leídas
function recalculateUnread(items) {
  return items.reduce((acc, n) => (n.read ? acc : acc + 1), 0);
}

export const useNotificationsStore = create()(
  persist(
    (set, get) => ({
      items: [],
      unreadCount: 0,
      loading: false,
      page: 1,
      pageSize: 10,
      hasMore: true,
      lastFetchedAt: null,
      _debugFetches: 0,
      _debugApplied: 0,
      _debugDeduped: 0,

      // ✅ Push desde WebSocket
      pushFromWS: (notif) => {
        // Si ya existe y está leída localmente, nunca la volvemos a poner como no leída
        const prev = get().items.find((n) => String(n.id) === String(notif.id));
        let merged = notif;
        if (prev && prev.read) {
          merged = { ...notif, read: true };
        }
        const items = dedupe(upsert(get().items, merged));
        const unreadCount = recalculateUnread(items);
        set({ items, unreadCount });
      },

      // 📄 Cargar notificaciones paginadas
      fetchPage: async (page = 1, extraParams = {}) => {
        if (!getAccessToken()) {
          return { skipped: true };
        }
        const state = get();
        const page_size = extraParams.page_size ?? state.pageSize;
        // Build a stable key for dedupe (exclude volatile functions)
        const { read, type } = extraParams;
        const fetchKey = JSON.stringify({ page, page_size, read: read ?? null, type: type ?? null });
        const now = Date.now();
        // Simple throttling/deduplication window (2s) unless force specified
        if (!extraParams.force && state._lastFetchKey === fetchKey && (now - (state._lastFetchAt || 0)) < 2000) {
          set({ _debugDeduped: state._debugDeduped + 1 });
          return { deduped: true };
        }
        set({ loading: true, _debugFetches: state._debugFetches + 1 });
        try {
          const data = await fetchNotifications({ page, page_size, ...extraParams });

          // Mantener leídas locales aunque el backend mande read: false
          const prevMap = new Map(get().items.map(n => [String(n.id), n]));
          const mergedResults = data.results.map(n => {
            const prev = prevMap.get(String(n.id));
            if (prev && prev.read) return { ...n, read: true };
            return n;
          });
          const allItems = page === 1 ? mergedResults : [...get().items, ...mergedResults];
          let items = dedupe(allItems);

          // Filtros client-side si el backend no los soporta
          if (extraParams.read === true) {
            items = items.filter((n) => n.read === true);
          }
          if (extraParams.type) {
            items = items.filter((n) => (n.notif_type || n.type) === extraParams.type);
          }

          const unreadCount = recalculateUnread(items);
          const totalCount = typeof data.count === "number" ? data.count : 0;
          const hasMore = Boolean(data.next) && items.length < totalCount;

            // Idempotent guard: if nothing material changed, skip set() to avoid extra rerenders
            const prevState = get();
            const samePage = prevState.page === page;
            const sameLen = prevState.items.length === items.length;
            let sameContent = false;
            if (sameLen) {
              sameContent = prevState.items.every((prevItem, idx) => prevItem.id === items[idx].id && prevItem.read === items[idx].read);
            }
            const sameHasMore = prevState.hasMore === hasMore;
            const sameUnread = prevState.unreadCount === unreadCount;
            if (samePage && sameLen && sameContent && sameHasMore && sameUnread) {
              return data; // no-op
            }

          const nextState = {
            items,
            page: extraParams.noAdvance ? state.page : page,
            hasMore,
            lastFetchedAt: Date.now(),
            unreadCount,
            _lastFetchKey: fetchKey,
            _lastFetchAt: Date.now(),
          };
          set({ ...nextState, _debugApplied: state._debugApplied + 1 });
          return data;
        } catch (e) {
          console.error("[Notifications] Error en fetchPage", e);
        } finally {
          set({ loading: false });
        }
      },

      // ✅ Marcar una como leída
      markAsRead: async (id) => {
        try {
          await markNotificationRead(id);
          const items = get().items.map((n) =>
            String(n.id) === String(id)
              ? { ...n, read: true } // n ya está normalizado y con id
              : n
          );
          const unreadCount = recalculateUnread(items);
          set({ items, unreadCount });
        } catch (e) {
          console.error("[Notifications] Error en markAsRead", e);
          throw e;
        }
      },

      // ✅ Marcar todas como leídas
      markAllAsRead: async () => {
        try {
          await markAllNotificationsRead();
          const items = get().items.map((n) => ({ ...n, read: true }));
          const unreadCount = recalculateUnread(items);
          set({ items, unreadCount });
        } catch (e) {
          console.error("[Notifications] Error en markAllAsRead", e);
        }
      },

      // 🔄 Reset
      resetPagination: () => set({ items: [], page: 1, hasMore: true }),
    }),
    {
      name: "notifications-store",
      version: 2,
      migrate: (persisted) => {
        if (!persisted) return persisted;
        const items = (persisted.items || []).map(normalizeNotif).filter(Boolean);
        const unreadCount = recalculateUnread(items);
        return { ...persisted, items, unreadCount };
      },
      // guardamos lo justo (hasta 50)
      partialize: (state) => ({
        items: state.items.slice(0, 50),
        unreadCount: state.unreadCount,
        pageSize: state.pageSize,
      }),
    }
  )
);
