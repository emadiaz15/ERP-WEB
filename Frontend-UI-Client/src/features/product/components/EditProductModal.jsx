// src/features/product/components/EditProductModal.jsx
import React from "react";
import PropTypes from "prop-types";
import Modal from "@/components/ui/Modal";
import FormInput from "@/components/ui/form/FormInput";
import FormStockInput from "@/features/product/components/FormStockInput";
import ErrorMessage from "@/components/common/ErrorMessage";
import SuccessMessage from "@/components/common/SuccessMessage";
import DeleteMessage from "@/components/common/DeleteMessage";
import ProductCarouselOverlay from "@/features/product/components/ProductCarouselOverlay";
import { useUploadProductFiles, useDeleteProductFile } from "@/features/product/hooks/useProductFileHooks";
import { usePrefetchedData } from "@/context/DataPrefetchContext";
import { useEditProductForm } from "@/features/product/hooks/useEditProductForm";
import CategoryPicker from "@/features/product/components/CategoryPicker";
import { useProducts } from "@/features/product/hooks/useProductHooks";

export default function EditProductModal({ product, isOpen, onClose, onSave, children, loading: outerLoading = false }) {
  const { categories } = usePrefetchedData(); // <-- sólo categorías; sin types
  const { products, updateProduct } = useProducts({ page_size: 1000 });
  const uploadMut = useUploadProductFiles(product.id);
  const deleteMut = useDeleteProductFile(product.id);

  // form hook
  const {
    formData,
    previewFiles,
    error,
    loading,
    showSuccess,
    isDeleting,
    deleteError,
    isDeleteOpen,
    fileToDelete,
    openDeleteRequest,
    closeDeleteRequest,
    handleChange,
    handleStockChange,
    handleFileChange,
    removeFile,
    handleSubmit,
    confirmDelete,
    selectCategory,
  } = useEditProductForm({
    product,
    categories,
  products,
  updateProduct,
    uploadMut,
    onSave,
    onClose,
    deleteMut,
  });

  // inyectar trigger de delete en el carrusel
  const childrenWithProps = React.Children.map(children, (child) =>
    React.isValidElement(child) && child.type === ProductCarouselOverlay
      ? React.cloneElement(child, {
        onDeleteRequest: openDeleteRequest,
        editable: true,
      })
      : child
  );

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Editar Producto" maxWidth="max-w-6xl" loading={outerLoading}>
      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1 p-4 bg-background-100 rounded max-h-[80vh] overflow-y-auto">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <ErrorMessage message={error} onClose={() => { /* manejado en el hook */ }} />}
            {showSuccess && (
              <div className="fixed top-20 right-5 z-[10000]">
                <SuccessMessage message="Producto actualizado correctamente" />
              </div>
            )}

            {/* Categoría */}
            <div>
              <label htmlFor="category-input" className="block text-sm font-medium text-text-secondary">
                Categoría *
              </label>
              <CategoryPicker
                id="category-input"
                name="categoryInput"
                value={formData.categoryInput}
                onChange={handleChange}
                selectCategory={selectCategory}
                selectedId={formData.category}
                isOpen={isOpen}
              />
            </div>

            {/* Otros campos */}
            <FormInput
              label="Nombre / Medida"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FormInput
                label="Código"
                name="code"
                value={formData.code}
                onChange={handleChange}
                required
              />
              <FormStockInput
                label="Stock Inicial"
                name="initial_stock_quantity"
                value={formData.initial_stock_quantity}
                onChange={handleStockChange}
                placeholder="Ej: 100"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <FormInput label="Marca" name="brand" value={formData.brand} onChange={handleChange} />
              <FormInput label="Ubicación" name="location" value={formData.location} onChange={handleChange} />
              <FormInput label="Posición" name="position" value={formData.position} onChange={handleChange} />
            </div>

            <FormInput
              label="Descripción"
              name="description"
              value={formData.description}
              onChange={handleChange}
            />

            <div className="flex items-center space-x-2">
              {/* asegurar booleano */}
              <input
                type="checkbox"
                id="has_subproducts"
                name="has_subproducts"
                checked={!!formData.has_subproducts}
                onChange={handleChange}
                className="w-4 h-4 text-primary-500 border-gray-300 rounded focus:ring-primary-500"
              />
              <label htmlFor="has_subproducts" className="ml-2 text-sm">
                Este producto tiene subproductos
              </label>
            </div>

            {/* Archivos */}
            <div>
              <label className="block mb-2 text-sm font-medium">Archivos (máx. 5)</label>
              <div className="flex items-center space-x-4">
                <label
                  htmlFor="images"
                  className="cursor-pointer bg-info-500 text-white px-4 py-2 rounded hover:bg-info-600"
                >
                  Seleccionar archivos
                </label>
                <span className="text-sm">
                  {previewFiles.length ? `${previewFiles.length} archivo(s)` : "Sin archivos"}
                </span>
              </div>
              <input
                id="images"
                type="file"
                multiple
                accept="image/*,video/*,application/pdf"
                onChange={handleFileChange}
                className="hidden"
              />
              {previewFiles.length > 0 && (
                <ul className="mt-2 text-sm text-gray-600 space-y-1">
                  {previewFiles.map((nm, i) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="truncate">{nm}</span>
                      <button
                        type="button"
                        onClick={() => removeFile(i)}
                        className="text-gray-400 hover:text-red-600"
                      >
                        ✖
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* Botones */}
            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={onClose}
                disabled={loading}
                className="bg-neutral-500 text-white px-4 py-2 rounded hover:bg-neutral-600"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
              >
                {loading ? "Guardando..." : "Actualizar Producto"}
              </button>
            </div>
          </form>
        </div>

        {/* Carrusel */}
        {childrenWithProps && (
          <div className="flex-1 p-4 bg-background-50 rounded max-h-[80vh] overflow-y-auto">
            {childrenWithProps}
          </div>
        )}
      </div>

      {/* Confirmar eliminación */}
      <DeleteMessage
        isOpen={isDeleteOpen}
        onClose={closeDeleteRequest}
        onDelete={confirmDelete}
        isDeleting={isDeleting}
        deleteError={deleteError?.message || null}
        itemName="el archivo"
        itemIdentifier={fileToDelete?.filename || fileToDelete?.name || ""}
      />
    </Modal>
  );
}

EditProductModal.propTypes = {
  product: PropTypes.object.isRequired,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSave: PropTypes.func,
  children: PropTypes.node,
  loading: PropTypes.bool,
};
