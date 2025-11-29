import { djangoApi } from "@/api/clients";
import { clearUsersCache } from "./userCache";
import { extractFileName } from "@/utils/extractFileName";  // ✅ Import del helper

/**
 * 🗑️ Elimina la imagen de perfil de un usuario.
 *
 * @param {string} filePath - Ruta completa o parcial del archivo en el sistema.
 * @param {number|null} userId - ID del usuario (requerido solo si lo hace un admin).
 * @returns {Promise<Object>} - Usuario actualizado sin imagen de perfil.
 */
export const deleteProfileImage = async (filePath, userId = null) => {
  if (!filePath) throw new Error("Falta el ID del archivo a eliminar.");

  // Si la ruta incluye slash, usar el endpoint que acepta file_path como query param
  const needsQuery = filePath.includes('/');
  const encodedPath = encodeURIComponent(filePath);
  try {
    let response;
    if (needsQuery) {
      // Usar POST con body para evitar problemas con slashes codificados en la URL
      response = await djangoApi.post(`/users/image/delete/`, { file_path: filePath, user_id: userId });
    } else {
      const url = userId
        ? `/users/image/${encodedPath}/delete/?user_id=${userId}`
        : `/users/image/${encodedPath}/delete/`;
      response = await djangoApi.delete(url);
    }

    clearUsersCache();
    return response.data;
  } catch (error) {
    console.error("❌ Error al eliminar imagen de perfil:", error.response?.data || error.message);
    throw new Error("No se pudo eliminar la imagen. Intenta nuevamente.");
  }
};

export default deleteProfileImage;
