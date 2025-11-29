import { useInfiniteQuery } from '@tanstack/react-query';
import { listStockProductEvents } from '../services/listStockProductEvents';
import { useCallback, useState } from 'react';

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

export function useStockProductEvents(productId) {
  const [filters, setFilters] = useState({ start_date: null, end_date: null });

  const handleFilterChange = useCallback((start, end) => {
    const toISO = (d) => (d instanceof Date ? d.toISOString() : d || null);
    setFilters({ start_date: toISO(start), end_date: toISO(end) });
  }, []);

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
    queryKey: ['stockProductEvents', productId, filters],
    enabled: !!productId,
    initialPageParam: 1,
    queryFn: async ({ pageParam }) => {
      const url = `/stocks/products/${productId}/stock/events/`;
      const page = pageParam || 1;
      const res = await listStockProductEvents(url + `?page=${page}`, filters.start_date, filters.end_date);
      return res;
    },
    getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
  });

  const stockEvents = data?.pages?.flatMap((p) => p?.results ?? []) ?? [];
  const nextPage = data?.pages?.[data.pages.length - 1]?.next ?? null;
  const previousPage = data?.pages?.[0]?.previous ?? null;

  return {
    stockEvents,
    loading,
    error: isError ? (error?.message || 'Error al obtener los eventos de stock.') : null,
    nextPage,
    previousPage,
    fetchStockEvents: fetchNextPage,
    handleFilterChange,
    refetch,
    isFetchingNextPage,
    hasNextPage,
  };
}
