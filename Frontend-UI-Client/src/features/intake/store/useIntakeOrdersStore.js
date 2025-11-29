// Zustand store for Intake Orders
// Centralizes list data, pagination, filters, summary, loading states, and optimistic mutations.
// Inspired by notifications store patterns: idempotent guards, in-flight dedupe, optional prefetch.

import { create } from 'zustand';
import intakeApi, {
  getIntakeOrders,
  getIntakeSummary,
  assignIntakeOrder,
  unassignIntakeOrder,
  closeIntakeOrder,
  updateIntakeOrder,
  deleteIntakeOrder,
  ingestIntakeOrders,
  prefetchIntakeOrders,
  forceRefetchIntake,
  forceRefetchIntakeSummary,
} from '../services/intakeApi';

// Pagination + Cache Interaction:
//   The store keeps only the current page slice (not an ever-growing infinite list) to simplify memory usage.
//   When prefetching next page we rely on the cached HTTP layer storing that response; advancing page triggers fetchOrders
//   which will load from cache quickly if still fresh.
// Optimistic Mutations:
//   Each mutation captures a snapshot for revert. After server success we lazily refresh summary.
// Realtime Events:
//   External component listens for CRUD events and calls fetchOrders({ force: true }) ensuring alignment with server.
// Force Hard Refresh:
//   Clears client cache (via forceRefetch*) then fetches both list and summary ignoring TTL.
//
// Edge Cases & Guards:
//   - Dedupe in-flight list fetches using key + _inflightFetch flag.
//   - _version counter for selectors that might subscribe to changes in derived UIs.
//
// Potential Extensions:
//   - Expose a map of cached pages to support infinite scroll accumulation.
//   - Integrate generation header from backend (if exposed) to shorten stale windows.
//   - Add negative caching for common 404 scenarios (not needed presently).
// Helpers
function buildParams({ page, pageSize, search, ordering, status }) {
  const p = { page, page_size: pageSize };
  if (search) p.search = search;
  if (ordering) p.ordering = ordering;
  if (status) p.status = status; // adapt if backend field differs
  return p;
}

const initialState = {
  items: [],
  page: 1,
  pageSize: 25,
  total: 0,
  totalPages: 0,
  search: '',
  ordering: '-created_at',
  status: undefined,
  loading: false,
  error: null,
  summary: null,
  summaryLoading: false,
  summaryError: null,
  // internal
  _lastFetchKey: null,
  _inflightFetch: false,
  _version: 0, // increments when items mutate (for selectors that need subscription)
};

export const useIntakeOrdersStore = create((set, get) => ({
  ...initialState,

  setFilter(partial) {
    set((s) => ({ ...partial, page: 1 }));
    // Trigger refetch after filters update
    get().fetchOrders({ force: true });
  },

  setPage(page) {
    set({ page });
    get().fetchOrders();
  },

  refresh(force = false) {
    return get().fetchOrders({ force });
  },

  refreshSummary(force = false) {
    return get().fetchSummary({ force });
  },

  async fetchOrders({ force = false } = {}) {
    const state = get();
    const params = buildParams(state);
    const key = JSON.stringify(params);
    if (!force && state._inflightFetch && state._lastFetchKey === key) return; // dedupe

    set({ loading: true, error: null, _inflightFetch: true, _lastFetchKey: key });
    try {
      const data = await getIntakeOrders(params, { force });
      // Expect DRF pagination: { results, count, next, previous }
      const items = data.results || data.items || [];
      const total = data.count ?? items.length;
      const totalPages = state.pageSize ? Math.ceil(total / state.pageSize) : 1;
      set({
        items,
        total,
        totalPages,
        loading: false,
        _inflightFetch: false,
        _version: state._version + 1,
      });
    } catch (err) {
      set({ error: err, loading: false, _inflightFetch: false });
    }
  },

  async fetchSummary({ force = false } = {}) {
    const state = get();
    if (state.summaryLoading && !force) return;
    set({ summaryLoading: true, summaryError: null });
    try {
      const data = await getIntakeSummary({ force });
      set({ summary: data, summaryLoading: false });
    } catch (err) {
      set({ summaryError: err, summaryLoading: false });
    }
  },

  prefetchNextPage() {
    const s = get();
    if (!s.totalPages) return;
    const next = s.page + 1;
    if (next > s.totalPages) return;
    const params = buildParams({ ...s, page: next });
    prefetchIntakeOrders(params); // silent
  },

  // Optimistic helpers
  _applyPatch(id, patchFn) {
    set((state) => {
      const idx = state.items.findIndex((o) => o.id === id);
      if (idx === -1) return {};
      const copy = [...state.items];
      copy[idx] = { ...copy[idx], ...patchFn(copy[idx]) };
      return { items: copy, _version: state._version + 1 };
    });
  },

  async optimisticAssign(id, payload = {}) {
    const revert = get()._snapshot();
    get()._applyPatch(id, () => ({ assignee: payload.user || 'me', status: 'assigned' }));
    try {
      await assignIntakeOrder(id, payload);
      // refresh summary lazily
      get().refreshSummary(false);
    } catch (e) {
      revert();
    }
  },

  async optimisticUnassign(id) {
    const revert = get()._snapshot();
    get()._applyPatch(id, () => ({ assignee: null }));
    try {
      await unassignIntakeOrder(id, {});
      get().refreshSummary(false);
    } catch (e) {
      revert();
    }
  },

  async optimisticClose(id) {
    const revert = get()._snapshot();
    get()._applyPatch(id, () => ({ status: 'closed' }));
    try {
      await closeIntakeOrder(id, {});
      get().refreshSummary(false);
    } catch (e) {
      revert();
    }
  },

  async optimisticUpdate(id, partial) {
    const revert = get()._snapshot();
    get()._applyPatch(id, () => partial);
    try {
      await updateIntakeOrder(id, partial);
      get().refreshSummary(false);
    } catch (e) {
      revert();
    }
  },

  async optimisticDelete(id) {
    const revert = get()._snapshot();
    set((s) => ({ items: s.items.filter((o) => o.id !== id), _version: s._version + 1 }));
    try {
      await deleteIntakeOrder(id);
      get().refreshSummary(false);
      // refetch list maybe to ensure pagination integrity
      get().refresh(true);
    } catch (e) {
      revert();
    }
  },

  async ingest(payload) {
    await ingestIntakeOrders(payload);
    // after ingest force a refresh to see new orders
    await get().refresh(true);
    get().refreshSummary(true);
  },

  // Snapshot used for optimistic revert
  _snapshot() {
    const state = get();
    const prev = { items: state.items, _version: state._version };
    return () => set({ items: prev.items, _version: prev._version + 1 });
  },

  forceHardRefresh() {
    forceRefetchIntake(buildParams(get()));
    forceRefetchIntakeSummary();
    get().fetchOrders({ force: true });
    get().fetchSummary({ force: true });
  },

  reset() {
    set({ ...initialState });
  },
}));

export default useIntakeOrdersStore;
