// wsEnv.node.js (Node/Jest)
export function getIsDev() {
  return typeof process !== "undefined" && process.env && !!process.env.NODE_ENV && process.env.NODE_ENV === "development";
}
export function getWsUrl() {
  return (typeof process !== "undefined" && process.env && process.env.VITE_WS_URL)
    ? process.env.VITE_WS_URL.trim()
    : "";
}
export function getApiBaseUrl() {
  return (typeof process !== "undefined" && process.env && process.env.VITE_API_BASE_URL)
    ? process.env.VITE_API_BASE_URL.trim()
    : "";
}
