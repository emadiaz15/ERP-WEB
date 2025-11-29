
// Utilidades para entorno Vite/browser
export function getIsDev() {
  return import.meta.env.DEV;
}
export function getWsUrlNotifications() {
  return import.meta.env.VITE_WS_URL_NOTIFICATIONS || '';
}
export function getWsUrlCrudEvents() {
  return import.meta.env.VITE_WS_URL_CRUD_EVENTS || '';
}
export function getApiBaseUrl() {
  return import.meta.env.VITE_API_BASE_URL || '';
}
