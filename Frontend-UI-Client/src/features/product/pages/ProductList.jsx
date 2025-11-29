// src/features/product/pages/ProductsList.jsx
import React, { useState, useCallback, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useNavigate, useLocation, useSearchParams } from "react-router-dom";

import Layout from "@/pages/Layout";
import Toolbar from "@/components/common/Toolbar";
import { useProductsWithFiles } from "@/features/metrics/hooks/useProductsWithFiles";
import SuccessMessage from "@/components/common/SuccessMessage";
import ErrorMessage from "@/components/common/ErrorMessage";

import ProductFilter from "@/features/product/components/ProductFilter";
import ProductModals from "@/features/product/components/ProductModals";
import ProductTable from "@/features/product/components/ProductTable";

import { useAuth } from "@/context/AuthProvider";
import { useInfinitePageQuery } from "@/hooks/useInfinitePageQuery";
import { djangoApi } from "@/api/clients";

const ProductsList = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const isStaff = !!user?.is_staff;

  // ⬇️ Filtros del querystring al montar
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState(() => ({
    name: searchParams.get("name") ?? "",
    code: searchParams.get("code") ?? "",
    category: searchParams.get("category") ?? "",
  }));

  // ⬇️ Mantener filtros en la URL (para que se conserven al volver)
  useEffect(() => {
    const next = new URLSearchParams();
    if (filters.name) next.set("name", filters.name);
    if (filters.code) next.set("code", filters.code);
    if (filters.category) next.set("category", filters.category);
    // Evita re-render innecesario si ya coincide
    const same =
      next.toString() === searchParams.toString();
    if (!same) setSearchParams(next, { replace: true });
  }, [filters, setSearchParams, searchParams]);

  // 🌀 Listado con infinite scroll (endpoint bajo /inventory)
  const {
    items: products,
    isLoading,
    isError,
    error: fetchError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    invalidate,
  } = useInfinitePageQuery({
    key: ["products", filters],
    url: "/inventory/products/",
    params: filters,
    pageSize: 10,
    enabled: true,
  });

  // 📊 KPI: % productos con archivos
  const { data: kpi, isLoading: isLoadingKpi } = useProductsWithFiles();
  const kpiText = isLoadingKpi
    ? "cargando…"
    : `${Number(kpi?.percentage ?? 0).toFixed(2)}% (${kpi?.with_files ?? 0}/${kpi?.total ?? 0}) con archivos`;

  const [modalState, setModalState] = useState({ type: null, productData: null });
  const openModal = useCallback((type, data = null) => {
    setModalState({ type, productData: data });
  }, []);
  const closeModal = useCallback(() => {
    setModalState({ type: null, productData: null });
  }, []);

  const [successMessage, setSuccessMessage] = useState("");
  const [showSuccess, setShowSuccess] = useState(false);
  const [deleteError, setDeleteError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSaveToast = useCallback((msg) => {
    setSuccessMessage(msg);
    setShowSuccess(true);
    setTimeout(() => setShowSuccess(false), 3000);
  }, []);

  const handleFilterChange = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
    // react-query rehace el query y resetea páginas
  }, []);

  // --- API helpers locales (PUT/DELETE) ---
  const updateProductApi = useCallback(async (id, payload) => {
    const { data } = await djangoApi.put(`/inventory/products/${id}/`, payload);
    return data;
  }, []);

  const deleteProductApi = useCallback(async (id) => {
    await djangoApi.delete(`/inventory/products/${id}/`);
  }, []);



  const handleUpdate = useCallback(
    async (id, formData) => {
      try {
        const updated = await updateProductApi(id, formData);

        // 1) Parche local inmediato en listas de productos (todas las páginas activas)
        queryClient.setQueriesData(
          { predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === "products" },
          (old) => {
            if (!old) return old;
            // Soporte tanto para infiniteQuery ({pages}) como para lista simple ({results})
            if (Array.isArray(old.pages)) {
              let touched = false;
              const pages = old.pages.map((p) => {
                if (!Array.isArray(p?.results)) return p;
                const results = p.results.map((r) => (r?.id === updated?.id ? { ...r, ...updated } : r));
                if (results !== p.results) touched = true;
                return { ...p, results };
              });
              return touched ? { ...old, pages } : old;
            }
            if (Array.isArray(old.results)) {
              const results = old.results.map((r) => (r?.id === updated?.id ? { ...r, ...updated } : r));
              return { ...old, results };
            }
            // Detalle plano
            if (typeof old === "object" && old?.id === updated?.id) return { ...old, ...updated };
            return old;
          }
        );

        // 2) Upsert de caches de detalle conocidos
        queryClient.setQueriesData(
          {
            predicate: (q) => {
              const k = q.queryKey;
              return (
                Array.isArray(k) &&
                k[0] === "products" &&
                ((k[1] === "detail" && k[2] === id) || (k.length === 2 && k[1] === id))
              );
            },
          },
          (old) => (old ? { ...old, ...updated } : updated)
        );

        // 3) Invalidación con pequeño retraso para evitar sobrescribir con respuestas viejas
        setTimeout(() => {
          queryClient.invalidateQueries({
            predicate: (q) => {
              const k = q.queryKey;
              if (!Array.isArray(k)) return false;
              if (k[0] !== 'products') return false;
              // Evita refrescar claves de archivos ['products','files',id]
              if (k[1] === 'files') return false;
              return true;
            },
            refetchType: 'active',
          });
        }, 150);

        handleSaveToast("¡Producto actualizado con éxito!");
        closeModal();
      } catch (err) {
        console.error("Error actualizando producto:", err);
      }
    },
    [updateProductApi, queryClient, handleSaveToast, closeModal]
  );
  const handleDelete = useCallback(
    async (id) => {
      setIsDeleting(true);
      setDeleteError(null);
      try {
        await deleteProductApi(id);
        // Invalidación filtrada (excluye ['products','files',id]) con pequeño retraso
        setTimeout(() => {
          queryClient.invalidateQueries({
            predicate: (q) => {
              const k = q.queryKey;
              if (!Array.isArray(k)) return false;
              if (k[0] !== 'products') return false;
              if (k[1] === 'files') return false;
              return true;
            },
            refetchType: 'active',
          });
        }, 150);
        handleSaveToast("¡Producto eliminado con éxito!");
        closeModal();
      } catch (err) {
        setDeleteError(err?.message || "Error al eliminar producto.");
      } finally {
        setIsDeleting(false);
      }
    },
    [deleteProductApi, queryClient, handleSaveToast, closeModal]
  );

  const handleViewStockHistory = (product) => {
    if (product?.id) {
      navigate(`/products/${product.id}/stock-history`, {
        state: { from: `${location.pathname}${location.search}` },
      });
    }
  };

  // Realtime refresh gestionado globalmente en useRealtimeSync para evitar duplicar invalidaciones

  return (
    <>
      <Layout isLoading={isLoading}>
        {showSuccess && (
          <div className="fixed top-20 right-5 z-[10000]">
            <SuccessMessage message={successMessage} onClose={() => setShowSuccess(false)} />
          </div>
        )}

        <div className="p-3 md:p-4 lg:p-6 mt-6">
          <Toolbar
            title="Lista de Productos"
            titleRight={kpiText}
            buttonText={isStaff ? "Crear Producto" : undefined}
            onButtonClick={isStaff ? () => openModal("create") : undefined}
            configItems={[
              { label: "Categorías - Rubros", onClick: () => navigate("/categories"), adminOnly: true },
            ]}
          />

          <ProductFilter filters={filters} onFilterChange={handleFilterChange} />

          {isError && !isLoading && (
            <div className="my-4">
              <ErrorMessage message={fetchError?.message || "Error al cargar productos."} />
            </div>
          )}

          {products.length > 0 && !isLoading && (
            <ProductTable
              products={products}
              onView={(p) => openModal("view", p)}
              onEdit={(p) => openModal("edit", p)}
              onDelete={(p) => openModal("deleteConfirm", p)}
              onShowSubproducts={(p) =>
                navigate(`/products/${p.id}/subproducts`, {
                  state: { from: `${location.pathname}${location.search}` },
                })
              }
              onViewStockHistory={handleViewStockHistory}
              onLoadMore={fetchNextPage}
              hasNextPage={!!hasNextPage}
              isFetchingNextPage={isFetchingNextPage}
            />
          )}

          {!isLoading && products.length === 0 && (
            <div className="text-center py-10 px-4 mt-4 bg-white rounded-lg shadow">
              <p className="text-gray-500">No se encontraron productos.</p>
            </div>
          )}
        </div>
      </Layout>

      <ProductModals
        modalState={modalState}
        closeModal={closeModal}
        onUpdateProduct={handleUpdate}
        handleSave={handleSaveToast}
        onDeleteProduct={handleDelete}
        isDeleting={isDeleting}
        deleteError={deleteError}
        clearDeleteError={() => setDeleteError(null)}
      />
    </>
  );
};

export default ProductsList;
