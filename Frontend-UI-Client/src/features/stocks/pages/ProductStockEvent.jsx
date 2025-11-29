// Helpers para tipo de evento, extracción de OC y formato de fecha
// Fecha y hora en formato dd/mm/aaaa HH:mm (24h)
const formatDate = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    const fecha = d.toLocaleDateString('es-AR');
    const hora = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false });
    return `${fecha} ${hora}`;
};

const getTypeMeta = (event_type, quantity_change) => {
    const q = Number(quantity_change || 0);
    const t = String(event_type || '').toLowerCase();
    const salidas = new Set(['egreso_venta', 'egreso_corte', 'egreso_ajuste', 'traslado_salida']);
    const entradas = new Set(['ingreso', 'ingreso_ajuste', 'traslado_entrada', 'ingreso_inicial']);
    if (entradas.has(t)) return { label: 'Ingreso', sign: '+', icon: <ArrowDownIcon className="h-4 w-4" />, className: 'bg-green-500' };
    if (salidas.has(t)) return { label: 'Egreso', sign: '-', icon: <ArrowUpIcon className="h-4 w-4" />, className: 'bg-red-500' };
    return { label: 'Ajuste', sign: q >= 0 ? '+' : '-', icon: <KeyIcon className="h-4 w-4" />, className: 'bg-blue-500' };
};

const extractOC = (notes) => {
    const m = String(notes || '').match(/orden\s+de\s+corte\s*#\s*(\d+)/i);
    return m ? m[1] : null;
};
// src/features/stocks/pages/ProductStockEvent.jsx
import React, { useMemo, useState, useEffect, useCallback, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { ArrowUpIcon, ArrowDownIcon, KeyIcon, EyeIcon } from '@heroicons/react/24/solid';

import ViewCuttingOrderModal from '@/features/cuttingOrder/components/ViewCuttingOrderModal';
import { useCuttingOrderDetail } from '../hooks/useCuttingOrderDetail';
import Layout from '@/pages/Layout';
import StockEventToolbar from '../components/StockEventToolbar';
import StockDateFilter from '../components/StockDateFilter';
import StockEventTable from '../components/StockEventTable';
import SentinelRow from '../components/SentinelRow';
import AdjustStockModal from '../components/AdjustStockModal';
import { useInfinitePageQuery } from '@/hooks/useInfinitePageQuery';

function ProductStockEvent() {
    const { productId } = useParams();
    const [showAdjustModal, setShowAdjustModal] = useState(false);
    const [adjustLoading, setAdjustLoading] = useState(false);
    const [adjustError, setAdjustError] = useState(null);
    const [openOC, setOpenOC] = useState(null); // orderId (number) o null
    const [useAgg, setUseAgg] = useState(true);

    // Alternar entre endpoint agregado y directo según error
    const baseUrl = `/stocks/products/${productId}/stock/events/`;
    const aggUrl = `/stocks/products/${productId}/subproducts/stock/events/`;
    const url = useAgg ? aggUrl : baseUrl;

    const {
        items: stockEvents,
        isLoading: loading,
        isError,
        error,
        fetchNextPage,
        hasNextPage,
        isFetchingNextPage,
        invalidate,
    } = useInfinitePageQuery({
        key: ['stockEvents', productId, useAgg ? 'agg' : 'direct'],
        url,
        pageSize: 20,
        enabled: !!productId,
    });

    // ↔️ alternar entre agregado ↔ directo cuando llega 400/404
    useEffect(() => {
        if (!isError || !error) return;
        const status = error?.response?.status ?? error?.status ?? error?.code;
        if ((status === 400 || status === 404) && useAgg) {
            setUseAgg(false); // probar directo
        } else if ((status === 400 || status === 404) && !useAgg) {
            setUseAgg(true);  // volver a agregado
        }
    }, [isError, error, useAgg]);

    // 🔒 blindaje de datos: filtrar nulls directamente
    const orderedAsc = useMemo(
        () => {
            const safeEvents = Array.isArray(stockEvents) ? stockEvents.filter(Boolean) : [];
            return [...safeEvents].sort(
                (a, b) => new Date(a?.created_at || 0) - new Date(b?.created_at || 0)
            );
        },
        [stockEvents]
    );

    const handleOpenOC = useCallback((orderId) => setOpenOC(orderId), []);
    const handleCloseOC = useCallback(() => setOpenOC(null), []);

    // Calcular stock resultante de forma estable
    const rows = useMemo(() => {
        let running = 0;
        return [...orderedAsc]
            .map((ev) => {
                if (!ev || typeof ev !== 'object') return null; // ⛑️
                const qty = Number(ev.quantity_change || 0);
                running += qty;

                const meta = getTypeMeta(ev.event_type, qty) || { label: '—', sign: '', icon: null, className: 'bg-gray-400' };
                const qtyAbs = Math.abs(qty);
                const ocNumber = extractOC(ev.notes);
                const createdBy =
                    typeof ev.created_by === 'object'
                        ? ev.created_by?.username || ev.created_by?.id || '—'
                        : ev.created_by ?? '—';

                // Solo permitir abrir modal para egresos con nro OC
                const isEgresoCorte = String(ev.event_type).toLowerCase() === 'egreso_corte';
                const canOpenOC = isEgresoCorte && !!ocNumber;

                return {
                    'Fecha': formatDate(ev.created_at),
                    'Tipo': (
                        <span className={`px-2 py-1 rounded text-sm font-semibold inline-flex items-center gap-1 ${meta.className} text-white`}>
                            {meta.icon}{meta.label}
                        </span>
                    ),
                    'Cantidad': (
                        <span className={`px-2 py-1 rounded text-sm font-semibold inline-flex items-center gap-1 ${meta.className} text-white`}>
                            {meta.icon}{`${meta.sign}${qtyAbs}`}
                        </span>
                    ),
                    'Nro Orden de Corte': (
                        <div className="flex items-center gap-2">
                            <span>{ocNumber || '—'}</span>
                            <button
                                type="button"
                                className={`bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors disabled:opacity-50 ${canOpenOC ? '' : 'opacity-50 cursor-not-allowed'}`}
                                title="Ver orden de corte"
                                disabled={!canOpenOC}
                                onClick={canOpenOC ? () => handleOpenOC(Number(ocNumber)) : undefined}
                            >
                                <EyeIcon className="w-5 h-5 text-white" />
                            </button>
                        </div>
                    ),
                    'Usuario': createdBy,
                    'Descripción': ev.notes || '—',
                    'Stock Resultante': <span className="text-gray-700 font-extrabold">{running}</span>,
                };
            })
            .filter(Boolean)
            .reverse();
    }, [orderedAsc, handleOpenOC]);

    // Mensaje amigable para 404 en la primera página
    const firstPage404 =
        isError && (error?.response?.status === 404 || error?.status === 404) && rows.length === 0;

    // Hook para detalle de OC
    const { data: ocDetail, loading: loadingOC, error: errorOC } = useCuttingOrderDetail(openOC, { enabled: !!openOC });

    const handleAdjustStock = async (values) => {
        setAdjustLoading(true);
        setAdjustError(null);
        try {
            await adjustProductStock(productId, values);
            setShowAdjustModal(false);
            // Refetch con pequeño retraso para evitar carreras
            setTimeout(() => invalidate(), 150);
        } catch (err) {
            setAdjustError(err?.message || 'Error al ajustar stock');
        } finally {
            setAdjustLoading(false);
        }
    };

    // Refrescar en eventos realtime (crear/actualizar/eliminar evento de stock) con dedupe
    useEffect(() => {
        const map = (typeof window !== 'undefined') ? (window.__rtDedupe ||= new Map()) : new Map();
        const shouldDedupe = (key, ttlMs = 700) => {
            const now = Date.now();
            const last = map.get(key) || 0;
            if (now - last < ttlMs) return true;
            map.set(key, now);
            return false;
        };
        function onRealtime(e) {
            const msg = e?.detail;
            if (!msg || msg.model !== 'StockEvent') return;
            const k = `StockEvent:${msg.event}:product:${productId ?? 'any'}`;
            if (shouldDedupe(k)) return;
            setTimeout(() => invalidate(), 150);
        }
        window.addEventListener('realtime-crud-event', onRealtime);
        return () => window.removeEventListener('realtime-crud-event', onRealtime);
    }, [invalidate, productId]);

    return (
        <Layout isLoading={loading}>
            <div className="p-3 md:p-4 lg:p-6 mt-6">
                <StockEventToolbar
                    title="Historial de Stock"
                    backTo="/product-list"
                    configItems={[{ label: 'Ajustar Stock', onClick: () => setShowAdjustModal(true), adminOnly: true }]}
                />

                <StockDateFilter onFilterChange={invalidate} />

                {firstPage404 && (
                    <div className="p-4 text-center text-gray-500">
                        No hay eventos de stock para este producto.
                    </div>
                )}
                {!firstPage404 && error && error.message && (
                    <div className="text-yellow-500 text-center mt-4">{error.message}</div>
                )}

                {!loading && (
                    <div className="relative overflow-x-auto shadow-md sm:rounded-lg flex-1 mt-2">
                        <StockEventTable
                            headers={['Fecha y Hora (dd/mm/aaaa HH:mm)', 'Tipo', 'Cantidad', 'Nro Orden de Corte', 'Usuario', 'Descripción', 'Stock Resultante']}
                            rows={rows}
                            columnClasses={['w-40', 'w-28', 'w-28', 'w-44', 'w-40', 'w-96', 'w-32']}
                            sentinelRow={
                                hasNextPage ? (
                                    <SentinelRow
                                        onLoadMore={fetchNextPage}
                                        disabled={!hasNextPage}
                                        isLoadingMore={isFetchingNextPage}
                                        colSpan={7}
                                    />
                                ) : null
                            }
                        />
                        {rows.length === 0 && !loading && (
                            <div className="p-6 text-center text-gray-500">Sin eventos de stock.</div>
                        )}
                    </div>
                )}

                <AdjustStockModal
                    open={showAdjustModal}
                    onClose={() => setShowAdjustModal(false)}
                    onSubmit={handleAdjustStock}
                    loading={adjustLoading}
                    error={adjustError}
                />

                {/* Modal de OC: solo renderizar si hay order */}
                {!!openOC && !!ocDetail && (
                    <ViewCuttingOrderModal
                        order={ocDetail}
                        isOpen={true}
                        onClose={handleCloseOC}
                        subproductMap={undefined}
                    />
                )}
            </div>
        </Layout>
    );
}

export default ProductStockEvent;
