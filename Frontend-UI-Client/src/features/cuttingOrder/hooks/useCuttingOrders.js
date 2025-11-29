import { useInfiniteQuery, useQuery, useQueryClient, useMutation } from '@tanstack/react-query';
import { useRef, useState, useEffect, useCallback } from 'react';
import {
  createCuttingOrder,
  listCuttingOrders,
  getCuttingOrder,
  updateCuttingOrder,
  patchCuttingOrderWorkflow,
  cancelCuttingOrder,
  replaceCuttingOrderItems,
  assignCuttingOrder,
  setCuttingOrderQuantity,
  deleteCuttingOrder,
} from "@/features/cuttingOrder/services/cuttingOrders";

// -----------------------------------------------------------------------------
// Helpers
// -----------------------------------------------------------------------------

function useSafeState(initial) {
  const mountedRef = useRef(true);
  const [state, setState] = useState(initial);
  useEffect(() => () => { mountedRef.current = false; }, []);
  const safeSet = useCallback((updater) => {
    if (mountedRef.current) setState(updater);
  }, []);
  return [state, safeSet];
}

// Limpia/mapea filtros antes de llamar al backend
function sanitizeParams(params = {}) {
  const out = {};
  const put = (k, v) => {
    const val = typeof v === "string" ? v.trim() : v;
    if (val !== "" && val !== undefined && val !== null) out[k] = val;
  };

  // Convenciones del backend para lista:
  put("created_from", params.created_from ?? params.start_date);
  put("created_to", params.created_to ?? params.end_date);
  put("customer", params.customer ?? params.client);
  put("order_number", params.order_number);
  put("status", params.status);

  // Extras opcionales (si los usas en tu filtro, se pasan tal cual)
  put("assigned_to", params.assigned_to);
  put("product_id", params.product_id);
  put("product_code", params.product_code);

  return out;
}

// -----------------------------------------------------------------------------
// Queries (React Query)
// -----------------------------------------------------------------------------

function getPageFromUrl(urlLike) {
  if (!urlLike) return undefined;
  try {
    const u = new URL(urlLike, window.location.origin);
    const p = u.searchParams.get('page');
    return p ? Number(p) : undefined;
  } catch {
    const query = String(urlLike).split('?')[1] || '';
    const params = new URLSearchParams(query);
    const p = params.get('page');
    return p ? Number(p) : undefined;
  }
}

export function useCuttingOrders(options = {}) {
  const {
    url = "/cuts/cutting-orders/",
    params,
    enabled = true,
  } = options;
  const cleanParams = sanitizeParams(params);
  const queryClient = useQueryClient();

  const {
    data,
    isLoading: loading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['cuttingOrders', url, cleanParams],
    enabled,
    initialPageParam: 1,
    queryFn: async ({ pageParam }) => {
      const page = pageParam || 1;
      const pageUrl = url.includes('?') ? `${url}&page=${page}` : `${url}?page=${page}`;
      const res = await listCuttingOrders(pageUrl, cleanParams);
      return res;
    },
    getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
    keepPreviousData: true,
    staleTime: 0,
    cacheTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const cuttingOrders = data?.pages?.flatMap((p) => p?.results ?? []) ?? [];
  const nextPage = data?.pages?.[data.pages.length - 1]?.next ?? null;
  const previousPage = data?.pages?.[0]?.previous ?? null;
  const count = data?.pages?.[0]?.count ?? 0;

  // Invalidar cache y refrescar
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['cuttingOrders'] });
    refetch();
  };

  return {
    data: cuttingOrders,
    pagination: {
      next: nextPage,
      previous: previousPage,
      count,
      fetchNext: fetchNextPage,
      fetchPrevious: () => {}, // not supported
    },
    loading,
    error: isError ? (error?.message || 'Error al obtener órdenes de corte.') : null,
    refetch,
    isFetchingNextPage,
    hasNextPage,
    invalidate,
  };
}

export function useCuttingOrder(orderId, options = {}) {
  const { enabled = true } = options;
  const {
    data,
    isLoading: loading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['cuttingOrder', orderId],
    enabled: !!orderId && enabled,
    queryFn: () => getCuttingOrder(orderId),
    staleTime: 0,
    cacheTime: 30 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
  return {
    data,
    loading,
    error: isError ? (error?.message || 'Error al obtener orden de corte.') : null,
    refetch,
  };
}

// -----------------------------------------------------------------------------
// Mutations (cada una expone fn + estado)
// -----------------------------------------------------------------------------

function useLocalMutation(fn) {
  const [loading, setLoading] = useSafeState(false);
  const [error, setError] = useSafeState(null);
  const mutate = useCallback(
    async (...args) => {
      setLoading(true);
      setError(null);
      try {
        const res = await fn(...args);
        return res;
      } catch (e) {
        setError(e);
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [fn, setLoading, setError]
  );
  return [mutate, { loading, error }];
}

/** Crear orden */
export function useCreateCuttingOrder() {
  return useLocalMutation(createCuttingOrder);
}

/** Update genérico (PUT/PATCH) */
export function useUpdateCuttingOrder() {
  return useLocalMutation(updateCuttingOrder);
}

/** Cambiar workflow (PATCH) */
export function usePatchCuttingOrderWorkflow() {
  return useLocalMutation(patchCuttingOrderWorkflow);
}

/** Cancelar (PATCH workflow_status='cancelled') */
export function useCancelCuttingOrder() {
  return useLocalMutation(cancelCuttingOrder);
}

/** Reemplazar ítems (PATCH) */
export function useReplaceCuttingOrderItems() {
  return useLocalMutation(replaceCuttingOrderItems);
}

/** Asignar a usuario (PATCH) */
export function useAssignCuttingOrder() {
  return useLocalMutation(assignCuttingOrder);
}

/** Cambiar objetivo total (PATCH) */
export function useSetCuttingOrderQuantity() {
  return useLocalMutation(setCuttingOrderQuantity);
}

/** Eliminar (DELETE) */
export function useDeleteCuttingOrder() {
  return useLocalMutation(deleteCuttingOrder);
}

// -----------------------------------------------------------------------------
// Export agrupado (opcional)
// -----------------------------------------------------------------------------
const cuttingOrderHooks = {
  useCuttingOrders,
  useCuttingOrder,
  useCreateCuttingOrder,
  useUpdateCuttingOrder,
  usePatchCuttingOrderWorkflow,
  useCancelCuttingOrder,
  useReplaceCuttingOrderItems,
  useAssignCuttingOrder,
  useSetCuttingOrderQuantity,
  useDeleteCuttingOrder,
};

export default cuttingOrderHooks;
