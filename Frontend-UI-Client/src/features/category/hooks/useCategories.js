import { useInfiniteQuery, useQueryClient } from "@tanstack/react-query";
import { djangoApi } from "@/api/clients";
import { buildQueryString } from "@/utils/queryUtils";
import { categoryKeys } from "../utils/queryKeys";

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

export function useCategories(filters = {}) {
  const qs = buildQueryString(filters);
  const endpoint = `/inventory/categories/${qs}`;
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
    queryKey: categoryKeys.list(filters),
    initialPageParam: 1,
    queryFn: async ({ pageParam }) => {
      const page = pageParam || 1;
      const pageUrl = endpoint.includes('?') ? `${endpoint}&page=${page}` : `${endpoint}?page=${page}`;
      const res = await djangoApi.get(pageUrl).then((r) => r.data);
      return res;
    },
    getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
    keepPreviousData: true,
    staleTime: 0,
    cacheTime: 10 * 60 * 1000,
    refetchOnWindowFocus: false,
  });

  const categories = data?.pages?.flatMap((p) => p?.results ?? []) ?? [];
  const total = data?.pages?.[0]?.count ?? 0;
  const nextPageUrl = data?.pages?.[data.pages.length - 1]?.next ?? null;
  const previousPageUrl = data?.pages?.[0]?.previous ?? null;

  // Invalidar por root key; React Query se encarga de refetchear activas
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: categoryKeys.all, exact: false, refetchType: 'active' });
  };

  return {
    categories,
    total,
    nextPageUrl,
    previousPageUrl,
    loading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
    invalidate,
  };
}
