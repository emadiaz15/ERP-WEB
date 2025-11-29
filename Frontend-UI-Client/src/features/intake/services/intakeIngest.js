// Servicio de ingesta manual reutilizando endpoint /intake/ingest/ (order_ingest_views.py)
import { djangoApi } from '@/api/clients';

export async function ingestIntakeOrder(payload) {
  const { data } = await djangoApi.post('/intake/ingest/', payload);
  return data; // {status, data: { order_id, created, items_created, cutting_orders_created, ... }}
}

export async function assignIntakeOrder(id, assigned_to) {
  const { data } = await djangoApi.post(`/intake/orders/${id}/assign/`, { assigned_to });
  return data;
}

export default { ingestIntakeOrder, assignIntakeOrder };
