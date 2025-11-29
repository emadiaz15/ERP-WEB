// src/hooks/useInfinitePageQuery.js
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { axiosInstance as defaultAxios } from '@/api/clients'; // ✅ ruta correcta

// Extrae ?page=N de una URL "next"
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

/**
 * Hook genérico para DRF PageNumberPagination:
 * API => { count, next, previous, results }
 */
export function useInfinitePageQuery({
  key,                 // string | any[]   ej: ['users', filters]
  url,                 // string           ej: '/users/'
  params = {},         // object           filtros/búsqueda
  pageSize = 10,       // respeta page_size / max_page_size del backend
  enabled = true,      // boolean
  axios = defaultAxios // permite inyectar otro cliente si hiciera falta
}) {
  const queryClient = useQueryClient();

  const query = useInfiniteQuery({
    queryKey: Array.isArray(key) ? key : [key],
    enabled,
    initialPageParam: 1,
    queryFn: async ({ pageParam }) => {
      const { data } = await axios.get(url, {
        params: { ...params, page: pageParam, page_size: pageSize },
      });
      return data; // { count, next, previous, results }
    },
    getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
  });

  // invalidar por "root key" (primera parte del queryKey)
  const rootKey = Array.isArray(key) ? key[0] : key;
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: [rootKey], exact: false, refetchType: 'active' });

  const items = query.data?.pages?.flatMap(p => p?.results ?? []) ?? [];

  return {
    ...query,
    invalidate,
    items,
  };
}
