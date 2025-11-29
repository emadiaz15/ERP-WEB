import { djangoApi } from "@/api/clients";
import { getCached, setCached } from "@/utils/httpCache";

export const listUsers = async (url = "/users/list/") => {
  const cached = getCached(url, 30000);
  if (cached) return cached;

  try {
    const response = await djangoApi.get(url);

    if (Array.isArray(response.data?.results)) {
      response.data.results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    setCached(url, response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Error al listar usuarios:", error);
    throw new Error("Error al listar usuarios");
  }
};
