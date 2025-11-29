// utils/httpCache.js
// Caché HTTP en memoria con TTL (global y reutilizable)

const mem = new Map(); // Map<string, { t: number, data: any }>

/**
 * Genera una clave estable para la URL dada.
 * @param {string} url
 * @returns {string}
 */
export function cacheKey(url) {
  return `httpcache:${String(url || "")}`;
}

/**
 * Devuelve el dato cacheado si NO ha expirado (según ttlMs).
 * Si no hay entrada o está expirada, devuelve null.
 * @param {string} url
 * @param {number} ttlMs - TTL en milisegundos. Si es <=0 o no numérico, siempre da MISS.
 * @returns {any|null}
 */
export function getCached(url, ttlMs = 0) {
  const k = cacheKey(url);
  const hit = mem.get(k);
  if (!hit) return null;

  if (!Number.isFinite(ttlMs) || ttlMs <= 0) {
    // Requiere TTL explícito para considerar HIT
    return null;
  }
  if (Date.now() - hit.t > ttlMs) {
    mem.delete(k);
    return null;
  }
  return hit.data;
}

/**
 * Guarda un valor en el caché para la URL indicada.
 * @param {string} url
 * @param {any} data
 */
export function setCached(url, data) {
  mem.set(cacheKey(url), { t: Date.now(), data });
}

/**
 * Invalida por coincidencia EXACTA de URL (o lista de URLs).
 * @param {string|string[]} urlOrUrls
 */
export function invalidateExact(urlOrUrls) {
  const urls = Array.isArray(urlOrUrls) ? urlOrUrls : [urlOrUrls];
  for (const u of urls) mem.delete(cacheKey(u));
}

/**
 * Invalida todas las entradas cuyo key contenga alguno de los prefijos indicados.
 * Útil para invalidar rangos (p.ej. '/products/', '/cutting/').
 * @param {string|string[]} prefixes
 */
export function invalidatePrefixes(prefixes) {
  const arr = Array.isArray(prefixes) ? prefixes : [prefixes];
  for (const k of [...mem.keys()]) {
    if (arr.some((p) => k.includes(p))) mem.delete(k);
  }
}

/**
 * Limpia completamente el caché en memoria.
 */
export function clearAll() {
  mem.clear();
}

/**
 * Stats simples para debug (no usar en producción si te preocupa exponer keys).
 * @returns {{ size: number, keys: string[] }}
 */
export function getStats() {
  return { size: mem.size, keys: [...mem.keys()] };
}

export default {
  cacheKey,
  getCached,
  setCached,
  invalidateExact,
  invalidatePrefixes,
  clearAll,
  getStats,
};
