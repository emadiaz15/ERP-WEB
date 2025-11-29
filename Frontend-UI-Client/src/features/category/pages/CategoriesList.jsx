// src/features/category/pages/CategoryList.jsx
import React, { useState, useMemo, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import Toolbar from "@/components/common/Toolbar";
import SuccessMessage from "@/components/common/SuccessMessage";
import ErrorMessage from "@/components/common/ErrorMessage";
import Filter from "@/components/ui/Filter";
import Layout from "@/pages/Layout";

import CategoryTable from "../components/CategoryTable";
import CategoryModals from "../components/CategoryModals";
import {
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from "../hooks/useCategoryMutations";

import useEntityModal from "@/hooks/useEntityModal";
import useSuccess from "@/hooks/useSuccess";

// ✅ Hook genérico raíz (DRF PageNumberPagination)
import { useInfinitePageQuery } from "@/hooks/useInfinitePageQuery";

export default function CategoryList() {
  const navigate = useNavigate();

  // Filtros controlados (sin page; infinite se encarga)
  const [filters, setFilters] = useState({ name: "" });

  // Mutaciones
  const createMut = useCreateCategory();
  const updateMut = useUpdateCategory();
  const deleteMut = useDeleteCategory();

  // 🌀 Listado con infinite scroll (endpoint bajo /inventory)
  const {
    items: categories,
    isLoading: loading,
    isError,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    invalidate,
  } = useInfinitePageQuery({
    key: ["categories", filters],
    url: "/inventory/categories/",
    params: filters,
    pageSize: 10,
    enabled: true,
  });

  // Éxitos/errores de acciones
  const {
    successMessage,
    error: actionError,
    handleSuccess,
    handleError,
    clear: clearStatus,
  } = useSuccess();

  // 🔐 Gestor de modales (debe declararse ANTES de callbacks que usen closeAllModals)
  const {
    showCreateModal,
    showEditModal,
    showViewModal,
    showConfirmDialog,
    selectedEntity: selectedCategory,
    entityToDelete,
    openCreateModal,
    openEditModal,
    openViewModal,
    openConfirmDialog,
    handleDelete: handleDeleteModal,
    closeAllModals,
  } = useEntityModal({
    onDelete: async (cat) => {
      try {
        await deleteMut.mutateAsync(cat.id);
        handleSuccess(`Categoría "${cat.name}" eliminada.`);
        setTimeout(() => invalidate(), 150);
      } catch (err) {
        handleError(err);
      }
    },
  });

  // 📌 Callbacks de acciones (todas las deps incluidas para evitar warnings)
  const handleCreate = useCallback(
    async (data) => {
      clearStatus();
      try {
        const created = await createMut.mutateAsync(data);
        handleSuccess(`Categoría "${created.name}" creada.`);
  setTimeout(() => invalidate(), 150);
        closeAllModals();
      } catch (err) {
        handleError(err);
      }
    },
    [
      createMut,
      handleSuccess,
      handleError,
      invalidate,
      clearStatus,
      closeAllModals,
    ]
  );

  const handleUpdate = useCallback(
    async ({ id, payload }) => {
      clearStatus();
      try {
        const updated = await updateMut.mutateAsync({ id, payload });
        handleSuccess(`Categoría "${updated.name}" actualizada.`);
  setTimeout(() => invalidate(), 150);
        closeAllModals();
      } catch (err) {
        handleError(err);
      }
    },
    [
      updateMut,
      handleSuccess,
      handleError,
      invalidate,
      clearStatus,
      closeAllModals,
    ]
  );

  const filterColumns = useMemo(
    () => [{ key: "name", label: "Nombre Categoría", filterType: "text" }],
    []
  );

  return (
    <>
      <Layout isLoading={loading}>
        {successMessage && (
          <div className="fixed top-20 right-5 z-[10000]">
            <SuccessMessage message={successMessage} onClose={clearStatus} />
          </div>
        )}

        {/* 👇 Misma estructura y espaciados que Users */}
        <div className="p-3 md:p-4 lg:p-6 mt-6">
          <Toolbar
            title="Lista de Categorías"
            onBackClick={() => navigate("/product-list")}
            onButtonClick={openCreateModal}
            buttonText="Nueva Categoría"
          />

          <Filter
            columns={filterColumns}
            initialFilters={filters}
            onFilterChange={(newF) =>
              setFilters((f) => ({ ...f, ...newF })) // sin page
            }
          />

          {isError && !loading && (
            <div className="my-4">
              <ErrorMessage
                message={error?.message || "Error al cargar categorías."}
              />
            </div>
          )}

          {!loading && categories.length > 0 && (
            <CategoryTable
              categories={categories}
              openViewModal={openViewModal}
              openEditModal={openEditModal}
              openDeleteConfirmModal={openConfirmDialog}
              // 👇 Props para infinite scroll dentro de la tabla
              onLoadMore={fetchNextPage}
              hasNextPage={!!hasNextPage}
              isFetchingNextPage={isFetchingNextPage}
            />
          )}

          {!loading && categories.length === 0 && (
            <div className="text-center py-10 px-4 mt-4 bg-white rounded-lg shadow">
              <p className="text-gray-500">
                No se encontraron rubros o categorías.
              </p>
            </div>
          )}
        </div>
      </Layout>

      <CategoryModals
        category={selectedCategory}
        categoryToDelete={entityToDelete}
        showCreateModal={showCreateModal}
        showEditModal={showEditModal}
        showViewModal={showViewModal}
        showConfirmDialog={showConfirmDialog}
        closeAllModals={closeAllModals}
        onCreate={handleCreate}
        onUpdateCategory={handleUpdate}
        onDelete={handleDeleteModal}
        isProcessing={
          createMut.isLoading || updateMut.isLoading || deleteMut.isLoading
        }
        error={actionError}
      />
    </>
  );
}
