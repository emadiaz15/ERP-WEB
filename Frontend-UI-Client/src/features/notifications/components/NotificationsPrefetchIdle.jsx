import { useEffect, useRef } from 'react';
import { useNotificationsStore } from '../stores/useNotificationsStore';

/**
 * NotificationsPrefetchIdle
 *
 * Prefetches the next notifications pages opportunistically when:
 *  - Browser is idle (requestIdleCallback / setTimeout fallback)
 *  - Tab is visible
 *  - There are more pages AND we haven't prefetched beyond a depth
 *  - User is not currently loading another page
 *
 * Rationale: User usually opens bell and then inbox; having page 2 (and maybe 3) ready
 * reduces perceived latency when scrolling or pressing "Cargar más".
 */
export default function NotificationsPrefetchIdle({ maxDepth = 2, intervalMs = 8000 }) {
  const fetchPage = useNotificationsStore(s => s.fetchPage);
  // Tomar sólo snapshots primitivos para no disparar loops de suscripción.
  const page = useNotificationsStore(s => s.page);
  const hasMore = useNotificationsStore(s => s.hasMore);
  const loading = useNotificationsStore(s => s.loading);
  const prefetchedUntil = useRef(1); // last page index prefetched
  const timerRef = useRef(null);

  useEffect(() => {
    function schedule() {
      if (timerRef.current) return;
      timerRef.current = setTimeout(run, intervalMs);
    }

    function run(deadline) {
      timerRef.current = null;
      if (document.hidden) { // don't prefetch in background tab
        schedule();
        return;
      }
      if (!hasMore) return; // nothing else to prefetch
      if (loading) { schedule(); return; }

      const current = prefetchedUntil.current;
      // Base real de usuario (page) + maxDepth define tope superior
      let next = current + 1;
      const maxAllowed = page + maxDepth;
      if (next > maxAllowed) { schedule(); return; }

      const doFetch = () => {
        fetchPage(next, { force: false, noAdvance: true }).then((res) => {
          // Si realmente trajo results nuevos, avanzamos prefetchedUntil
          if (res && res.results && res.results.length) {
            prefetchedUntil.current = next;
            // Si prefetch llegó a tope actual (usuario+maxDepth) no reprogramamos tan rápido
          }
          schedule();
        }).catch(() => schedule());
      };

      if (typeof window.requestIdleCallback === 'function') {
        window.requestIdleCallback((dl) => {
          if (dl.timeRemaining() > 5) doFetch(); else schedule();
        }, { timeout: 2000 });
      } else {
        doFetch();
      }
    }

    schedule();
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [page, hasMore, loading, fetchPage, maxDepth, intervalMs]);

  return null;
}
