import { djangoApi } from "@/api/clients";

/**
 * Obtiene los metadatos públicos de un producto y sus archivos multimedia
 * según el código proporcionado. Utiliza el endpoint sin autenticación.
 */
export const fetchPublicProductFilesByCode = async (code) => {
  const cleanedCode = (code ?? "").trim();
  if (!cleanedCode) {
    throw new Error("Debes indicar un código de producto.");
  }

  try {
    const response = await djangoApi.get("/inventory/public/products/files/", {
      params: { code: cleanedCode },
    });

    const payload = response?.data;
    if (!payload || typeof payload !== "object") {
      throw new Error("La API no devolvió información válida del producto.");
    }

    return {
      product: payload.product ?? null,
      files: Array.isArray(payload.files) ? payload.files : [],
    };
  } catch (error) {
    const detail =
      error?.response?.data?.detail ||
      error?.message ||
      "No fue posible recuperar los archivos públicos del producto.";
    throw new Error(detail);
  }
};
