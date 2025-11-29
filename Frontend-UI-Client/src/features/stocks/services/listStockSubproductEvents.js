// src/features/stocks/services/listStockSubproductEvents.js
import { djangoApi } from "@/api/clients";

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

// 🔧 Mapeamos al formato que espera el componente (created_at, event_type, quantity_change, notes, created_by)
function mapEventToUI(e) {
  // Detectar tipo si viene con otro nombre
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
    event_type: (rawType || "").toString().toLowerCase(),           // ej: "ingreso_inicial"
    quantity_change: Number(e?.quantity_change ?? e?.quantity ?? 0),
    notes: e?.notes ?? e?.description ?? null,
    user: e?.user ?? null,                                          // opcional
    created_by: createdBy,                                          // lo usa tu UI como fallback
    _raw: e,                                                        // por si necesitás más campos
  };
}

/**
 * Lista eventos de stock de un subproducto.
 * @param {string} url - p.ej. `/api/v1/stocks/subproducts/:subproductId/stock/events/`
 * @param {string|null} startISO
 * @param {string|null} endISO
 */
export async function listStockSubproductEvents(url, startISO = null, endISO = null) {
  const params = {};
  if (startISO) params.start = startISO;
  if (endISO) params.end = endISO;

  const finalUrl = (() => {
    if (!params.start && !params.end) return url;
    const u = new URL(url, window.location.origin);
    Object.entries(params).forEach(([k, v]) => v && u.searchParams.set(k, v));
    return url.startsWith("http") ? u.toString() : `${u.pathname}${u.search}`;
  })();

  const { data } = await djangoApi.get(finalUrl);
  const normalized = normalizeListResponse(data);

  // Devolvemos los eventos ya en el shape que usa tu componente
  return {
    ...normalized,
    results: (normalized.results || []).map(mapEventToUI),
  };
}

export default { listStockSubproductEvents };
