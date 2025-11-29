// src/utils/getApiBaseUrl.node.js
// Versión segura para entorno Node/Jest (sin import.meta)
export function getApiBaseUrl() {
  return process.env.VITE_API_BASE_URL || "/api/v1";
}
