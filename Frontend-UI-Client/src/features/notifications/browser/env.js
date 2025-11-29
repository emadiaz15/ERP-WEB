// env.js (browser)
export function getIsDev() {
  return typeof import.meta !== "undefined" && import.meta.env && !!import.meta.env.DEV;
}
