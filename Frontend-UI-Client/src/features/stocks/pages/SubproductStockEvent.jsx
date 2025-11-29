import React, { useState, useEffect, useCallback, useMemo } from 'react';
import InfiniteScrollSentinelRow from '@/components/common/InfiniteScrollSentinelRow';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowUpIcon, ArrowDownIcon, KeyIcon, EyeIcon } from '@heroicons/react/24/solid';
import ViewCuttingOrderModal from '@/features/cuttingOrder/components/ViewCuttingOrderModal';
import { useCuttingOrderDetail } from '../hooks/useCuttingOrderDetail';

import Toolbar from '@/components/common/Toolbar';
import StockEventTable from '../components/StockEventTable';
import Table from '@/components/common/Table';
import Pagination from '@/components/ui/Pagination';
import StockDateFilter from '../components/StockDateFilter';
import Layout from '@/pages/Layout';
import { useStockSubproductEvents } from '../hooks/useStockSubproductEvents';
import { adjustSubproductStock } from '../services/adjustSubproductStock';
import AdjustStockModal from '../components/AdjustStockModal';

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

const SubproductStockEvent = () => {
    // Estado para modal de OC
    const [openOC, setOpenOC] = useState(null); // orderId (number) o null
    const handleOpenOC = useCallback((orderId) => setOpenOC(orderId), []);
    const handleCloseOC = useCallback(() => setOpenOC(null), []);
    // Filtro local de fechas (usado solo para mostrar el valor actual en el filtro visual)
    const [dateFilter, setDateFilter] = useState({ start_date: '', end_date: '' });

    // Stock events hook
    const { subproductId, productId: paramProductId } = useParams();
    const {
        stockEvents,
        loading,
        error,
        nextPage,
        previousPage,
        fetchStockEvents,
        handleFilterChange,
        refetch,
    } = useStockSubproductEvents(subproductId);

    // Nuevo handler para el filtro de fechas (recibe {start_date, end_date})
    const handleDateFilterChange = useCallback((range) => {
        setDateFilter(range);
        handleFilterChange(range);
    }, [handleFilterChange]);


    // Intentar obtener el productId desde los params o desde el primer evento de stock
    const [productId, setProductId] = useState(paramProductId);

    useEffect(() => {
        if (!productId && stockEvents && stockEvents.length > 0) {
            // Buscar el productId en el primer evento de stock si existe
            const ev = stockEvents[0];
            if (ev && ev.product && (ev.product.id || ev.product.product_id)) {
                setProductId(ev.product.id || ev.product.product_id);
            }
        }
    }, [productId, stockEvents]);

    const navigate = useNavigate();

    // Modal state
    const [showAdjustModal, setShowAdjustModal] = useState(false);
    const [adjustLoading, setAdjustLoading] = useState(false);
    const [adjustError, setAdjustError] = useState(null);

    const orderedAsc = useMemo(
        () => [...stockEvents].sort((a, b) => new Date(a.created_at) - new Date(b.created_at)),
        [stockEvents]
    );

    let running = 0;
    const rows = [...orderedAsc]
        .map((ev) => {
            const qty = Number(ev.quantity_change || 0);
            running += qty;

            const meta = getTypeMeta(ev.event_type, qty);
            const qtyAbs = Math.abs(qty);
            const ocNumber = extractOC(ev.notes);

            const createdBy = ev.user ?? (
                typeof ev.created_by === 'object'
                    ? ev.created_by?.username || ev.created_by?.id || '—'
                    : ev.created_by ?? '—'
            );

            // Solo permitir abrir modal para egresos con nro OC
            const isEgresoCorte = String(ev.event_type).toLowerCase() === 'egreso_corte';
            const canOpenOC = isEgresoCorte && !!ocNumber;

            return {
                Fecha: formatDate(ev.created_at),
                Tipo: (
                    <span className={`px-2 py-1 rounded text-sm font-semibold inline-flex items-center gap-1 ${meta.className} text-white`}>
                        {meta.icon}{meta.label}
                    </span>
                ),
                Cantidad: (
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
                Usuario: createdBy,
                Descripción: ev.notes || '—',
                'Stock Resultante': <span className="text-gray-700 font-extrabold">{running}</span>,
            };
        })
        .reverse();
    // Hook para detalle de OC
    const { data: ocDetail } = useCuttingOrderDetail(openOC, { enabled: !!openOC });

    // Handler for modal submit
    const handleAdjustStock = async (values) => {
        setAdjustLoading(true);
        setAdjustError(null);
        try {
            await adjustSubproductStock(subproductId, values);
            setShowAdjustModal(false);
            setTimeout(() => refetch(), 150); // Refresh con retraso
        } catch (err) {
            setAdjustError(err.message);
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
            const k = `StockEvent:${msg.event}:subproduct:${subproductId ?? 'any'}`;
            if (shouldDedupe(k)) return;
            setTimeout(() => refetch(), 150);
        }
        window.addEventListener('realtime-crud-event', onRealtime);
        return () => window.removeEventListener('realtime-crud-event', onRealtime);
    }, [refetch, subproductId]);

    return (
        <Layout isLoading={loading}>
            <div className="p-3 md:p-4 lg:p-6 mt-6">
                <Toolbar
                    title="Historial de Stock del Subproducto"
                    onBackClick={() => {
                        if (productId) {
                            navigate(`/products/${productId}/subproducts`);
                        } else {
                            navigate(-1); // fallback seguro
                        }
                    }}
                    configItems={[
                        { label: "Ajustar Stock", onClick: () => setShowAdjustModal(true), adminOnly: true },
                    ]}
                />

                {error && <div className="text-yellow-500 text-center mt-4">{error}</div>}

                <StockDateFilter onFilterChange={handleDateFilterChange} />
                {!loading && (
                    <div className="relative overflow-x-auto shadow-md sm:rounded-lg flex-1 mt-2">
                        <StockEventTable
                            headers={['Fecha y Hora (dd/mm/aaaa HH:mm)', 'Tipo', 'Cantidad', 'Nro Orden de Corte', 'Usuario', 'Descripción', 'Stock Resultante']}
                            rows={rows}
                            columnClasses={['w-40', 'w-28', 'w-28', 'w-44', 'w-40', 'w-96', 'w-32']}
                            sentinelRow={
                                nextPage ? (
                                    <InfiniteScrollSentinelRow
                                        onLoadMore={() => fetchStockEvents(nextPage)}
                                        disabled={loading || !nextPage}
                                        isLoadingMore={loading}
                                        colSpan={7}
                                    />
                                ) : null
                            }
                        />
                        {rows.length === 0 && (
                            <div className="p-6 text-center text-gray-500">Sin eventos de stock.</div>
                        )}
                    </div>
                )}

                {/* Modal de ajuste de stock */}
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
};

export default SubproductStockEvent;
