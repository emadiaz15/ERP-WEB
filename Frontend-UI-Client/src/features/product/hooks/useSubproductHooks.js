import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import {
  listSubproducts,
  createSubproduct,
  updateSubproduct,
  deleteSubproduct,
} from "@/features/product/services/subproducts/subproducts";
import { productKeys } from "@/features/product/utils/queryKeys.js";

/**
 * 1️⃣ Listar subproductos (paginado) con prefetch automático y filtros.
 * Actualiza automáticamente la cache en tiempo real si hay eventos WebSocket de subproductos.
 */
export function useListSubproducts(productId, pageUrl = null, filters = {}) {
  const qc = useQueryClient();
  const listKey = productKeys.subproductList(productId, pageUrl, filters);

  const query = useQuery({
    queryKey: listKey,
    queryFn: () => listSubproducts(productId, pageUrl, filters),
    enabled: !!productId,
    keepPreviousData: true,
    staleTime: 5 * 60_000,
    cacheTime: 10 * 60_000,
    refetchOnWindowFocus: false,
  });

  // Prefetch siguiente página (con los mismos filtros)
  const prefetchPage = (nextUrl) => {
    if (!nextUrl) return;
    const nextKey = productKeys.subproductList(productId, nextUrl, filters);
    qc.prefetchQuery({
      queryKey: nextKey,
      queryFn: () => listSubproducts(productId, nextUrl, filters),
    });
  };

  // Realtime: invalidar queries si hay evento WebSocket de subproducto
  useEffect(() => {
    function handleRealtimeSubproductEvent(e) {
      const msg = e.detail;
      if (msg?.model === "Subproduct") {
        qc.invalidateQueries({
          predicate: (q) =>
            productKeys.prefixMatch(q.queryKey) &&
            q.queryKey[0] === "products" &&
            q.queryKey[1] === productId &&
            q.queryKey.includes("subproducts"),
        });
      }
    }
    window.addEventListener("realtime-crud-event", handleRealtimeSubproductEvent);
    return () => {
      window.removeEventListener("realtime-crud-event", handleRealtimeSubproductEvent);
    };
  }, [qc, productId]);

  return {
    ...query,
    subproducts: query.data?.results || [],
    nextPageUrl: query.data?.next || null,
    previousPageUrl: query.data?.previous || null,
    prefetchPage,
  };
}

/**
 * 2️⃣ Crear subproducto con inserción optimista + refetch.
 */
export function useCreateSubproduct(productId) {
  const qc = useQueryClient();
  const listPrefix = ["products", productId, "subproducts", "list"];

  return useMutation({
    mutationKey: ["products", productId, "subproducts", "create"],
    mutationFn: (formData) => createSubproduct(productId, formData),
   onSuccess: () => {
     // Solo invalidar. React Query se encarga del refetch activo.
     qc.invalidateQueries({ queryKey: listPrefix, refetchType: "active" });
   },
  });
}

/**
 * 3️⃣ Actualizar subproducto con invalidación de caches relacionadas.
 */
export function useUpdateSubproduct(productId) {
  const qc = useQueryClient();
  return useMutation({
    mutationKey: [...productKeys.subproductsList(productId), "update"],
    mutationFn: ({ subproductId, formData }) =>
      updateSubproduct(productId, subproductId, formData),
    onSuccess: (_data, { subproductId }) => {
      qc.invalidateQueries(productKeys.subproductsList(productId));
      qc.invalidateQueries(productKeys.subproductDetail(productId, subproductId));
      qc.invalidateQueries(productKeys.subproductFiles(productId, subproductId));
    },
  });
}

/**
 * 4️⃣ Eliminar subproducto con optimistic update (todas las listas).
 */
export function useDeleteSubproduct(productId) {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (subproductId) => deleteSubproduct(productId, subproductId),

    onMutate: async (subproductId) => {
      // Cancelar queries relacionadas
      await qc.cancelQueries({
        predicate: (q) =>
          productKeys.prefixMatch(q.queryKey) &&
          q.queryKey[0] === "products" &&
          q.queryKey[1] === productId &&
          q.queryKey.includes("subproducts") &&
          q.queryKey.includes("list"),
      });

      // Snapshots de todas las listas
      const affectedLists = qc.getQueriesData({
        predicate: (q) =>
          productKeys.prefixMatch(q.queryKey) &&
          q.queryKey[0] === "products" &&
          q.queryKey[1] === productId &&
          q.queryKey.includes("subproducts") &&
          q.queryKey.includes("list"),
      });

      const snapshots = affectedLists.map(([key, data]) => ({ key, data }));

      // Filtrar el eliminado en todas las listas
      snapshots.forEach(({ key, data }) => {
        if (!data?.results) return;
        qc.setQueryData(key, {
          ...data,
          results: data.results.filter((sp) => sp.id !== subproductId),
          count:
            typeof data?.count === "number"
              ? Math.max(0, data.count - 1)
              : data?.count,
        });
      });

      return { snapshots };
    },

    onError: (_err, _id, ctx) => {
      // Restaurar snapshots
      ctx?.snapshots?.forEach(({ key, data }) => {
        qc.setQueryData(key, data);
      });
    },

    onSettled: () => {
      // Invalidar todo lo de subproductos del producto
      qc.invalidateQueries({
        predicate: (q) =>
          productKeys.prefixMatch(q.queryKey) &&
          q.queryKey[0] === "products" &&
          q.queryKey[1] === productId &&
          q.queryKey.includes("subproducts"),
      });
    },
  });
}