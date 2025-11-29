
// src/utils/getApiBaseUrl.js
// Compatible con Vite/browser
export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || "/api/v1";
}
