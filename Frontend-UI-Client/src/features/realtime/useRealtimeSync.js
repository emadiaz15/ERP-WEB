// src/features/realtime/useRealtimeSync.js
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useCrudEventsSocket } from "@/features/realtime/useCrudEventsSocket";


export function useRealtimeSync({ enabled = true } = {}) {
  const qc = useQueryClient();
  // Ventana de silenciamiento para invalidaciones repetidas
  const dedupeMap = (typeof window !== 'undefined') ? (window.__crudDedupeMap ||= new Map()) : new Map();
  const shouldDedupe = (key, ttlMs = 700) => {
    const now = Date.now();
    const last = dedupeMap.get(key) || 0;
    if (now - last < ttlMs) return true;
    dedupeMap.set(key, now);
    return false;
  };

  // Helpers para actualizar caches de useInfiniteQuery (pages/results)
  const prependToInfiniteList = (rootKey, item) => {
    qc.setQueriesData({ queryKey: [rootKey], type: "active", exact: false }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      const pages = old.pages.slice();
      if (!pages[0]) return old;
      const first = pages[0] || {};
      const results = Array.isArray(first.results) ? first.results : [];
      pages[0] = {
        ...first,
        results: [item, ...results],
        count: typeof first.count === "number" ? first.count + 1 : first.count,
      };
      return { ...old, pages };
    });
  };

  const replaceInInfiniteList = (rootKey, item, idKey = "id") => {
    qc.setQueriesData({ queryKey: [rootKey], type: "active", exact: false }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      let replaced = false;
      const pages = old.pages.map((p) => {
        const results = Array.isArray(p?.results)
          ? p.results.map((r) => {
              if (r?.[idKey] === item?.[idKey]) {
                replaced = true;
                // Mezclar para no perder campos no incluidos en el payload WS
                return { ...r, ...item };
              }
              return r;
            })
          : p?.results;
        return { ...p, results };
      });
      return replaced ? { ...old, pages } : old;
    });
  };

  const removeFromInfiniteList = (rootKey, id, idKey = "id") => {
    qc.setQueriesData({ queryKey: [rootKey], type: "active", exact: false }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      let removed = false;
      const pages = old.pages.map((p) => {
        const before = Array.isArray(p?.results) ? p.results.length : 0;
        const results = Array.isArray(p?.results) ? p.results.filter((r) => r?.[idKey] !== id) : p?.results;
        if (Array.isArray(p?.results) && results.length !== before) removed = true;
        return {
          ...p,
          results,
          count: typeof p.count === "number" ? Math.max(0, p.count - (before - (results?.length ?? 0))) : p.count,
        };
      });
      return removed ? { ...old, pages } : old;
    });
  };

  // Upsert en caches de detalle para un ítem por id
  const upsertDetailById = (rootKey, item, idKey = "id") => {
    const id = item?.[idKey];
    if (id == null) return;
    // Actualiza queries tipo [rootKey, 'detail', id] o [rootKey, id]
    qc.setQueriesData(
      {
        predicate: (q) => {
          const k = q.queryKey;
          if (!Array.isArray(k)) return false;
          if (k[0] !== rootKey) return false;
          // ['products','detail', id]
          if (k[1] === 'detail' && k[2] === id) return true;
          // ['products', id]
          if (k.length === 2 && k[1] === id) return true;
          return false;
        },
      },
      (old) => (old ? { ...old, ...item } : item)
    );
  };

  const removeDetailById = (rootKey, id) => {
    qc.removeQueries({
      predicate: (q) => {
        const k = q.queryKey;
        if (!Array.isArray(k)) return false;
        if (k[0] !== rootKey) return false;
        if (k[1] === 'detail' && k[2] === id) return true;
        if (k.length === 2 && k[1] === id) return true;
        return false;
      },
    });
  };

  function onMessage(msg) {
    console.log("[RealtimeSync] WS EVENT RECEIVED:", msg);
    if (!msg || !msg.model || !msg.event) return;

    // Generalizar con mapeo a keys reales del cache
    const model = msg.model;
    const modelToKey = {
      Product: "products",
      Category: "categories",
      CuttingOrder: "cuttingOrders",
      Notification: "notifications",
      User: "users",
      StockEvent: "stocks",
      Subproduct: "products", // subproductos viven bajo products/*
    };
    const rootKey = modelToKey[model] || (model ? `${model.toLowerCase()}s` : null);
    if (!rootKey) return;

    // Casos especiales
    if (model === "Subproduct") {
      // Claves reales están anidadas bajo ["products", productId, "subproducts", ...]
      // Intentar invalidación dirigida por productId si viene en el payload
      const p = msg.payload || {};
      const productId = p.product_id ?? p.productId ?? p.product?.id ?? p.parent_id ?? p.parentId ?? null;
      if (productId != null) {
        qc.invalidateQueries({
          predicate: (q) => {
            const k = q.queryKey;
            if (!Array.isArray(k)) return false;
            if (!(k[0] === 'products' && k[1] === productId)) return false;
            if (!k.includes('subproducts')) return false;
            // Excluir archivos para no spamear /files
            if (k.includes('files')) return false;
            return true;
          },
        });
      } else {
        // Fallback amplio si no podemos extraer productId
        qc.invalidateQueries({ queryKey: ["products"], exact: false });
      }
      window.dispatchEvent(new CustomEvent("realtime-crud-event", { detail: msg }));
      return;
    }
    if (model === "StockEvent") {
      // Invalida listados de eventos de stock tanto para productos como subproductos
      qc.invalidateQueries({
        predicate: (q) => {
          const k = q.queryKey;
          return (
            Array.isArray(k) &&
            (k[0] === 'stockProductEvents' || k[0] === 'stockSubproductEvents')
          );
        },
      });
      window.dispatchEvent(new CustomEvent("realtime-crud-event", { detail: msg }));
      return;
    }

    if (msg.event === "create") {
      const item = msg.payload;
      prependToInfiniteList(rootKey, item);
      upsertDetailById(rootKey, item);
      // Caso especial: CuttingOrder usa clave de detalle ['cuttingOrder', id]
      if (model === 'CuttingOrder' && item?.id != null) {
        qc.setQueryData(['cuttingOrder', item.id], (old) => (old ? { ...old, ...item } : item));
      }
      // Evitar invalidar queries de archivos (e.g., ['products','files',id]) para no spamear /files/
      qc.invalidateQueries({
        predicate: (q) => {
          const k = q.queryKey;
          if (!Array.isArray(k)) return false;
          if (k[0] !== rootKey) return false;
          // Excluir claves de archivos bajo products
          if (k[0] === 'products' && k[1] === 'files') return false;
          return true;
        },
        refetchType: 'active',
      });
    }
    if (msg.event === "update") {
      const item = msg.payload;
      replaceInInfiniteList(rootKey, item);
      upsertDetailById(rootKey, item);
      if (model === 'CuttingOrder' && item?.id != null) {
        qc.setQueryData(['cuttingOrder', item.id], (old) => (old ? { ...old, ...item } : item));
      }
      // Importante: si cambian campos que afectan filtros/orden (ej. name),
      // necesitamos refetchear listas para recomputar membresía de resultados.
      // Refrescar todas las listas activas del modelo
      // Pequeño retraso para evitar carrera con invalidación de caché en el backend
      const dedupeKey = `${model}:update:${item?.id ?? 'unknown'}`;
      if (shouldDedupe(dedupeKey)) return;
      setTimeout(() => {
        qc.invalidateQueries({
          predicate: (q) => {
            const k = q.queryKey;
            if (!Array.isArray(k)) return false;
            if (k[0] !== rootKey) return false;
            if (k[0] === 'products' && k[1] === 'files') return false; // no refrescar /files
            return true;
          },
          refetchType: 'active',
        });
  }, 300);
    }
    if (msg.event === "delete") {
      const id = msg.payload?.id;
      removeFromInfiniteList(rootKey, id);
      removeDetailById(rootKey, id);
      if (model === 'CuttingOrder' && id != null) {
        qc.removeQueries({ queryKey: ['cuttingOrder', id], exact: true });
      }
      // Refrescar listas activas del modelo para sacar el eliminado en vistas filtradas (excluye /files)
      qc.invalidateQueries({
        predicate: (q) => {
          const k = q.queryKey;
          if (!Array.isArray(k)) return false;
          if (k[0] !== rootKey) return false;
          if (k[0] === 'products' && k[1] === 'files') return false;
          return true;
        },
        refetchType: 'active',
      });
    }

    // Emitir evento global para integración con otros hooks
    window.dispatchEvent(new CustomEvent("realtime-crud-event", { detail: msg }));
  }

  // Suscripción sólo a CRUD events (notificaciones se manejan en NotificationsBridge)
  // Evitar ruido por StrictMode en dev (doble montaje). Solo loguear una vez.
  const WS_DEBUG = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_WS_DEBUG === 'true');
  if (!window.__crud_ws_logged_once && WS_DEBUG) {
    window.__crud_ws_logged_once = true;
    console.log("[RealtimeSync] Subscribing to CRUD events WebSocket...");
  }
  useCrudEventsSocket(onMessage, { enabled });
}
