// src/features/product/services/subproducts/subproducts.js
import { djangoApi } from "@/api/clients";
import { getCached, setCached, invalidatePrefixes } from "@/utils/httpCache";

/** ─────────────────────────────────────────────────────────────
 * Utilidad: extrae un mensaje legible desde respuestas de DRF/Django
 * - Soporta: {detail}, {campo: ["err1","err2"]}, string plano (HTML o texto)
 * - Nunca devuelve string vacío
 * ───────────────────────────────────────────────────────────── */
function extractErrorMessage(error, fallback = "Ocurrió un error") {
  try {
    const status = error?.response?.status;
    const data = error?.response?.data;

    // 1) Si el backend envía un string (p.ej. HTML o texto)
    if (typeof data === "string") {
      // Sanitiza un poco HTML de Django debug si llegara
      const text = data.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
      return text || `${fallback}${status ? ` (HTTP ${status})` : ""}`;
    }

    // 2) Si envía un objeto { detail: "..." }
    if (data && typeof data === "object") {
      if (typeof data.detail === "string" && data.detail.trim() !== "") {
        return data.detail.trim();
      }

      // 3) Si envía errores por campo: { field: ["msg1","msg2"], ... }
      const entries = Object.entries(data);
      if (entries.length > 0) {
        // construye algo como "number_coil: Ya existe... · net_weight: No puede ser mayor..."
        const parts = entries.map(([field, val]) => {
          const msgs = Array.isArray(val) ? val : [val];
          const first = msgs.map((m) => String(m)).filter(Boolean).join(" | ");
          return `${field}: ${first}`;
        });
        return parts.join(" · ");
      }
    }

    // 4) Axios error.message o fallback
    if (error?.message) return error.message;
    return `${fallback}${status ? ` (HTTP ${status})` : ""}`;
  } catch {
    return fallback;
  }
}

/**
 * Lista subproductos con soporte para paginación y filtros.
 * @param {number|string} product_pk
 * @param {string|null} url - URL paginada (si viene, IGNORA product_pk y filters)
 * @param {object} filters - ej: { status: "true" | "false" | undefined, ... }
 * @returns {Promise<Object>} - { results, next, previous, count, ... }
 */
export const listSubproducts = async (product_pk, url = null, filters = {}) => {
  if (!url && !product_pk) {
    throw new Error("❌ Debes proporcionar product_pk o una URL de paginación.");
  }

  const endpoint = url || `/inventory/products/${product_pk}/subproducts/`;

  // Normaliza filtros (booleans -> "true"/"false", limpia vacíos)
  const params = {};
  if (!url) {
    Object.entries(filters || {}).forEach(([k, v]) => {
      if (v === undefined || v === null || v === "") return;
      if (typeof v === "boolean") params[k] = v ? "true" : "false";
      else params[k] = String(v);
    });
  }

  // Clave de caché única por endpoint y filtros
  const cacheKey = url
    ? url
    : `${endpoint}?${new URLSearchParams(params).toString()}`;
  const cached = getCached(cacheKey, 60000);
  if (cached) return cached;

  try {
    const response = await djangoApi.get(endpoint, { params });
    setCached(cacheKey, response.data);
    return response.data;
  } catch (error) {
    const msg = extractErrorMessage(error, "Error al listar subproductos.");
    console.error("❌ listSubproducts:", msg);
    throw new Error(msg);
  }
};

/**
 * ➕ Crea un subproducto asociado a un producto padre.
 * @param {number|string} productId - ID del producto padre
 * @param {FormData} subproductData - FormData con los campos del subproducto
 * @param {AbortSignal} [signal] - AbortSignal opcional
 * @returns {Promise<Object|null>} - Subproducto creado o null si fue cancelado
 */
export const createSubproduct = async (productId, subproductData, signal = null) => {
  if (!productId) throw new Error("❌ Falta productId para crear subproducto.");

  const fd = subproductData instanceof FormData
    ? subproductData
    : (() => {
        const f = new FormData();
        Object.entries(subproductData || {}).forEach(([k, v]) => {
          if (v !== undefined && v !== null && String(v) !== "") f.append(k, v);
        });
        return f;
      })();

  const res = await djangoApi.post(
    `/inventory/products/${productId}/subproducts/create/`,
    fd,
    { signal, headers: { "Content-Type": "multipart/form-data", Accept: "application/json" } }
  );
  invalidatePrefixes(`/inventory/products/${productId}/subproducts/`);
  return res.data;
};

/**
 * ✏️ Actualiza un subproducto (FormData soportado).
 * @param {number|string} productId - ID del producto padre
 * @param {number|string} subproductId - ID del subproducto
 * @param {FormData} subproductData - FormData con los campos
 * @returns {Promise<Object>} - Subproducto actualizado
 */
export const updateSubproduct = async (productId, subproductId, subproductData) => {
  if (!productId || !subproductId || !(subproductData instanceof FormData)) {
    throw new Error("❌ Parámetros inválidos para actualizar subproducto.");
  }

  try {
    const response = await djangoApi.put(
      `/inventory/products/${productId}/subproducts/${subproductId}/`,
      subproductData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          Accept: "application/json",
        },
      }
    );
    invalidatePrefixes(`/inventory/products/${productId}/subproducts/`);
    return response.data;
  } catch (error) {
    const msg = extractErrorMessage(error, "No se pudo actualizar el subproducto.");
    console.error("❌ Error al actualizar subproducto:", msg, error?.response?.data || "");
    throw new Error(msg);
  }
};

/**
 * 🗑️ Elimina (soft delete) un subproducto.
 * @param {number|string} product_pk - ID del producto padre
 * @param {number|string} subp_pk - ID del subproducto
 * @returns {Promise<void>} - Lanza error si falla
 */
export const deleteSubproduct = async (product_pk, subp_pk) => {
  if (!product_pk || !subp_pk) {
    throw new Error("Se requieren product_pk y subp_pk para eliminar un subproducto.");
  }

  try {
    await djangoApi.delete(`/inventory/products/${product_pk}/subproducts/${subp_pk}/`, {
      headers: { Accept: "application/json" },
    });
    invalidatePrefixes(`/inventory/products/${product_pk}/subproducts/`);
  } catch (error) {
    const msg = extractErrorMessage(error, "No se pudo eliminar el subproducto.");
    console.error("❌ Error al eliminar subproducto:", msg, error?.response?.data || "");
    throw new Error(msg);
  }
};
