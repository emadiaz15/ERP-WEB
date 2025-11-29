import { useEffect } from 'react';
import useIntakeOrdersStore from '../store/useIntakeOrdersStore';

// Idle prefetch for next page of intake orders (optional performance enhancement)
// Similar pattern to notifications prefetch: when user is idle and there is a next page, prefetch in background.
// Does not force overwrite; relies on API layer caching to store results.

export default function IntakeOrdersPrefetchIdle({ enabled = true, intervalMs = 12_000 }) {
  const { page, totalPages, prefetchNextPage, loading } = useIntakeOrdersStore((s) => ({
    page: s.page,
    totalPages: s.totalPages,
    prefetchNextPage: s.prefetchNextPage,
    loading: s.loading,
  }));

  useEffect(() => {
    if (!enabled) return;
    if (page >= totalPages) return;
    let timer = null;

    const schedule = () => {
      timer = setTimeout(() => {
        if ('requestIdleCallback' in window) {
          window.requestIdleCallback(() => {
            if (!loading) prefetchNextPage();
            schedule();
          }, { timeout: 2000 });
        } else {
          if (!loading) prefetchNextPage();
          schedule();
        }
      }, intervalMs);
    };
    schedule();
    return () => { if (timer) clearTimeout(timer); };
  }, [enabled, page, totalPages, prefetchNextPage, loading, intervalMs]);

  return null;
}
