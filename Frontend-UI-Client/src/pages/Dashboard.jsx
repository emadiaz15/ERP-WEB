import React, { useEffect, useMemo, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "../pages/Layout";
import { useAuth } from "../context/AuthProvider";
import KanbanCard from "../components/kanban/KanbanCard";
import KanbanColumn from "../components/kanban/KanbanColumn";
import ErrorMessage from "../components/common/ErrorMessage";
import Spinner from "../components/ui/Spinner";
import Modal from "@/components/ui/Modal";

// Modales/steps ya existentes
import ViewCuttingOrderModal from "../features/cuttingOrder/components/ViewCuttingOrderModal";
import Step2Subproducts from "../features/cuttingOrder/components/wizard/Step2Subproducts";

// Helpers del wizard
import { getAvailableStock } from "../features/cuttingOrder/components/wizard/helpers";

// Servicios
import {
  listCuttingOrders,
  patchCuttingOrderWorkflow,
  replaceCuttingOrderItems,
  listSubproductsByParent,
} from "../features/cuttingOrder/services/cuttingOrders";

// 🔴 IMPORTANTE: Hook para sincronización en vivo
import { useCuttingOrderLiveSync } from "@/features/cuttingOrder/hooks/useCuttingOrderLiveSync";

/** Normaliza el estado que venga del backend o legacy a un set estable */
const normalizeStatus = (order) => {
  const raw =
    order?.workflow_status ??
    order?.status ??
    order?.state ??
    "";
  const s = String(raw).toLowerCase().trim();

  if (!s) return "pending"; // default en creación

  if (s === "pending") return "pending";
  if (s === "in_process" || s === "in process") return "in_process";
  if (s === "completed" || s === "complete" || s === "done") return "completed";

  if (s.includes("asignada") || s.includes("pendiente")) return "pending";
  if (s.includes("proceso") || s.includes("proces")) return "in_process";
  if (s.includes("complet")) return "completed";

  return "unknown";
};

const statusTitle = {
  pending: "Pendientes",
  in_process: "En Proceso",
  completed: "Completadas",
};

const toNumber = (v, d = 0) => {
  const n = Number(String(v).replace(",", "."));
  return Number.isFinite(n) ? n : d;
};
const round2 = (n) => Math.round(n * 100) / 100;
const nearlyEq = (a, b, eps = 0.005) => Math.abs(a - b) <= eps;

const PAGE_SIZE = 10;

const Dashboard = () => {
  const { isAuthenticated, loading: authLoading, user } = useAuth();
  const navigate = useNavigate();

  // 🔴 Hook de sincronización en vivo
  useCuttingOrderLiveSync();


  // === Tres “feeds” independientes por columna ===
  const [pending, setPending] = useState([]);
  const [pendingNext, setPendingNext] = useState(null);
  const [loadingPending, setLoadingPending] = useState(true);
  const [loadingMorePending, setLoadingMorePending] = useState(false);

  const [inProcess, setInProcess] = useState([]);
  const [inProcessNext, setInProcessNext] = useState(null);
  const [loadingInProcess, setLoadingInProcess] = useState(true);
  const [loadingMoreInProcess, setLoadingMoreInProcess] = useState(false);

  const [completed, setCompleted] = useState([]);
  const [completedNext, setCompletedNext] = useState(null);
  const [loadingCompleted, setLoadingCompleted] = useState(true);
  const [loadingMoreCompleted, setLoadingMoreCompleted] = useState(false);

  const [errorMsg, setErrorMsg] = useState("");
  const [advancingId, setAdvancingId] = useState(null);

  // Modal: ver detalle
  const [viewOpen, setViewOpen] = useState(false);
  const [viewOrder, setViewOrder] = useState(null);

  // Modal: Step2 con Step2Subproducts
  const [step2Open, setStep2Open] = useState(false);
  const [step2Order, setStep2Order] = useState(null);
  const [loadingSubs, setLoadingSubs] = useState(false);
  const [subproducts, setSubproducts] = useState([]);
  const [selectedItems, setSelectedItems] = useState({}); // { [subId]: "12.5" }
  const [step2Saving, setStep2Saving] = useState(false);

  // ---- loaders por estado ----
  const fetchStatusFirstPage = useCallback(async (status) => {
    const setList = status === "pending" ? setPending : status === "in_process" ? setInProcess : setCompleted;
    const setNext = status === "pending" ? setPendingNext : status === "in_process" ? setInProcessNext : setCompletedNext;
    const setLoading = status === "pending" ? setLoadingPending : status === "in_process" ? setLoadingInProcess : setLoadingCompleted;

    setLoading(true);
    try {
      const res = await listCuttingOrders(
        "/cutting/cutting-orders/",
        { workflow_status: status, page_size: PAGE_SIZE },
        { force: true }
      );
      setList(res?.results || []);
      setNext(res?.next || null);
    } catch (err) {
      setList([]);
      setNext(null);
      setErrorMsg(
        err?.response?.data?.detail || `No se pudieron cargar las órdenes (${status}).`
      );
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchStatusNext = useCallback(async (status) => {
    const getNext = status === "pending" ? pendingNext : status === "in_process" ? inProcessNext : completedNext;
    if (!getNext) return;

    const setList = status === "pending" ? setPending : status === "in_process" ? setInProcess : setCompleted;
    const setNext = status === "pending" ? setPendingNext : status === "in_process" ? setInProcessNext : setCompletedNext;
    const setLoadingMore = status === "pending" ? setLoadingMorePending : status === "in_process" ? setLoadingMoreInProcess : setLoadingMoreCompleted;

    setLoadingMore(true);
    try {
      const res = await listCuttingOrders(getNext, undefined, { force: true });
      setList((prev) => [...prev, ...(res?.results || [])]);
      setNext(res?.next || null);
    } catch (err) {
      setErrorMsg(
        err?.response?.data?.detail || `No se pudieron cargar más órdenes (${status}).`
      );
    } finally {
      setLoadingMore(false);
    }
  }, [pendingNext, inProcessNext, completedNext]);

  const reloadAll = useCallback(() => {
    fetchStatusFirstPage("pending");
    fetchStatusFirstPage("in_process");
    fetchStatusFirstPage("completed");
  }, [fetchStatusFirstPage]);

  // Listener global para actualizaciones que vienen por WebSocket (fallback cuando
  // componentes mantienen estado local y no observan React Query directamente).
  useEffect(() => {
    const handler = (e) => {
      try {
        reloadAll();
      } catch (err) {
        // noop
      }
    };
    window.addEventListener("cuttingOrder:status", handler);
    return () => window.removeEventListener("cuttingOrder:status", handler);
  }, [reloadAll]);

  // También refrescar ante eventos CRUD genéricos
  useEffect(() => {
    const onRealtime = (e) => {
      const msg = e?.detail;
      if (!msg || msg.model !== 'CuttingOrder') return;
      reloadAll();
    };
    window.addEventListener('realtime-crud-event', onRealtime);
    return () => window.removeEventListener('realtime-crud-event', onRealtime);
  }, [reloadAll]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
  navigate("/");
      return;
    }
    reloadAll();
  }, [isAuthenticated, authLoading, navigate, reloadAll]);

  const openViewModal = (order) => {
    setViewOrder(order || null);
    setViewOpen(!!order);
  };
  const closeViewModal = () => {
    setViewOpen(false);
    setViewOrder(null);
  };

  // Determina si requiere Step2 (selección de bobina/rollo) al iniciar
  const willNeedStep2 = (order, nextStatus) =>
    nextStatus === "in_process" &&
    !!order?.operator_can_edit_items &&
    (!Array.isArray(order?.items) || order.items.length === 0);

  // Cargar subproductos para Step2
  const loadSubproducts = async (order) => {
    setSubproducts([]);
    setSelectedItems({});
    const productId = order?.product_id ?? order?.product?.id ?? null;
    if (!productId) {
      throw new Error("La orden no trae product_id. Exponelo en el serializer.");
    }
    const { results } = await listSubproductsByParent(productId, { status: true });
    setSubproducts(Array.isArray(results) ? results : []);
  };

  // Handler para avanzar estado
  const handleAdvance = async (order, nextStatus) => {
    if (!order?.id || !nextStatus) return;

    // Si debe elegir bobina/rollo, abrimos el modal Step2
    if (willNeedStep2(order, nextStatus)) {
      const isStaff = !!user?.is_staff;
      const assigned =
        typeof order?.assigned_to === "string"
          ? order.assigned_to
          : String(order?.assigned_to ?? "");
      const isAssignee = user?.username && String(user.username) === String(assigned);
      if (!isStaff && !isAssignee) {
        setErrorMsg("No tienes permiso para iniciar esta orden.");
        return;
      }

      try {
        setStep2Order(order);
        setStep2Open(true);
        setLoadingSubs(true);
        await loadSubproducts(order);
      } catch (e) {
        console.error(e);
        setErrorMsg(e?.message || "No se pudieron cargar los subproductos.");
        setStep2Open(false);
        setStep2Order(null);
      } finally {
        setLoadingSubs(false);
      }
      return;
    }

    // Flujo normal
    try {
      setAdvancingId(order.id);
      await patchCuttingOrderWorkflow(order.id, nextStatus);
      reloadAll(); // ← refresca las tres columnas
    } catch (err) {
      console.error("Error advancing status:", err);
      const detail = err?.response?.data;
      setErrorMsg(
        (detail && typeof detail === "object"
          ? Object.values(detail).flat().join(", ")
          : detail?.detail) ||
        "No se pudo actualizar el estado de la orden."
      );
    } finally {
      setAdvancingId(null);
    }
  };

  // Helpers de totales en Step2
  const target = toNumber(step2Order?.quantity_to_cut, 0);
  const sumSelected = useCallback((obj) => {
    return Object.values(obj).reduce((acc, raw) => acc + toNumber(raw, 0), 0);
  }, []);

  // Step2: toggle selección
  const onToggle = (id) => {
    setSelectedItems((prev) => {
      const next = { ...prev };
      if (Object.prototype.hasOwnProperty.call(next, id)) {
        delete next[id];
        return next;
      }
      const sp = subproducts.find((s) => Number(s?.id) === Number(id));
      const available = sp ? toNumber(getAvailableStock(sp), 0) : 0;

      const usedByOthers = sumSelected(next);
      const remaining = Math.max(0, target - usedByOthers);

      const initial = round2(Math.min(available, remaining));
      next[id] = String(initial);
      return next;
    });
  };

  // Step2: cambio de cantidad con clamp a disponible y a objetivo total
  const onQuantityChange = (id, raw) => {
    setSelectedItems((prev) => {
      const next = { ...prev };
      const sp = subproducts.find((s) => Number(s?.id) === Number(id));
      const available = sp ? toNumber(getAvailableStock(sp), 0) : 0;

      let req = toNumber(raw, NaN);
      if (!Number.isFinite(req)) {
        next[id] = "0";
        return next;
      }
      if (req < 0) req = 0;

      const othersSum = Object.entries(prev).reduce((acc, [k, v]) => {
        if (String(k) === String(id)) return acc;
        return acc + toNumber(v, 0);
      }, 0);

      const maxByTarget = Math.max(0, target - othersSum);
      const clamped = round2(Math.min(req, available, maxByTarget));
      next[id] = String(clamped);
      return next;
    });
  };

  // Step2: confirmar -> guardar items y pasar a in_process
  const confirmStep2 = async () => {
    if (!step2Order) return;
    const items = Object.entries(selectedItems)
      .map(([subId, raw]) => ({
        subproduct: Number(subId),
        cutting_quantity: toNumber(raw, 0),
      }))
      .filter((it) => it.subproduct > 0 && it.cutting_quantity > 0);

    if (items.length === 0) return;

    try {
      setStep2Saving(true);
      await replaceCuttingOrderItems(step2Order.id, items);
      await patchCuttingOrderWorkflow(step2Order.id, "in_process");
      setStep2Open(false);
      setStep2Order(null);
      setSelectedItems({});
      reloadAll();
    } catch (err) {
      console.error(err);
      setErrorMsg(
        err?.response?.data?.detail ||
        (typeof err?.response?.data === "object"
          ? Object.values(err.response.data).flat().join(", ")
          : "No se pudo iniciar la orden con los ítems seleccionados.")
      );
    } finally {
      setStep2Saving(false);
    }
  };

  const renderCards = (arr, keyPrefix) =>
    (arr || [])
      .filter(Boolean)
      .map((order) => (
        <KanbanCard
          key={order?.id ?? `${keyPrefix}-${Math.random().toString(36).slice(2)}`}
          order={order}
          currentUser={user}
          onAdvance={handleAdvance}
          advancing={advancingId === order?.id}
          onClick={() => openViewModal(order)}
        />
      ));

  // Totales seleccionados en Step2 (UI)
  const totalSelected = useMemo(() => {
    return Object.values(selectedItems).reduce(
      (acc, raw) => acc + toNumber(raw, 0),
      0
    );
  }, [selectedItems]);

  // Confirmación estricta: suma == objetivo (con tolerancia)
  const canConfirm =
    !step2Saving &&
    target > 0 &&
    nearlyEq(totalSelected, target);

  // Hay algún loading inicial?
  const anyInitialLoading = loadingPending || loadingInProcess || loadingCompleted;

  return (
    <Layout isLoading={false}>
      <div className="p-10 mt-4">
        <h1 className="text-2xl font-bold text-start mb-6 text-text.primary">
          Órdenes de Corte
        </h1>

        {errorMsg ? (
          <div className="mb-4">
            <ErrorMessage message={errorMsg} onClose={() => setErrorMsg("")} />
          </div>
        ) : null}

        {authLoading || anyInitialLoading ? (
          <div className="flex justify-center items-center h-64">
            <Spinner size="8" color="text-primary-500" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Pendiente */}
            <KanbanColumn
              title={statusTitle.pending}
              count={pending.length}
              color="warning"
              onLoadMore={() => fetchStatusNext("pending")}
              hasNext={!!pendingNext}
              isLoadingMore={loadingMorePending}
            >
              {pending.length > 0 ? (
                renderCards(pending, "p")
              ) : (
                <p className="text-text.secondary/70 text-sm">
                  No hay órdenes pendientes.
                </p>
              )}
            </KanbanColumn>

            {/* En Proceso */}
            <KanbanColumn
              title={statusTitle.in_process}
              count={inProcess.length}
              color="success"
              onLoadMore={() => fetchStatusNext("in_process")}
              hasNext={!!inProcessNext}
              isLoadingMore={loadingMoreInProcess}
            >
              {inProcess.length > 0 ? (
                renderCards(inProcess, "ip")
              ) : (
                <p className="text-text.secondary/70 text-sm">
                  No hay órdenes en proceso.
                </p>
              )}
            </KanbanColumn>

            {/* Completada */}
            <KanbanColumn
              title={statusTitle.completed}
              count={completed.length}
              color="primary"
              onLoadMore={() => fetchStatusNext("completed")}
              hasNext={!!completedNext}
              isLoadingMore={loadingMoreCompleted}
            >
              {completed.length > 0 ? (
                renderCards(completed, "c")
              ) : (
                <p className="text-text.secondary/70 text-sm">
                  No hay órdenes completadas.
                </p>
              )}
            </KanbanColumn>
          </div>
        )}
      </div>

      {/* Modal: Ver orden */}
      {viewOpen && viewOrder && (
        <ViewCuttingOrderModal
          order={viewOrder}
          isOpen={viewOpen}
          onClose={closeViewModal}
        />
      )}

      {/* Modal: Step2 con Step2Subproducts */}
      {step2Open && step2Order && (
        <Modal
          isOpen={step2Open}
          onClose={() => {
            setStep2Open(false);
            setStep2Order(null);
            setSelectedItems({});
          }}
          title={
            step2Order
              ? `Seleccionar bobina/rollo — Pedido N°${step2Order.order_number ?? step2Order.id}`
              : "Seleccionar bobina/rollo"
          }
          position="center"
          maxWidth="max-w-5xl"
        >
          <div className="space-y-4">
            <div className="text-sm flex flex-wrap gap-4">
              <span>
                <span className="font-semibold">Cliente:</span> {step2Order.customer ?? "—"}
              </span>
              <span>
                <span className="font-semibold">Producto:</span> {step2Order.product ?? "—"}
              </span>
              <span>
                <span className="font-semibold">Cantidad pedida:</span>{" "}
                {step2Order.quantity_to_cut ?? "—"} mts
              </span>
            </div>

            {!step2Order?.product_id ? (
              <div className="p-3 rounded border bg-amber-50 text-amber-800 text-sm">
                La orden no trae <code>product_id</code>. Exponelo en el serializer para poder
                cargar los subproductos del producto.
              </div>
            ) : null}

            <Step2Subproducts
              loadingSubs={loadingSubs}
              subproducts={subproducts}
              selectedItems={selectedItems}
              onToggle={onToggle}
              onQuantityChange={onQuantityChange}
            />

            <div className="flex items-center justify-between pt-2">
              <div className="text-sm">
                Seleccionado: <strong>{round2(totalSelected).toFixed(2)}</strong> mts
                {target > 0 ? (
                  <span className="ml-2">
                    (objetivo: <strong>{round2(target).toFixed(2)}</strong> mts)
                  </span>
                ) : null}
              </div>

              <div className="flex gap-2">
                <button
                  className="bg-neutral-500 text-white px-4 py-2 rounded hover:bg-neutral-600"
                  onClick={() => {
                    setStep2Open(false);
                    setStep2Order(null);
                    setSelectedItems({});
                  }}
                  disabled={step2Saving}
                >
                  Cancelar
                </button>
                <button
                  className="px-4 py-2 bg-primary-500 rounded text-white hover:bg-primary-600 transition"
                  onClick={confirmStep2}
                  disabled={!canConfirm}
                  title="Guardar ítems y pasar a En Proceso"
                >
                  {step2Saving ? "Guardando..." : "Confirmar y Iniciar"}
                </button>
              </div>
            </div>

            {!canConfirm && target > 0 && (
              <div className="text-[12px] text-amber-800 bg-amber-50 border border-amber-200 rounded p-2">
                Para continuar, ajustá las cantidades hasta sumar exactamente <strong>{round2(target).toFixed(2)}</strong> mts.
              </div>
            )}
          </div>
        </Modal>
      )}
    </Layout>
  );
};

export default Dashboard;