import { djangoApi } from '@/api/clients';

function mapEventToUI(e) {
    const rawType =
        e?.event_type ??
        e?.type ??
        e?.type_display ??
        (typeof e?.description === 'string' && /inicial/i.test(e.description) ? 'ingreso_inicial' : null);

    const createdBy =
        e?.created_by ??
        e?.user ??
        (typeof e?.created_by === 'object' ? e.created_by?.username ?? e.created_by?.id : null) ??
        null;

    return {
        id: e?.id ?? e?._id ?? undefined,
        created_at: e?.created_at ?? e?.date ?? null,
        event_type: (rawType || '').toString().toLowerCase(),
        quantity_change: Number(e?.quantity_change ?? e?.quantity ?? 0),
        notes: e?.notes ?? e?.description ?? null,
        user: e?.user ?? null,
        created_by: createdBy,
        _raw: e,
    };
}

/**
 * Ajusta el stock de un producto y devuelve el evento mapeado para la UI.
 * @param {number|string} productId
 * @param {object} values
 */
export async function adjustProductStock(productId, values) {
    try {
        const { data } = await djangoApi.post(`/stocks/products/${productId}/stock/adjust/`, values);
        return mapEventToUI(data);
    } catch (err) {
        const detail = err?.response?.data?.detail || err?.message || 'Error al ajustar el stock';
        throw new Error(detail);
    }
}
