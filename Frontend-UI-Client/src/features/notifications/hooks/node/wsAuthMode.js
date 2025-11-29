// wsAuthMode.node.js (Node/Jest)
export function getWsAuthMode() {
  return (typeof process !== "undefined" && process.env && process.env.VITE_WS_AUTH_MODE)
    ? process.env.VITE_WS_AUTH_MODE.trim()
    : "query";
}
