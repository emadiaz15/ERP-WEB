import { djangoApi } from "@/api/clients";
import { getAccessToken } from "@/utils/sessionUtils";
import {
  getCached,
  setCached,
  invalidateExact,
  invalidatePrefixes,
  cacheKey
} from "@/utils/httpCache";

// ✅ Booleano robusto
const toBool = (v) => {
  if (typeof v === "boolean") return v;
  if (typeof v === "number") return v !== 0;
  if (typeof v === "string") {
    const s = v.trim().toLowerCase();
    if (s === "true" || s === "1") return true;
    if (s === "false" || s === "0" || s === "") return false;
  }
  return Boolean(v);
};

const normalizeNotif = (raw = {}) => {
  // ✅ Aceptar múltiples alias de ID provenientes del backend/WS
  const rawId =
    raw.id ?? raw.uuid ?? raw.notification_id ?? raw.notificationId ?? raw.pk ?? raw._id;
  // ❌ Sin id, descartamos
  if (rawId == null) return null;

  const readRaw = raw.read ?? raw.is_read;
  const read = readRaw == null ? false : toBool(readRaw);

  // created_at con fallback y normalizado a ISO
  const created_at_raw =
    raw.created_at ?? raw.createdAt ?? raw.timestamp ?? raw.created ?? Date.now();
  const created_at = (() => {
    if (typeof created_at_raw === "number") return new Date(created_at_raw).toISOString();
    const d = new Date(created_at_raw);
    return isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString();
  })();

  return {
    ...raw,
    id: rawId,
    read,
    created_at,
    type: raw.type ?? raw.notif_type ?? "generic",
    notif_type: raw.notif_type ?? raw.type ?? "generic",
  };
};

// 📥 Listar notificaciones + unread en una sola llamada (summary)
const NOTIF_SUMMARY_TTL = 10000; // 10s cache TTL
const NOTIF_SUMMARY_MIN_INTERVAL = 5000; // 5s throttle window
let _lastSummaryFetch = 0;
let _lastSummary404 = 0; // timestamp of last 404 for summary
const SUMMARY_404_BACKOFF = 15000; // 15s negative cache window
export const fetchNotificationsSummary = async (params = {}) => {
  if (!getAccessToken()) {
    return {
      count: 0,
      next: null,
      previous: null,
      results: [],
      unread: 0,
      unread_count: 0,
    };
  }
  const { page = 1, page_size = 10, read, type } = params;
  const query = { page, page_size };
  if (read === false) query.unread = true; // compat: read=false => unread only
  if (type) query.type = type;
  const url = `/notifications/summary/?${new URLSearchParams(query).toString()}`;
  const cached = getCached(url, NOTIF_SUMMARY_TTL);
  if (cached) return cached;
  // Negative cache: if we recently got a 404, skip hitting /summary/ again and go straight to fallback
  const nowCheck = Date.now();
  const recently404 = (nowCheck - _lastSummary404) < SUMMARY_404_BACKOFF;
  if (recently404) {
    // Si existe algo en caché lo devolvemos inmediatamente evitando sobrecarga
    if (cached) return cached;
  }
  let data;
  try {
    if (recently404) {
      throw { __skip: true }; // force fallback branch without network
    }
    ({ data } = await djangoApi.get("/notifications/summary/", { params: query }));
  } catch (e) {
    if (e?.response?.status === 404 || e?.__skip) {
      if (!e?.__skip) {
        _lastSummary404 = Date.now();
      }
      // Fallback: usar listado clásico y sintetizar unread con results
      ({ data } = await djangoApi.get("/notifications/", { params: query }));
      if (typeof data.unread !== "number") {
        const calcUnread = Array.isArray(data?.results)
          ? data.results.filter(r => !(r.read || r.is_read)).length
          : 0;
        data.unread = calcUnread;
      }
    } else {
      throw e;
    }
  }
  _lastSummaryFetch = Date.now();
  const normalized = Array.isArray(data?.results)
    ? data.results.map(normalizeNotif).filter(Boolean)
    : [];
  const unread_count = typeof data?.unread === "number" ? data.unread : 0;
  const result = { ...data, unread_count, results: normalized };
  setCached(url, result);
  return result;
};

// Backward compatibility: previous name used by store
export const fetchNotifications = fetchNotificationsSummary;

// Backward compatibility for unread-count: derives from summary
export const fetchUnreadCount = async () => {
  const data = await fetchNotificationsSummary({ page: 1, page_size: 1 });
  return { unread_count: data.unread_count ?? data.unread ?? 0 };
};

// ✅ Marcar UNA como leída (invalida caché)
export const markNotificationRead = async (id) => {
  await djangoApi.post(`/notifications/${id}/read/`);
  // Invalida cualquier summary/list cache y detalle
  invalidatePrefixes(["/notifications/"]); // incluye /notifications/summary/
  return { ok: true };
};

// ✅ Marcar TODAS como leídas (invalida caché)
export const markAllNotificationsRead = async () => {
  const { data } = await djangoApi.post("/notifications/mark-all-read/");
  invalidatePrefixes(["/notifications/"]); // summary incluido
  return data;
};

// (Opcional) Traer detalle por ID (con caché global)
const NOTIF_DETAIL_TTL = 10000; // 10s
export const fetchNotificationById = async (id) => {
  const url = `/notifications/${id}/`;
  const cached = getCached(url, NOTIF_DETAIL_TTL);
  if (cached) return cached;
  try {
    const { data } = await djangoApi.get(url);
    const result = normalizeNotif(data);
    setCached(url, result);
    return result;
  } catch (e) {
    // fallback: buscar en la lista
  const listUrl = `/notifications/summary/?page=1&page_size=50`;
  const cachedList = getCached(listUrl, NOTIF_SUMMARY_TTL);
    let found = null;
    if (cachedList && Array.isArray(cachedList.results)) {
      found = cachedList.results.find((n) => String(n.id) === String(id));
    } else {
      const { data } = await djangoApi.get("/notifications/", {
        params: { page: 1, page_size: 50 },
      });
      found = (data?.results ?? []).find((n) => String(n.id) === String(id));
    }
    const result = found ? normalizeNotif(found) : null;
    setCached(url, result);
    return result;
  }
};
