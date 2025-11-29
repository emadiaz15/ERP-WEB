// wsAuthMode.js (browser)
export function getWsAuthMode() {
  return (typeof import.meta !== "undefined" && import.meta.env && import.meta.env.VITE_WS_AUTH_MODE)
    ? import.meta.env.VITE_WS_AUTH_MODE.trim()
    : "query";
}
