// src/features/product/utils/queryKeys.js

// Normaliza filtros para que el objeto sea estable como parte de la queryKey
function normalizeFilters(filters) {
  if (!filters) return {};
  const out = {};
  Object.keys(filters)
    .sort()
    .forEach((k) => {
      const v = filters[k];
      if (v === undefined || v === null || v === "") return;
      if (typeof v === "boolean") out[k] = v ? "true" : "false";
      else out[k] = String(v);
    });
  return out;
}

export const productKeys = {
  // ======================
  // NAMESPACE raíz
  // ======================
  root: ["products"],                // NUEVO nombre
  base: ["products"],                // Alias compat. con código previo

  // ======================
  // PRODUCTO (nivel padre)
  // ======================
  // Compat: listado/filters/paginación de productos
  list: (filters = {}, pageUrl = null) => {
    const norm = normalizeFilters(filters);
    return [...productKeys.base, "list", { pageUrl: pageUrl || null, ...norm }];
  },
  // Compat: detalle y media de producto
  detail: (productId) => [...productKeys.base, "detail", productId],
  files: (productId) => [...productKeys.base, "files", productId],

  // NUEVOS helpers explícitos
  product: (productId) => ["products", productId],
  subproducts: (productId) => ["products", productId, "subproducts"],

  // ======================
  // SUBPRODUCTOS
  // ======================
  /**
   * Prefijo ESTABLE del listado (sin paginación/filters) — ideal para invalidar todo el listado.
   * 👉 Usado por los hooks: productKeys.subproductsList(productId)
   */
  subproductsList: (productId) => ["products", productId, "subproducts", "list"],

  /**
   * Clave concreta de UNA página del listado (con paginación y filtros)
   * 👉 Usado por useListSubproducts(productId, pageUrl, filters)
   */
  subproductList: (productId, pageUrl = null, filters = {}) => [
    "products",
    productId,
    "subproducts",
    "list",
    { filters: normalizeFilters(filters), pageUrl: pageUrl ?? null },
  ],

  // Detalle de un subproducto
  subproductDetail: (productId, subproductId) => [
    "products",
    productId,
    "subproducts",
    "detail",
    subproductId,
  ],

  // Archivos de un subproducto
  subproductFiles: (productId, subproductId) => [
    "products",
    productId,
    "subproducts",
    "files",
    subproductId,
  ],

  /**
   * Utilidad para predicados (useDeleteSubproduct)
   */
  prefixMatch: (key) => Array.isArray(key) && key[0] === "products",
};

export default productKeys;
