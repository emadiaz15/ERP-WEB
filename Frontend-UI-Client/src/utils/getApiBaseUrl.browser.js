// src/utils/getApiBaseUrl.browser.js
// Solo para Vite/browser
export function getApiBaseUrl() {
  return (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE_URL)
    ? import.meta.env.VITE_API_BASE_URL
    : "/api/v1";
}
