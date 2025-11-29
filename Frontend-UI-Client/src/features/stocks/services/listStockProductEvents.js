import { djangoApi } from "@/api/clients";

// Normaliza respuesta paginada DRF
function normalizeListResponse(data) {
  if (data && typeof data === "object" && Array.isArray(data.results)) {
    return {
      results: data.results,
      next: data.next ?? null,
      previous: data.previous ?? null,
      count: data.count ?? data.results.length,
      raw: data,
    };
  }
  if (Array.isArray(data)) {
    return { results: data, next: null, previous: null, count: data.length, raw: data };
  }
  return { results: data ? [data] : [], next: null, previous: null, count: data ? 1 : 0, raw: data };
}

// 🔧 Mismo shape que subproductos
function mapEventToUI(e) {
  const rawType =
    e?.event_type ??
    e?.type ??
    e?.type_display ??
    (typeof e?.description === "string" && /inicial/i.test(e.description) ? "ingreso_inicial" : null);

  const createdBy =
    e?.created_by ??
    e?.user ??
    (typeof e?.created_by === "object" ? e.created_by?.username ?? e.created_by?.id : null) ??
    null;

  return {
    id: e?.id ?? e?._id ?? undefined,
    created_at: e?.created_at ?? e?.date ?? null,
    event_type: (rawType || "").toString().toLowerCase(),
    quantity_change: Number(e?.quantity_change ?? e?.quantity ?? 0),
    notes: e?.notes ?? e?.description ?? null,
    user: e?.user ?? null,
    created_by: createdBy,
    _raw: e,
  };
}

/**
 * Lista eventos de stock de un producto.
 * Si el endpoint directo (sin subproductos) da 400, hace fallback al agregado (con subproductos).
 * @param {string} url - p.ej. `/api/v1/stocks/products/:productId/stock/events/`
 * @param {string|null} startISO
 * @param {string|null} endISO
 */
export async function listStockProductEvents(url, startISO = null, endISO = null) {
  const params = {};
  if (startISO) params.start = startISO;
  if (endISO) params.end = endISO;

  const buildUrlWithParams = (baseUrl) => {
    if (!params.start && !params.end) return baseUrl;
    const u = new URL(baseUrl, window.location.origin);
    Object.entries(params).forEach(([k, v]) => v && u.searchParams.set(k, v));
    return baseUrl.startsWith("http") ? u.toString() : `${u.pathname}${u.search}`;
  };

  const finalUrl = buildUrlWithParams(url);

  try {
    const { data } = await djangoApi.get(finalUrl);
    const normalized = normalizeListResponse(data);
    return { ...normalized, results: (normalized.results || []).map(mapEventToUI) };
  } catch (err) {
    const status = err?.response?.status ?? err?.status;

    // Fallback solo si era la ruta base de producto y respondió 400 (tiene subproductos)
    const isBaseProdUrl = /\/stocks\/products\/\d+\/stock\/events\/?$/.test(url);
    if (status === 400 && isBaseProdUrl) {
      const aggUrl = url.replace(/\/stock\/events\/?$/, "/subproducts/stock/events/");
      const { data } = await djangoApi.get(buildUrlWithParams(aggUrl));
      const normalized = normalizeListResponse(data);
      return { ...normalized, results: (normalized.results || []).map(mapEventToUI) };
    }

    const detail = err?.response?.data?.detail || err?.message || "Error al obtener los eventos de stock.";
    throw new Error(detail);
  }
}

export default { listStockProductEvents };
