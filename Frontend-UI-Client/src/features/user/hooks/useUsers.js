import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { listUsers } from '../services/listUsers';

function buildQueryString(filterObj) {
  const queryParams = new URLSearchParams();
  Object.entries(filterObj || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      let apiValue = value;
      if (key === 'is_active') {
        apiValue = (apiValue === true || apiValue === 'true' || apiValue.toLowerCase() === 'activo') ? 'true' :
          (apiValue === false || apiValue === 'false' || apiValue.toLowerCase() === 'inactivo') ? 'false' : '';
      }
      if (key === 'is_staff') {
        apiValue = (apiValue === true || apiValue === 'true' || apiValue.toLowerCase() === 'admin') ? 'true' :
          (apiValue === false || apiValue === 'false' || apiValue.toLowerCase() === 'operario') ? 'false' : '';
      }
      if (apiValue) queryParams.append(key, apiValue);
    }
  });
  const queryString = queryParams.toString();
  return queryString ? `?${queryString}` : '';
}

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

const useUsers = (filters, initialUrl = '/users/list/') => {
  const queryClient = useQueryClient();
  const queryStr = buildQueryString(filters);
  const url = `${initialUrl.split('?')[0]}${queryStr}`;

  const {
    data,
    isLoading: loadingUsers,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    refetch,
  } = useInfiniteQuery({
    queryKey: ['users', url],
    initialPageParam: 1,
    queryFn: async ({ pageParam }) => {
      const page = pageParam || 1;
      const pageUrl = url.includes('?') ? `${url}&page=${page}` : `${url}?page=${page}`;
      const res = await listUsers(pageUrl);
      return res;
    },
    getNextPageParam: (lastPage) => getPageFromUrl(lastPage?.next),
  });

  const users = data?.pages?.flatMap((p) => p?.results ?? []) ?? [];
  const nextPageUrl = data?.pages?.[data.pages.length - 1]?.next ?? null;
  const previousPageUrl = data?.pages?.[0]?.previous ?? null;

  // Paginación siguiente
  const next = () => {
    if (hasNextPage) fetchNextPage();
  };
  // Paginación anterior (no soportada por useInfiniteQuery, pero se puede implementar si es necesario)
  const previous = () => {
    // No-op
  };
  // Invalidar cache y refrescar
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['users'] });
    refetch();
  };

  return {
    users,
    loadingUsers,
    error: isError ? (error?.message || 'Error al obtener usuarios.') : null,
    nextPageUrl,
    previousPageUrl,
    fetchUsers: fetchNextPage,
    next,
    previous,
    currentUrl: url,
    invalidate,
    isFetchingNextPage,
    hasNextPage,
    refetch,
  };
};

export default useUsers;
