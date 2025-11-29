// src/features/product/services/products/products.js
import { djangoApi } from "@/api/clients";
import { getCached, setCached, invalidatePrefixes } from "@/utils/httpCache";

/**
 * Obtener lista de productos con paginación y filtros opcionales
 * @param {Object|string} paramsOrUrl - Objeto de filtros o URL de paginación
 */
export const listProducts = async (paramsOrUrl = {}) => {
  let url;
  if (typeof paramsOrUrl === "string") {
    url = paramsOrUrl;
  } else {
    // Filtra parámetros inválidos antes de construir la query
    const cleanParams = { ...paramsOrUrl };
    const pruneEmpty = (v) => v === undefined || v === null || v === "" || v === "undefined";
    if (pruneEmpty(cleanParams.code)) delete cleanParams.code;
    if (pruneEmpty(cleanParams.name)) delete cleanParams.name;
    if (pruneEmpty(cleanParams.category)) delete cleanParams.category;
    const params = new URLSearchParams(cleanParams).toString();
    url = params ? `/inventory/products/?${params}` : "/inventory/products/";
  }
  const cached = getCached(url, 60000);
  if (cached) return cached;
  try {
    const response = await djangoApi.get(url);
    const data = response.data;
    if (Array.isArray(data.results)) {
      data.results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }
    setCached(url, data);
    return data;
  } catch (error) {
    console.error("❌ Error al obtener productos:", error);
    throw new Error(
      error.response?.data?.detail || "Error al obtener la lista de productos."
    );
  }
};

/**
 * Crear un nuevo producto
 * @param {Object|FormData} productData - Datos del producto o FormData con archivos
 */
export const createProduct = async (productData) => {
  if (
    !productData ||
    (typeof productData !== "object" && !(productData instanceof FormData))
  ) {
    throw new Error("Los datos del producto son inválidos.");
  }

  try {
    // Deja que Axios maneje el Content-Type para FormData (boundary)
    const config = {};
    const response = await djangoApi.post(
      "/inventory/products/create/",
      productData,
      config
    );
    invalidatePrefixes("/inventory/products/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al crear el producto:", error);
    throw new Error(
      error.response?.data?.detail || "No se pudo crear el producto."
    );
  }
};

/**
 * Actualizar un producto existente
 * @param {number|string} productId - ID del producto
 * @param {Object|FormData} productData - Datos del producto o FormData con archivos
 */
export const updateProduct = async (productId, productData) => {
  if (
    !productId ||
    (typeof productData !== "object" && !(productData instanceof FormData))
  ) {
    throw new Error("❌ Se requiere un ID y datos válidos para actualizar.");
  }

  const id = String(productId).trim();

  try {
    // Deja que Axios maneje el Content-Type para FormData (boundary)
    const config = {};
    const response = await djangoApi.put(
      `/inventory/products/${id}/`,
      productData,
      config
    );
    invalidatePrefixes("/inventory/products/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al actualizar producto:", error);
    if (error.response?.status === 405) {
      throw new Error(
        `Método \"PUT\" no permitido (código ${error.response.status}). Verifica el endpoint en el backend.`
      );
    }
    throw new Error(
      error.response?.data?.detail || "No se pudo actualizar el producto."
    );
  }
};

/**
 * Eliminar un producto por ID
 * @param {number|string} productId - ID del producto a eliminar
 */
export const deleteProduct = async (productId) => {
  const id = String(productId).trim();

  try {
    const response = await djangoApi.delete(
      `/inventory/products/${id}/`
    );
    invalidatePrefixes("/inventory/products/");
    return response.data;
  } catch (error) {
    console.error("❌ Error al eliminar producto:", error);
    throw new Error(
      error.response?.data?.detail || "No se pudo eliminar el producto."
    );
  }
};
