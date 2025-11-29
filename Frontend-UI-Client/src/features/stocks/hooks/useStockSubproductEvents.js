import { useInfiniteQuery } from '@tanstack/react-query';
import { listStockSubproductEvents } from '../services/listStockSubproductEvents';
import { useCallback, useState } from 'react';

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

export function useStockSubproductEvents(subproductId) {
    const [filters, setFilters] = useState({ start_date: null, end_date: null });

    // Recibe un objeto { start_date, end_date } en formato yyyy-MM-dd
    const handleFilterChange = useCallback((range) => {
        const toISO = (s) => {
            if (!s) return null;
            const d = new Date(s);
            return isNaN(d) ? null : d.toISOString();
        };
        setFilters({
            start_date: toISO(range.start_date),
            end_date: toISO(range.end_date),
        });
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
        queryKey: ['stockSubproductEvents', subproductId, filters],
        enabled: !!subproductId,
        initialPageParam: 1,
        queryFn: async ({ pageParam }) => {
            const url = `/stocks/subproducts/${subproductId}/stock/events/`;
            const page = pageParam || 1;
            const res = await listStockSubproductEvents(url + `?page=${page}`, filters.start_date, filters.end_date);
            return res;
        },
        getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
    });

    // Unifica todos los resultados
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
