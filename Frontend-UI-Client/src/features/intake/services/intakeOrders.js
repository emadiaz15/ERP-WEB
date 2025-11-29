// src/features/intake/services/intakeOrders.js
// Servicio para listar Intake Orders con soporte de filtros y cache simple.
// Filtros soportados (query params): created_from, created_to, customer_name, carrier, assigned_to
// Backend endpoint base: /intake/orders/

import { djangoApi } from '@/api/clients';
import { getCached, setCached } from '@/utils/httpCache';

const LIST_TTL = 30_000; // 30s
const LIST_PREFIX = '/intake/orders/';

function buildUrl(base, params = {}) {
  if (!params || Object.keys(params).length === 0) return base;
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return;
    sp.append(k, v);
  });
  const qs = sp.toString();
  return qs ? `${base}?${qs}` : base;
}

function normalizeListResponse(data) {
  if (data && typeof data === 'object' && Array.isArray(data.results)) {
    return {
      results: data.results,
      next: data.next ?? null,
      previous: data.previous ?? null,
      count: data.count ?? data.results.length,
      raw: data,
    };
  }
  if (Array.isArray(data)) {
    return { results: data, next: null, previous: null, count: data.length, raw: data };
  }
  return { results: data ? [data] : [], next: null, previous: null, count: data ? 1 : 0, raw: data };
}

export async function listIntakeOrders(params = {}, options = {}) {
  const url = buildUrl(LIST_PREFIX, params);
  const ttl = options.ttlMs ?? LIST_TTL;
  if (!options.force) {
    const cached = getCached(url, ttl);
    if (cached) return normalizeListResponse(cached);
  }
  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return normalizeListResponse(data);
}

export async function updateIntakeOrder(id, data) {
  const { data: resp } = await djangoApi.patch(`/intake/orders/${id}/`, data);
  return resp;
}

export async function createIntakeOrder(data) {
  // Espera payload con campos: customer_name, carrier, locality, notes, declared_value, items(optional)
  const { data: resp } = await djangoApi.post('/intake/orders/', data);
  return resp;
}

export async function deleteIntakeOrder(id) {
  await djangoApi.delete(`/intake/orders/${id}/`);
  return true;
}

export default { listIntakeOrders, updateIntakeOrder, deleteIntakeOrder, createIntakeOrder };
