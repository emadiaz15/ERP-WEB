import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

import Toolbar from "../../../components/common/Toolbar";
import SuccessMessage from "../../../components/common/SuccessMessage";

import {
  listCuttingOrders,
  updateCuttingOrder,
  cancelCuttingOrder,
} from "../services/cuttingOrders";
import { useAuth } from "../../../context/AuthProvider";
import Layout from "../../../pages/Layout";
import OrderFilter from "../components/OrderFilter";
import CuttingOrderTable from "../components/CuttingOrderTable";
import CuttingOrderModals from "../components/CuttingOrderModals";
import CreateCuttingOrderWizard from "../components/wizard/CreateCuttingOrderWizard";

import { useLocation } from "react-router-dom";

const CuttingOrdersList = () => {
  const [orders, setOrders] = useState([]);
  const [initialLoaded, setInitialLoaded] = useState(false);

  const [nextPage, setNextPage] = useState(null);
  const [isFetching, setIsFetching] = useState(false);
  const [isFetchingNext, setIsFetchingNext] = useState(false);

  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [filters, setFilters] = useState({}); // ← recibe { created_from, created_to, customer, order_number, workflow_status }

  const [modalState, setModalState] = useState({ type: null, orderData: null });
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  const [isCreateOpen, setIsCreateOpen] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, loading, user } = useAuth();
  const isStaff = !!user?.is_staff;

  // 🔧 Mapea filtros UI (ya normalizados por OrderFilter) → querystring del backend
  const buildUrlWithParams = useCallback(
    (baseUrl = "/cutting/cutting-orders/") => {
      const params = new URLSearchParams();

      const put = (k, v) => {
        const val = typeof v === "string" ? v.trim() : v;
        if (val !== "" && val !== undefined && val !== null) params.append(k, val);
      };

      // Fechas: si tu IsoDateTimeFilter requiere hora, expándelas (opcional)
      const from = filters.created_from ? `${filters.created_from}T00:00:00` : "";
      const to = filters.created_to ? `${filters.created_to}T23:59:59` : "";

      put("created_from", from || filters.created_from);
      put("created_to", to || filters.created_to);

      put("customer", filters.customer);
      put("order_number", filters.order_number);

      // 👇 clave correcta para el backend
      put("workflow_status", filters.workflow_status);

      const qs = params.toString();
      return qs ? `${baseUrl}?${qs}` : baseUrl;
    },
    [filters]
  );

  const fetchOrders = useCallback(async () => {
    setIsFetching(true);
    try {
      const url = buildUrlWithParams("/cutting/cutting-orders/");
      const data = await listCuttingOrders(url);
      if (data?.results) {
        setOrders(data.results);
        setNextPage(data.next);
      } else if (Array.isArray(data)) {
        setOrders(data);
        setNextPage(null);
      } else {
        setOrders([]);
        setNextPage(null);
      }
    } catch (e) {
      console.error("Error fetching orders", e);
      setOrders([]);
      setNextPage(null);
    } finally {
      setIsFetching(false);
      setInitialLoaded(true);
    }
  }, [buildUrlWithParams]);

  // Refrescar en eventos realtime (crear/actualizar/eliminar orden de corte)
  useEffect(() => {
    // Dedupe basado en window Map para compartir entre montajes
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
      if (!msg || msg.model !== 'CuttingOrder') return;
      const k = `CuttingOrder:${msg.event}:${msg.payload?.id ?? 'any'}`;
      if (shouldDedupe(k)) return;
      // Pequeño delay para evitar carreras con invalidaciones backend
      setTimeout(() => fetchOrders(), 150);
    }
    window.addEventListener('realtime-crud-event', onRealtime);
    return () => window.removeEventListener('realtime-crud-event', onRealtime);
  }, [fetchOrders]);

  const fetchNext = useCallback(async () => {
    if (!nextPage || isFetchingNext) return;
    setIsFetchingNext(true);
    try {
      const data = await listCuttingOrders(nextPage);
      if (data?.results) {
        setOrders((prev) => [...prev, ...data.results]);
        setNextPage(data.next);
      } else if (Array.isArray(data)) {
        setOrders((prev) => [...prev, ...data]);
        setNextPage(null);
      } else {
        setNextPage(null);
      }
    } catch (e) {
      console.error("Error fetching next page", e);
    } finally {
      setIsFetchingNext(false);
    }
  }, [nextPage, isFetchingNext]);

  // 🔁 carga inicial
  useEffect(() => {
    if (!loading) {
      if (!isAuthenticated) return navigate("/");
      fetchOrders();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, loading, navigate]); // ← fetchOrders fuera de deps

  // Si viene con state.openOrderModalId, busca y abre el modal
  useEffect(() => {
    if (location.state && location.state.openOrderModalId && orders.length > 0) {
      const orderId = location.state.openOrderModalId;
      const found = orders.find((o) => String(o.id) === String(orderId));
      if (found) {
        setModalState({ type: "view", orderData: found });
        // Limpia el state para evitar reabrir al navegar
        navigate(location.pathname, { replace: true, state: {} });
      } else {
        // Si no está en la lista, intenta buscarlo por API y abrir modal
        import("../services/cuttingOrders").then(({ getCuttingOrder }) => {
          getCuttingOrder(orderId).then((order) => {
            if (order) setModalState({ type: "view", orderData: order });
            navigate(location.pathname, { replace: true, state: {} });
          });
        });
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state, orders]);

  // ✅ refetch cuando cambian los filtros (ignora primer render)
  useEffect(() => {
    if (!loading && isAuthenticated && initialLoaded) {
      setOrders([]);     // opcional: limpia mientras busca
      setNextPage(null); // opcional: resetea paginación
      fetchOrders();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters]); // ← solo depende de filters

  const handleShowSuccess = (msg) => {
    setSuccessMessage(msg);
    setShowSuccess(true);
    fetchOrders();
    window.setTimeout(() => setShowSuccess(false), 3000);
  };

  const handleUpdateOrder = async (payload) => {
    try {
      await updateCuttingOrder(payload.id, payload);
      handleShowSuccess(`Orden #${payload.id} actualizada`);
    } catch (e) {
      console.error(e);
    } finally {
      setModalState({ type: null, orderData: null });
    }
  };

  const handleDeleteOrder = async (id) => {
    setIsDeleting(true);
    try {
      await cancelCuttingOrder(id);
      handleShowSuccess(`Orden #${id} cancelada con éxito`);
    } catch (e) {
      setDeleteError(e.response?.data?.detail || e.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const clearDeleteError = () => setDeleteError(null);

  const openView = (order) => setModalState({ type: "view", orderData: order });
  const openEdit = (order) => setModalState({ type: "edit", orderData: order });
  const openDeleteConfirm = (order) => setModalState({ type: "deleteConfirm", orderData: order });

  const kpiText =
    (isFetching && !initialLoaded) ? "cargando…" : `${orders.length}${nextPage ? "+" : ""} órdenes`;

  return (
    <Layout isLoading={!initialLoaded || isFetching}>
      {showSuccess && (
        <div className="fixed top-20 right-5 z-[10000]">
          <SuccessMessage message={successMessage} onClose={() => setShowSuccess(false)} />
        </div>
      )}

      <div className="p-3 md:p-4 lg:p-6 mt-6">
        <Toolbar
          title="Órdenes de Corte"
          titleRight={kpiText}
          buttonText={isStaff ? "Crear Orden de Corte" : undefined}
          onButtonClick={isStaff ? () => setIsCreateOpen(true) : undefined}
        />

        <OrderFilter
          filters={filters}
          onFilterChange={(f) => setFilters(f)}
        />

        <CuttingOrderTable
          orders={orders}
          onView={openView}
          onEdit={openEdit}
          onDelete={openDeleteConfirm}
          onLoadMore={fetchNext}
          hasNextPage={Boolean(nextPage)}
          isFetchingNextPage={isFetchingNext}
        />

        <CuttingOrderModals
          modalState={modalState}
          closeModal={() => setModalState({ type: null, orderData: null })}
          onUpdateOrder={handleUpdateOrder}
          onDeleteOrder={handleDeleteOrder}
          isDeleting={isDeleting}
          deleteError={deleteError}
          clearDeleteError={clearDeleteError}
        />

        <CreateCuttingOrderWizard
          isOpen={isCreateOpen}
          onClose={() => setIsCreateOpen(false)}
          onSave={(created) =>
            handleShowSuccess(
              created?.id
                ? `Orden #${created.id} creada correctamente`
                : "Orden creada correctamente"
            )
          }
          hideOperatorToggle={false}
          allowEmptyItemsDefault={true}
          embedded={false}
        />
      </div>
    </Layout>
  );
};

export default CuttingOrdersList;
