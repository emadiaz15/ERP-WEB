// src/features/cuttingOrder/services/cuttingOrders.js
// ----------------------------------------------------------------------------
// Services para Órdenes de Corte (Cuts) con caché en memoria (TTL)
// ❗️Sin lógica de formateo/validación: delega en utils/buildCuttingOrderPayload
// ----------------------------------------------------------------------------

import { djangoApi } from "@/api/clients";
import { getCached, setCached, invalidatePrefixes } from "@/utils/httpCache";
import {
  sanitizeCreateData,
  sanitizeUpdateData,
} from "@/features/cuttingOrder/utils/buildCuttingOrderPayload";

// ============================================================================
// Caché (TTLs y prefijos a invalidar)
// ============================================================================
const LIST_TTL = 30_000;   // 30s
const DETAIL_TTL = 30_000; // 30s

const LIST_PREFIX = "/cutting/cutting-orders/";
const DETAIL_PREFIX = "/cutting/cutting-orders/";

// ============================================================================
// Utils locales (solo red/transformaciones no de payload)
// ============================================================================

/** Build URL preservando query existente y agregando params. */
function buildUrl(base, params = {}) {
  try {
    const hasProtocol = /^https?:\/\//i.test(base);
    if (hasProtocol) {
      const u = new URL(base);
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
      });
      return u.toString();
    }
    const [path, existingQuery] = base.split("?");
    const sp = new URLSearchParams(existingQuery || "");
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== "") sp.set(k, v);
    });
    const qs = sp.toString();
    return qs ? `${path}?${qs}` : path;
  } catch {
    const qs = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== "")
      )
    ).toString();
    return qs ? `${base}?${qs}` : base;
  }
}

/** Normaliza respuesta lista (DRF paginada o arreglo simple). */
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

/** Sembrar cache de detalle a partir de listados. */
function seedDetailCache(listResults) {
  if (!Array.isArray(listResults)) return;
  for (const o of listResults) {
    const id = o?.id ?? o?.pk;
    if (id) setCached(`/cutting/cutting-orders/${id}/`, o);
  }
}

// ============================================================================
// Create (invalida caché)
// ============================================================================

/**
 * Crea una nueva Orden de Corte.
 * @param {{
 *  product:number, order_number:number, customer:string,
 *  quantity_to_cut:string|number,
 *  items?: Array<{subproduct:number, cutting_quantity:string|number}>,
 *  assigned_to?: number|null, operator_can_edit_items?: boolean,
 *  workflow_status?: 'pending'|'in_process'|'completed'|'cancelled'
 * }} payload
 */
export async function createCuttingOrder(payload) {
  const body = sanitizeCreateData(payload);
  const { data } = await djangoApi.post(
    "/cutting/cutting-orders/create/",
    body,
    { headers: { "Content-Type": "application/json" } }
  );
  invalidatePrefixes([LIST_PREFIX, DETAIL_PREFIX]);
  return data;
}

// ============================================================================
// List (cacheado)
// ============================================================================

export async function listCuttingOrders(
  url = "/cutting/cutting-orders/",
  params = undefined,
  options = undefined
) {
  const ttlMs = options?.ttlMs ?? LIST_TTL;
  const finalUrl = params ? buildUrl(url, params) : url;

  if (!options?.force) {
    const cached = getCached(finalUrl, ttlMs);
    if (cached) {
      const norm = normalizeListResponse(cached);
      seedDetailCache(norm.results);
      return norm;
    }
  }

  const { data } = await djangoApi.get(finalUrl);
  setCached(finalUrl, data);
  const norm = normalizeListResponse(data);
  seedDetailCache(norm.results);
  return norm;
}

// ============================================================================
// Detail (cacheado)
// ============================================================================

export async function getCuttingOrder(orderId) {
  const url = `/cutting/cutting-orders/${orderId}/`;
  const cached = getCached(url, DETAIL_TTL);
  if (cached) return cached;
  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return data;
}
export const getCuttingOrderDetail = getCuttingOrder;

// ============================================================================
// Update (invalida caché)
// ============================================================================

/**
 * Actualiza una orden (PUT/PATCH). No envía order_number (lo filtra sanitizeUpdateData).
 */
export async function updateCuttingOrder(orderId, updateData, method = "PATCH") {
  const httpMethod = String(method || "PATCH").toUpperCase();
  if (!["PUT", "PATCH"].includes(httpMethod)) {
    throw new Error("Método inválido: usa 'PUT' o 'PATCH'.");
  }

  const payload = sanitizeUpdateData(updateData);
  const { data } = await djangoApi({
    url: `/cutting/cutting-orders/${orderId}/`,
    method: httpMethod,
    data: payload,
  });

  // Si quisieras cachear inmediato el detalle:
  // setCached(`/cutting/cutting-orders/${orderId}/`, data);
  invalidatePrefixes([LIST_PREFIX, DETAIL_PREFIX]);
  return data;
}

export async function patchCuttingOrderWorkflow(orderId, workflow_status) {
  return updateCuttingOrder(orderId, { workflow_status }, "PATCH");
}

/**
 * Cancela una orden de corte cambiando su workflow_status a 'cancelled'.
 * Preferible a DELETE cuando el backend implementa soft-cancel por estado.
 */
export async function cancelCuttingOrder(orderId) {
  return patchCuttingOrderWorkflow(orderId, "cancelled");
}

export async function replaceCuttingOrderItems(orderId, items) {
  return updateCuttingOrder(orderId, { items }, "PATCH");
}

/**
 * Guarda ítems y pasa la orden a 'in_process' en un solo PATCH.
 * @param {number} orderId
 * @param {Array<{subproduct:number, cutting_quantity:number|string}>} items
 */
export async function patchCuttingOrderItemsAndStart(orderId, items) {
  return updateCuttingOrder(orderId, { items, workflow_status: "in_process" }, "PATCH");
}

export async function assignCuttingOrder(orderId, userId) {
  return updateCuttingOrder(orderId, { assigned_to: Number(userId) }, "PATCH");
}

/** Cambiar objetivo total (con validación backend). */
export async function setCuttingOrderQuantity(orderId, quantity_to_cut) {
  return updateCuttingOrder(orderId, { quantity_to_cut }, "PATCH");
}

// ============================================================================
// Delete (invalida caché)
// ============================================================================

export async function deleteCuttingOrder(orderId) {
  const res = await djangoApi.delete(`/cutting/cutting-orders/${orderId}/`);
  invalidatePrefixes([LIST_PREFIX, DETAIL_PREFIX]);
  return res.data;
}

// ============================================================================
// Subproductos por producto (para Step 2) — cacheable opcionalmente
// ============================================================================

/** Lista subproductos de un producto padre (por ID) usando la ruta anidada. */
export async function listSubproductsByParent(parentId, params = {}, options = {}) {
  const pid = Number(parentId);
  if (!Number.isFinite(pid)) {
    throw new Error(`parentId inválido: ${parentId}`);
  }

  // ✅ ruta correcta según tus urls.py
  const base = `/inventory/products/${pid}/subproducts/`;

  const finalParams = { status: true, ...params }; // por defecto solo activos
  const url = buildUrl(base, finalParams);

  const ttlMs = options.ttlMs ?? LIST_TTL;
  if (!options.force) {
    const cached = getCached(url, ttlMs);
    if (cached) return normalizeListResponse(cached);
  }

  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return normalizeListResponse(data);
}

// ============================================================================
// Export por defecto
// ============================================================================
export default {
  createCuttingOrder,
  listCuttingOrders,
  getCuttingOrder,
  getCuttingOrderDetail,
  updateCuttingOrder,
  patchCuttingOrderWorkflow,
  replaceCuttingOrderItems,
  patchCuttingOrderItemsAndStart,   // ⬅️ nuevo
  cancelCuttingOrder,
  assignCuttingOrder,
  setCuttingOrderQuantity,
  deleteCuttingOrder,
  listSubproductsByParent,          // ⬅️ nuevo
};
