// src/features/intake/pages/IntakeOrdersList.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Layout from '@/pages/Layout';
import Toolbar from '@/components/common/Toolbar';
import SuccessMessage from '@/components/common/SuccessMessage';
import { useAuth } from '@/context/AuthProvider';
import IntakeOrderFilter from '../components/IntakeOrderFilter';
import IntakeOrderTable from '../components/IntakeOrderTable';
import CreateIntakeOrderWizard from '../components/CreateIntakeOrderWizard';
import IntakeOrderDetailDrawer from '../components/IntakeOrderDetailDrawer';
// Legacy direct service imports removed in favor of centralized store/api
// import { listIntakeOrders, updateIntakeOrder, deleteIntakeOrder } from '../services/intakeOrders';
import useIntakeOrdersStore from '../store/useIntakeOrdersStore';

/*
  Pattern replicated from CuttingOrdersList:
  - isFetching / isFetchingNext distinction
  - success message overlay
  - realtime listener (crud events) with dedupe
  - buildUrlWithParams (querystring) to unify filtering
  - kpiText logic and pagination sentinel
  Differences retained:
  - Drawer used for view/edit instead of modals/wizard
  - No creation flow (ingesta es automática)
*/

const IntakeOrdersList = () => {
  const {
    items: orders,
    page,
    totalPages,
    loading: isFetching,
    fetchOrders,
    prefetchNextPage,
    setPage,
    setFilter,
    refreshSummary,
    optimisticDelete,
    optimisticUpdate,
  } = useIntakeOrdersStore();
  const [initialLoaded, setInitialLoaded] = useState(false);
  const [isFetchingNext, setIsFetchingNext] = useState(false); // local sentinel for load more UI only
  const [hasNext, setHasNext] = useState(false);

  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [filters, setFilters] = useState({}); // local UI state -> mirrored into store on change

  const [detailOpen, setDetailOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);
  const [detailOrder, setDetailOrder] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading } = useAuth();

  // Construir URL con filtros (similar a CuttingOrdersList)
  // Translate UI filters to store filters (normalized field names expected by buildParams in store)
  const pushFiltersToStore = useCallback((f) => {
    setFilter({
      search: f.customer_name || '',
      // mapping additional filters if backend supports them
      status: f.flow_status,
    });
  }, [setFilter]);

  const fetchInitial = useCallback(async () => {
    await fetchOrders({ force: true });
    setInitialLoaded(true);
  }, [fetchOrders]);

  const fetchNext = useCallback(async () => {
    if (isFetchingNext) return;
    const next = page + 1;
    if (next > totalPages) return;
    setIsFetchingNext(true);
    try {
      // setPage triggers fetchOrders via store; we rely on existing items replacement (pagination strategy: page slice)
      setPage(next);
      await fetchOrders();
    } finally {
      setIsFetchingNext(false);
    }
  }, [isFetchingNext, page, totalPages, setPage, fetchOrders]);

  // Carga inicial y protección de ruta
  useEffect(() => {
    if (loading) return;
    if (!isAuthenticated) return navigate('/');
    // Sólo primera vez
    if (!initialLoaded) fetchInitial();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, loading, navigate, fetchInitial, initialLoaded]);

  // Realtime CRUD events (asumiendo mismo canal y msg.model = 'IntakeOrder')
  useEffect(() => {
    const map = (typeof window !== 'undefined') ? (window.__rtDedupe ||= new Map()) : new Map();
    const shouldDedupe = (key, ttlMs = 700) => {
      const now = Date.now();
      const last = map.get(key) || 0;
      if (now - last < ttlMs) return true;
      map.set(key, now); return false;
    };
    function onRealtime(e) {
      const msg = e?.detail;
      if (!msg || msg.model !== 'IntakeOrder') return;
      const k = `IntakeOrder:${msg.event}:${msg.payload?.id ?? 'any'}`;
      if (shouldDedupe(k)) return;
      setTimeout(() => fetchOrders({ force: true }), 150);
    }
    window.addEventListener('realtime-crud-event', onRealtime);
    return () => window.removeEventListener('realtime-crud-event', onRealtime);
  }, [fetchOrders]);

  // Refetch cuando cambian filtros (después de primera carga)
  useEffect(() => {
    if (!initialLoaded) return;
    pushFiltersToStore(filters);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, initialLoaded, pushFiltersToStore]);

  const handleShowSuccess = (msg) => {
    setSuccessMessage(msg);
    setShowSuccess(true);
    fetchOrders({ force: true });
    window.setTimeout(() => setShowSuccess(false), 3000);
  };

  const openView = (order) => {
    setDetailOrder(order);
    setDetailOpen(true);
  };

  const openEdit = (order) => {
    // reutilizamos drawer; se abrirá y usuario presiona Editar adentro
    setDetailOrder(order);
    setDetailOpen(true);
  };

  const openDeleteConfirm = (order) => {
    if (!window.confirm(`¿Eliminar (soft) la nota de pedido #${order.order_number || order.id}?`)) return;
    handleDeleteOrder(order.id);
  };

  const handleDeleteOrder = async (id) => {
    setIsDeleting(true);
    try {
      await optimisticDelete(id); // store handles refresh summary later
      handleShowSuccess(`Nota #${id} eliminada`);
      if (detailOrder?.id === id) {
        setDetailOpen(false);
        setDetailOrder(null);
      }
    } catch (e) {
      setDeleteError(e.response?.data?.detail || e.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleUpdateOrder = async (payload) => {
    try {
      await optimisticUpdate(payload.id, payload);
      handleShowSuccess(`Nota #${payload.id} actualizada`);
    } catch (e) {
      console.error(e);
    } finally {
      // Drawer se cierra manualmente dentro si se quiere
    }
  };

  const handleSaved = useCallback((updated) => {
    if (!updated) return;
    // store already updated optimistically via optimisticUpdate / or direct edits
    handleShowSuccess(`Nota #${updated.id} guardada`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [detailOrder]);

  useEffect(() => {
    // update pagination hasNext when page or totalPages change
    setHasNext(page < totalPages);
  }, [page, totalPages]);

  const kpiText = (isFetching && !initialLoaded)
    ? 'cargando…'
    : `${orders.length}${hasNext ? '+' : ''} notas`;

  // Evita "flicker" de la superposición global: sólo mostrar overlay en la carga inicial
  const isInitialLoading = !initialLoaded && isFetching;

  return (
    <Layout isLoading={isInitialLoading}>
      {showSuccess && (
        <div className="fixed top-20 right-5 z-[10000]">
          <SuccessMessage message={successMessage} onClose={() => setShowSuccess(false)} />
        </div>
      )}

      <div className="p-3 md:p-4 lg:p-6 mt-6">
        <Toolbar
          title="Notas de Pedido"
          titleRight={kpiText}
          actions={[
            {
              label: 'Crear Nota',
              onClick: () => setCreateOpen(true),
              variant: 'primary'
            }
          ]}
        />

        <IntakeOrderFilter value={filters} onChange={(f) => setFilters(f)} />

        <IntakeOrderTable
          orders={orders}
          onView={openView}
          onEdit={openEdit}
          onDelete={openDeleteConfirm}
          onLoadMore={fetchNext}
          hasNextPage={hasNext}
          isFetchingNextPage={isFetchingNext}
          loading={isFetching && !initialLoaded}
        />

        {/* Drawer de detalle / edición inline */}
        <IntakeOrderDetailDrawer
          open={detailOpen}
          order={detailOrder}
          onClose={() => setDetailOpen(false)}
          onSaved={handleSaved}
        />

        <CreateIntakeOrderWizard
          open={createOpen}
          onClose={() => setCreateOpen(false)}
          onCreated={(summary) => {
            // Prepend si no existe
            if (summary && summary.id && !orders.find(o => o.id === summary.id)) {
              // No tenemos setOrders local; forzamos un refetch para coherencia.
              fetchOrders({ force: true });
              handleShowSuccess('Nota creada con matching');
            }
          }}
        />

        {deleteError && (
          <div className="mt-4 text-sm text-error-600">
            Error eliminando: {deleteError}
            <button
              className="ml-2 underline"
              onClick={() => setDeleteError(null)}
            >cerrar</button>
          </div>
        )}
        {isDeleting && (
          <div className="mt-2 text-xs text-amber-600">Eliminando…</div>
        )}
      </div>
    </Layout>
  );
};

export default IntakeOrdersList;
