import { djangoApi } from "@/api/clients";
import { getCached, setCached } from "@/utils/httpCache";

/**
 * 🔍 Filtra usuarios con soporte de caché local.
 *
 * @param {Object} filters - Filtros clave-valor (e.g., { is_active: "true" }).
 * @param {string} [url='/users/list/'] - URL base del endpoint.
 * @returns {Promise<Object>} - Respuesta paginada de la API.
 */
export const filterUsers = async (filters = {}, url = '/users/list/') => {
  const params = new URLSearchParams(filters).toString();
  const finalUrl = params ? `${url}?${params}` : url;

  const cached = getCached(finalUrl, 30000);
  if (cached) return cached;

  try {
    const response = await djangoApi.get(finalUrl);

    // Guardamos la respuesta en caché para esa URL
  setCached(finalUrl, response.data);

    return response.data;
  } catch (error) {
    console.error('❌ Error filtrando usuarios:', error.response?.data || error.message);
    throw new Error(error.response?.data?.detail || 'Error al filtrar usuarios');
  }
};

export default {
  filterUsers,
};
