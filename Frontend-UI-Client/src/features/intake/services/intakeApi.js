// Centralized Intake API service with caching & invalidation helpers
// Mirrors backend generation-based caching window (approx 30s) but keeps a shorter client TTL
// to allow quick UI reflection after mutations. We still expose a manual invalidate to force refresh.
//
// Key goals:
// - Single place to build query cache keys (stable, hashed) to avoid duplication
// - Dedupe in-flight requests (coalescing)
// - Provide explicit invalidate helpers used by mutations / store
// - Support summary + paginated list + worklist (future) endpoints
// - Allow optimistic updates by returning previous snapshot
//
// Assumptions:
// - http client is axios instance imported as api
// - A small httpCache util exists with getCached(url, { ttl, force, paramsHash }) & setCached
//   If not, adapt accordingly.
// - Backend endpoints (adjust paths if different):
//    GET /api/intake/orders/  (list, paginated)
//    GET /api/intake/orders/summary/  (summary)
//    POST /api/intake/orders/ingest/  (ingest)
//    POST /api/intake/orders/{id}/assign/  (assign)
//    POST /api/intake/orders/{id}/unassign/ (unassign)
//    POST /api/intake/orders/{id}/close/ (close)
//    PATCH /api/intake/orders/{id}/ (update)
//    DELETE /api/intake/orders/{id}/ (delete)
//
// If some endpoints differ, update PATHS below.

// Adjusted imports to existing project structure (mirrors notifications.api.js pattern)
import { djangoApi as api } from '@/api/clients';
import { getCached, setCached, invalidateExact } from '@/utils/httpCache';

// Local helpers replicating functionality we initially assumed from a non-existent httpCache variant
function buildParamsHash(params = {}) {
  if (!params || typeof params !== 'object') return 'noparams';
  const keys = Object.keys(params).sort();
  const enc = (v) => encodeURIComponent(v == null ? '' : String(v));
  return keys.map(k => `${enc(k)}=${enc(params[k])}`).join('&') || 'noparams';
}

function delCached(key) {
  // In our simple httpCache, keys are the exact URLs we stored (listKey or summary path + query)
  invalidateExact(key);
}

const CLIENT_TTL_MS = 25_000; // Slightly under backend 30s window to reduce stale window
const MUTATION_INVALIDATE_DELAY = 50; // small timeout to batch quick successive invalidations

// NOTE: Base axios client already prefixes /api/v1 (see clients.js)
const PATHS = {
  list: '/intake/orders/',
  summary: '/intake/orders/summary/',
  ingest: '/intake/orders/ingest/',
  assign: (id) => `/intake/orders/${id}/assign/`,
  unassign: (id) => `/intake/orders/${id}/unassign/`,
  close: (id) => `/intake/orders/${id}/close/`,
  update: (id) => `/intake/orders/${id}/`,
  remove: (id) => `/intake/orders/${id}/`,
};

// Track pending fetches to dedupe concurrent calls with identical cache key
const inflight = new Map();

function buildListKey(params) {
  return `${PATHS.list}?${buildParamsHash(params)}`;
}

function buildSummaryKey() {
  return PATHS.summary;
}

function storeInflight(key, promise) {
  inflight.set(key, promise);
  promise.finally(() => inflight.delete(key));
  return promise;
}

async function fetchWithCache({ url, key, ttl = CLIENT_TTL_MS, force = false, method = 'get', data, params }) {
  if (!force) {
    const cached = getCached(key, ttl);
    if (cached) return cached;
  }
  if (inflight.has(key)) return inflight.get(key);
  const p = api({ method, url, data, params }).then((res) => {
    setCached(key, res.data);
    return res.data;
  }).catch((err) => { throw err; });
  return storeInflight(key, p);
}

export async function getIntakeOrders(params = {}, { force = false } = {}) {
  const key = buildListKey(params);
  return fetchWithCache({ url: PATHS.list, key, params, force });
}

export async function getIntakeSummary({ force = false } = {}) {
  const key = buildSummaryKey();
  return fetchWithCache({ url: PATHS.summary, key, force });
}

// Simple invalidation helpers
let invalidateTimer = null;
function scheduleInvalidate(keys) {
  if (!Array.isArray(keys)) keys = [keys];
  if (invalidateTimer) clearTimeout(invalidateTimer);
  invalidateTimer = setTimeout(() => {
    keys.forEach((k) => delCached(k));
  }, MUTATION_INVALIDATE_DELAY);
}

export function invalidateIntakeList(paramsArr = []) {
  if (paramsArr.length === 0) {
    // naive: clear every cached list variant (requires httpCache exposing a list; fallback: pattern not supported => no-op)
    // If httpCache has no enumeration, rely on store-level refetch with force.
    return; 
  }
  const keys = paramsArr.map((p) => buildListKey(p));
  scheduleInvalidate(keys);
}

export function invalidateIntakeSummary() {
  scheduleInvalidate(buildSummaryKey());
}

// Mutation wrappers (they invalidate cache + optionally return updated snapshot)
// Invalidation Strategy:
//   - We optimistically clear only the specific list variants when provided via affectedParams
//   - If affectedParams omitted we rely on store forced refetch (force=true) or manual forceRefetch helpers
//   - Summary is always invalidated after mutations (can be tuned via options)
//   - Backend generation bump ensures even if client cache survives TTL, subsequent force fetch observes changes
async function runMutation(requestFn, { invalidateList = true, invalidateSummary = true, affectedParams = [] } = {}) {
  const result = await requestFn();
  if (invalidateList) invalidateIntakeList(affectedParams);
  if (invalidateSummary) invalidateIntakeSummary();
  return result;
}

export async function ingestIntakeOrders(payload, options = {}) {
  return runMutation(() => api.post(PATHS.ingest, payload).then(r => r.data), { ...options });
}

export async function assignIntakeOrder(id, payload = {}, options = {}) {
  return runMutation(() => api.post(PATHS.assign(id), payload).then(r => r.data), { ...options });
}

export async function unassignIntakeOrder(id, payload = {}, options = {}) {
  return runMutation(() => api.post(PATHS.unassign(id), payload).then(r => r.data), { ...options });
}

export async function closeIntakeOrder(id, payload = {}, options = {}) {
  return runMutation(() => api.post(PATHS.close(id), payload).then(r => r.data), { ...options });
}

export async function updateIntakeOrder(id, partial, options = {}) {
  return runMutation(() => api.patch(PATHS.update(id), partial).then(r => r.data), { ...options });
}

export async function deleteIntakeOrder(id, options = {}) {
  return runMutation(() => api.delete(PATHS.remove(id)).then(r => r.data), { ...options });
}

// Utility prefetch (does not force) - used by idle prefetch logic
export async function prefetchIntakeOrders(params) {
  try {
    await getIntakeOrders(params, { force: false });
  } catch (_) {
    // silent
  }
}

export function forceRefetchIntake(params = {}) {
  const key = buildListKey(params);
  delCached(key);
  return getIntakeOrders(params, { force: true });
}

export function forceRefetchIntakeSummary() {
  const key = buildSummaryKey();
  delCached(key);
  return getIntakeSummary({ force: true });
}

export const intakeApi = {
  getIntakeOrders,
  getIntakeSummary,
  ingestIntakeOrders,
  assignIntakeOrder,
  unassignIntakeOrder,
  closeIntakeOrder,
  updateIntakeOrder,
  deleteIntakeOrder,
  prefetchIntakeOrders,
  forceRefetchIntake,
  forceRefetchIntakeSummary,
  invalidateIntakeList,
  invalidateIntakeSummary,
};

export default intakeApi;
