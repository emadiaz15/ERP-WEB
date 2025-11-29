// src/features/product/services/productsTypeahead.js
import { djangoApi } from "@/api/clients";
import { getCached, setCached, invalidateExact } from "@/utils/httpCache";

const TA_TTL = 30_000;
const FILES_TTL = 60_000;

function build(url, params = {}) {
  const [p, q] = url.split("?");
  const sp = new URLSearchParams(q || "");
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.set(k, v);
  });
  const qs = sp.toString();
  return qs ? `${p}?${qs}` : p;
}

/**
 * Busca productos con subproductos por texto libre (code o name).
 * Requiere que el backend acepte has_subproducts=true y (code= / search=).
 */
export async function typeaheadProductsWithSubproducts(query, { page_size = 20 } = {}) {
  const isNum = /^\d+$/.test((query || "").trim());
  const url = build("/products/", {
    status: true,
    has_subproducts: true,
    page_size,
    ...(query ? (isNum ? { code: query } : { search: query }) : {}),
  });

  const cached = getCached(url, TA_TTL);
  if (cached) return cached;

  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return data?.results || data || [];
}

// ✅ Lista serializada por DRF (usa SubproductImageSerializer)
export const listSubproductFiles = async (productId, subproductId) => {
  if (!productId || !subproductId) {
    throw new Error("Faltan productId o subproductId para listar archivos del subproducto.");
  }
  const url = `/inventory/products/${productId}/subproducts/${subproductId}/files/`;
  const cached = getCached(url, FILES_TTL);
  if (cached) return cached;
  try {
    const { data } = await djangoApi.get(url);
    const files = Array.isArray(data) ? data : (data?.files || []);
    setCached(url, files);
    return files;
  } catch (error) {
    const message = error.response?.data?.detail || "Error desconocido al listar archivos del subproducto.";
    console.error("❌ listSubproductFiles:", message);
    throw new Error(message);
  }
};

// ✅ Pide la URL presignada (JSON). NO concatenar rutas extra.
export const downloadSubproductFile = async (productId, subproductId, fileId, signal = null) => {
  if (!productId || !subproductId || !fileId) return null;
  try {
    const { data } = await djangoApi.get(
      `/inventory/products/${productId}/subproducts/${subproductId}/files/${encodeURIComponent(fileId)}/presign/`,
      { signal }
    );
    return data?.url || null;
  } catch (error) {
    console.error("❌ downloadSubproductFile:", error.response?.data || error.message);
    return null;
  }
};

export const uploadSubproductFiles = async (productId, subproductId, files) => {
  if (!productId || !subproductId || !files?.length) {
    throw new Error("Faltan productId, subproductId o archivos para subir al subproducto.");
  }
  const formData = new FormData();
  files.forEach((file) => formData.append("file", file));
  try {
    const { data } = await djangoApi.post(
      `/inventory/products/${productId}/subproducts/${subproductId}/files/upload/`,
      formData
    );
    invalidateExact(`/inventory/products/${productId}/subproducts/${subproductId}/files/`);
    return data;
  } catch (error) {
    const detail = error.response?.data?.detail || "No se pudo subir archivos del subproducto.";
    console.error("❌ uploadSubproductFiles:", detail);
    throw new Error(detail);
  }
};

export const deleteSubproductFile = async (productId, subproductId, fileId) => {
  if (!productId || !subproductId || !fileId) {
    throw new Error("Faltan parámetros necesarios para eliminar archivo de subproducto.");
  }
  const url = `/inventory/products/${productId}/subproducts/${subproductId}/files/`;
  try {
    await djangoApi.delete(
      `/inventory/products/${productId}/subproducts/${subproductId}/files/${encodeURIComponent(fileId)}/delete/`
    );
    invalidateExact(url);
  } catch (error) {
    const reason = error.response?.data?.detail || "Error al eliminar archivo de subproducto.";
    console.error(`❌ deleteSubproductFile (${fileId}):`, reason);
    throw new Error(reason);
  }
};
