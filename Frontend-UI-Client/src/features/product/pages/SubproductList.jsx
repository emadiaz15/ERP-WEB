import React, { useState, useCallback, useMemo, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useParams, useNavigate, useLocation } from "react-router-dom";

import Layout from "@/pages/Layout";
import Toolbar from "@/components/common/Toolbar";
import SuccessMessage from "@/components/common/SuccessMessage";
import ErrorMessage from "@/components/common/ErrorMessage";
import Pagination from "@/components/ui/Pagination";

import SubproductModals from "../components/SubproductModals";
import SubproductCard from "../components/SubproductCard";
import SubproductFilters from "../components/SubproductFilter";

import {
  useListSubproducts,
  useCreateSubproduct,
  useUpdateSubproduct,
  useDeleteSubproduct,
} from "@/features/product/hooks/useSubproductHooks";

import CreateCuttingOrderWizard from "@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard";

const toNumber = (v) => {
  if (typeof v === "number") return v;
  if (typeof v === "string" && v.trim() !== "" && !Number.isNaN(parseFloat(v))) {
    return parseFloat(v);
  }
  return 0;
};

const STORAGE_KEY = "productList.lastUrl";

export default function SubproductList() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const pid = Number(productId);
  const queryClient = useQueryClient();

  const [filters, setFilters] = useState({ status: "true" });
  const [pageUrl, setPageUrl] = useState(null);

  const [modalState, setModalState] = useState({ type: null, subproductData: null });
  const openModal = useCallback((type, data = null) => {
    setModalState({ type, subproductData: data });
  }, []);
  const closeModal = useCallback(() => {
    setModalState({ type: null, subproductData: null });
  }, []);

  const isCutWizardOpen = modalState.type === "createOrder";
  const preselectedSubpId = modalState.subproductData?.id;

  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [deleteError, setDeleteError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isCreating, setIsCreating] = useState(false); // 🔒 evita doble POST

  const handleSave = useCallback((msg) => {
    setPageUrl(null);
    setSuccessMessage(msg);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  }, []);

  const {
    subproducts,
    nextPageUrl,
    previousPageUrl,
    isLoading,
    isError,
    error: fetchError,
    refetch,
  } = useListSubproducts(pid, pageUrl, filters);

  const visibleSubproducts = useMemo(() => {
    if (!Array.isArray(subproducts)) return [];
    if (filters.status === "true") {
      return subproducts.filter((sp) => {
        const available =
          toNumber(sp.current_stock) ||
          toNumber(sp.current_stock_quantity) ||
          toNumber(sp.initial_stock_quantity);
        return sp.status === true && available > 0;
      });
    }
    return subproducts;
  }, [subproducts, filters.status]);

  const createMutation = useCreateSubproduct(pid);
  const updateMutation = useUpdateSubproduct(pid);
  const deleteMutation = useDeleteSubproduct(pid);

  // Helpers de patch local para subproductos (todas las listas del producto)
  const patchInsertSubproduct = useCallback((subp) => {
    if (!subp) return;
    queryClient.setQueriesData({
      predicate: (q) => Array.isArray(q.queryKey)
        && q.queryKey[0] === 'products'
        && q.queryKey[1] === pid
        && q.queryKey.includes('subproducts')
        && q.queryKey.includes('list')
    }, (old) => {
      if (!old?.results && !old?.pages) return old;
      // Soporta tanto useQuery de página simple ({results}) como infiniteQuery ({pages})
      if (Array.isArray(old.pages)) {
        const pages = old.pages.slice();
        const first = pages[0] || {};
        const results = Array.isArray(first.results) ? first.results : [];
        pages[0] = { ...first, results: [subp, ...results], count: typeof first.count === 'number' ? first.count + 1 : first.count };
        return { ...old, pages };
      }
      if (Array.isArray(old.results)) {
        return { ...old, results: [subp, ...old.results], count: typeof old.count === 'number' ? old.count + 1 : old.count };
      }
      return old;
    });
  }, [queryClient, pid]);

  const patchReplaceSubproduct = useCallback((subp) => {
    if (!subp) return;
    queryClient.setQueriesData({
      predicate: (q) => Array.isArray(q.queryKey)
        && q.queryKey[0] === 'products'
        && q.queryKey[1] === pid
        && q.queryKey.includes('subproducts')
        && q.queryKey.includes('list')
    }, (old) => {
      if (!old?.results && !old?.pages) return old;
      if (Array.isArray(old.pages)) {
        let changed = false;
        const pages = old.pages.map((p) => {
          const results = Array.isArray(p?.results)
            ? p.results.map((r) => (r?.id === subp.id ? (changed = true, { ...r, ...subp }) : r))
            : p?.results;
          return { ...p, results };
        });
        return changed ? { ...old, pages } : old;
      }
      if (Array.isArray(old.results)) {
        let changed = false;
        const results = old.results.map((r) => (r?.id === subp.id ? (changed = true, { ...r, ...subp }) : r));
        return changed ? { ...old, results } : old;
      }
      return old;
    });
  }, [queryClient, pid]);

  const patchRemoveSubproduct = useCallback((id) => {
    if (id == null) return;
    queryClient.setQueriesData({
      predicate: (q) => Array.isArray(q.queryKey)
        && q.queryKey[0] === 'products'
        && q.queryKey[1] === pid
        && q.queryKey.includes('subproducts')
        && q.queryKey.includes('list')
    }, (old) => {
      if (!old?.results && !old?.pages) return old;
      if (Array.isArray(old.pages)) {
        let changed = false;
        const pages = old.pages.map((p) => {
          const before = Array.isArray(p?.results) ? p.results.length : 0;
          const results = Array.isArray(p?.results) ? p.results.filter((r) => r?.id !== id) : p?.results;
          if (Array.isArray(p?.results) && results.length !== before) changed = true;
          return { ...p, results, count: typeof p.count === 'number' ? Math.max(0, p.count - (before - (results?.length ?? 0))) : p.count };
        });
        return changed ? { ...old, pages } : old;
      }
      if (Array.isArray(old.results)) {
        const before = old.results.length;
        const results = old.results.filter((r) => r?.id !== id);
        if (results.length === before) return old;
        return { ...old, results, count: typeof old.count === 'number' ? Math.max(0, old.count - (before - results.length)) : old.count };
      }
      return old;
    });
  }, [queryClient, pid]);

  const handleCreate = useCallback(
    async (formData) => {
      if (isCreating || createMutation.isPending) return null; // evita doble submit
      setIsCreating(true);
      try {
        if (formData && typeof formData.has === "function" && !formData.has("status")) {
          formData.append("status", "true");
        }
        const created = await createMutation.mutateAsync(formData);
        // Patch local inmediato
        patchInsertSubproduct(created);
        handleSave("Subproducto creado correctamente");
        closeModal();
        // Refetch con pequeño retraso
        setTimeout(() => refetch(), 150);
        return created;
      } catch (err) {
        console.error("Error creando subproducto:", err);
        return null;
      } finally {
        setIsCreating(false);
      }
    },
    [isCreating, createMutation, handleSave, closeModal, refetch, patchInsertSubproduct]
  );

  const handleUpdate = useCallback(
    async ({ id, formData }) => {
      try {
        const updated = await updateMutation.mutateAsync({ subproductId: id, formData });
        // Patch local inmediato de la tarjeta/lista
        patchReplaceSubproduct(updated);
        handleSave("Subproducto actualizado correctamente");
        closeModal();
        // Refetch con pequeño retraso
        setTimeout(() => refetch(), 150);
      } catch (err) {
        console.error("Error actualizando subproducto:", err);
      }
    },
    [updateMutation, handleSave, closeModal, refetch, patchReplaceSubproduct]
  );

  const handleDelete = useCallback(
    async ({ id }) => {
      setIsDeleting(true);
      setDeleteError(null);
      try {
        await deleteMutation.mutateAsync(id);
        // Patch local: remover de listas visibles
        patchRemoveSubproduct(id);
        handleSave("Subproducto eliminado correctamente");
        closeModal();
        setTimeout(() => refetch(), 150);
      } catch (err) {
        setDeleteError(err.message || "Error al eliminar subproducto");
      } finally {
        setIsDeleting(false);
      }
    },
    [deleteMutation, handleSave, closeModal, refetch, patchRemoveSubproduct]
  );

  const handleCreateOrder = useCallback(() => {
    handleSave("Orden de corte creada correctamente");
    closeModal();
  }, [handleSave, closeModal]);

  const onFilterChange = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    setPageUrl(null);
  }, []);

  // ⬇️ Guardar la URL de origen cuando venga por state.from (o por ?from=)
  useEffect(() => {
    const stateFrom = location.state?.from;
    const qsFrom = new URLSearchParams(location.search).get("from");
    const asUrl = (val) =>
      typeof val === "string" ? val : val ? `${val.pathname}${val.search ?? ""}` : null;

    const fromUrl = asUrl(stateFrom) || (qsFrom ? decodeURIComponent(qsFrom) : null);
    if (fromUrl) {
      try {
        sessionStorage.setItem(STORAGE_KEY, fromUrl);
      } catch {
        /* ignore */
      }
    }
  }, [location.state, location.search]);

  // ⬇️ Back inteligente: state -> ?from -> sessionStorage -> history -> fallback
  const handleBack = useCallback(() => {
    const asUrl = (val) =>
      typeof val === "string" ? val : val ? `${val.pathname}${val.search ?? ""}` : null;

    const stateFrom = asUrl(location.state?.from);
    const qsFromRaw = new URLSearchParams(location.search).get("from");
    const qsFrom = qsFromRaw ? decodeURIComponent(qsFromRaw) : null;

    let storedFrom = null;
    try {
      storedFrom = sessionStorage.getItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }

    const target = stateFrom || qsFrom || storedFrom;

    if (target) {
      navigate(target, { replace: true });
      return;
    }

    if (window.history.length > 1) {
      navigate(-1);
      return;
    }

    // Fallback razonable: detalle del producto padre si existe, o lista
    navigate(`/products/${pid}`); // o "/product-list"
  }, [location.state, location.search, navigate, pid]);

  // Refrescar en eventos realtime (crear/actualizar/eliminar subproducto) con dedupe
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
      if (!msg || msg.model !== 'Subproduct') return;
      const id = msg?.payload?.id ?? 'any';
      const k = `Subproduct:${msg.event}:${id}:product:${pid}`;
      if (shouldDedupe(k)) return;
      setTimeout(() => refetch(), 150);
    }
    window.addEventListener('realtime-crud-event', onRealtime);
    return () => window.removeEventListener('realtime-crud-event', onRealtime);
  }, [refetch, pid]);

  return (
    <Layout isLoading={isLoading}>
      {showSuccess && (
        <div className="fixed top-20 right-5 z-50">
          <SuccessMessage message={successMessage} onClose={() => setShowSuccess(false)} />
        </div>
      )}

      <div className="p-3 md:p-4 lg:p-6 mt-6">
        <Toolbar
          title="Lista de Subproductos"
          onBackClick={handleBack}
          buttonText="Crear Subproducto"
          onButtonClick={() => openModal("create")}
        />

        <SubproductFilters filters={filters} onChange={onFilterChange} />

        {isError && <ErrorMessage message={fetchError?.message} onClose={() => { }} />}

        {visibleSubproducts.length === 0 && !isLoading ? (
          <div className="text-center py-10 bg-white rounded-lg shadow mt-4">
            <p className="text-gray-500">No existen subproductos registrados para este producto.</p>
          </div>
        ) : (
          <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-5 gap-4">
            {visibleSubproducts.map((sp) => (
              <SubproductCard
                key={sp.id}
                subproduct={sp}
                onAddToOrder={() => openModal("createOrder", sp)}
                onViewDetails={() => openModal("view", sp)}
                onViewStock={() => openModal("viewHistory", sp)}
                onEdit={() => openModal("edit", sp)}
                onDelete={() => openModal("deleteConfirm", sp)}
              />
            ))}
          </div>
        )}

        <Pagination
          onNext={nextPageUrl ? () => setPageUrl(nextPageUrl) : undefined}
          onPrevious={previousPageUrl ? () => setPageUrl(previousPageUrl) : undefined}
          hasNext={Boolean(nextPageUrl)}
          hasPrevious={Boolean(previousPageUrl)}
        />
      </div>

      <SubproductModals
        modalState={modalState}
        closeModal={closeModal}
        onCreateSubproduct={handleCreate}
        onUpdateSubproduct={handleUpdate}
        onDeleteSubproduct={handleDelete}
        onCreateOrder={handleCreateOrder}
        isDeleting={isDeleting}
        deleteError={deleteError}
        clearDeleteError={() => setDeleteError(null)}
        parentProduct={{ id: pid }}
      />

      <CreateCuttingOrderWizard
        isOpen={isCutWizardOpen}
        onClose={closeModal}
        onSave={(created) =>
          handleSave(
            created?.id
              ? `Orden #${created.id} creada correctamente`
              : "Orden creada correctamente"
          )
        }
        productId={pid}
        preselectedSubproducts={preselectedSubpId ? [preselectedSubpId] : []}
        lockToPreselected={false}
        hideOperatorToggle={true}
        allowEmptyItemsDefault={false}
      />
    </Layout>
  );
}
