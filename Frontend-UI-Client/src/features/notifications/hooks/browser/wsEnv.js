// wsEnv.js (browser)
export function getIsDev() {
  return typeof import.meta !== "undefined" && import.meta.env && !!import.meta.env.DEV;
}
export function getWsUrl() {
  return (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_WS_URL)
    ? import.meta.env.VITE_WS_URL.trim()
    : "";
}
export function getApiBaseUrl() {
  return (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_API_BASE_URL)
    ? import.meta.env.VITE_API_BASE_URL.trim()
    : "";
}
