// src/api/clients.js
import axios from "axios";
import { getAccessToken, clearTokens } from "@/utils/sessionUtils";

// 🧭 En dev, lo ideal es base relativa y que Vite proxee.
// En prod, podés setear VITE_API_BASE_URL con un absoluto si querés.
import { getApiBaseUrl } from "@/utils/getApiBaseUrl";
const API_BASE_URL = getApiBaseUrl();

// ─────────────────────────────────────────────────────────────
// 🔧 Factory de clientes con configuración fija (Django)
// ─────────────────────────────────────────────────────────────
const createApiClient = () => {
  const instance = axios.create({ baseURL: API_BASE_URL });

  instance.interceptors.request.use((config) => {
    const token = getAccessToken();
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });

  instance.interceptors.response.use(
    (res) => res,
    (err) => {
      if (err.response?.status === 401) {
        const hadAuthHeader = Boolean(err.config?.headers?.Authorization);
        const hasStoredToken = Boolean(getAccessToken());
        const currentPath = typeof window !== "undefined" ? window.location.pathname : "";
        const isPublicSurface = currentPath === "/" || currentPath === "/login" || currentPath.startsWith("/public/");

        // Solo notificamos expiración si la request se hizo autenticada
        if (hadAuthHeader || hasStoredToken) {
          clearTokens();
          if (!isPublicSurface) {
            window.dispatchEvent(new Event("sessionExpired"));
          }
        }
      }
      return Promise.reject(err);
    }
  );

  return instance;
};

// ─────────────────────────────────────────────────────────────
// 🎯 Cliente principal para Django
// ─────────────────────────────────────────────────────────────
export const djangoApi = createApiClient();

// ─────────────────────────────────────────────────────────────
// 📤 Exportación utilitaria
// ─────────────────────────────────────────────────────────────
export { djangoApi as axiosInstance };
