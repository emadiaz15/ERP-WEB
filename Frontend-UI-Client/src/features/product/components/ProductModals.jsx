
// src/features/product/components/ProductModals.jsx
import React from "react"
import CreateProductModal from "./CreateProductModal"
import EditProductModal from "./EditProductModal"
import ViewProductModal from "./ViewProductModal"
import ProductCarouselOverlay from "./ProductCarouselOverlay"
import DeleteMessage from "@/components/common/DeleteMessage"
import Spinner from "@/components/ui/Spinner"
import { useAuth } from "@/context/AuthProvider"
import { useProductFilesData } from "@/features/product/hooks/useProductFileHooks"

const ProductModals = ({
    modalState,
    closeModal,
    onCreateProduct,
    onUpdateProduct,
    handleSave,
    onDeleteProduct,
    isDeleting,
    deleteError,
    clearDeleteError,
}) => {
    const { user } = useAuth()
    const isStaff = user?.is_staff

    const { type, productData } = modalState
    const productId = productData?.id

    // Cargar archivos SOLO cuando estamos en edición (el modal de vista se encarga solo)
    const {
        files: editFiles = [],
        isLoading: isLoadingEditFiles,
    } = useProductFilesData(type === 'edit' && productId ? productId : null)

    if (!type) return null

    return (
        <>
            {type === "create" && isStaff && (
                <CreateProductModal
                    isOpen
                    onClose={closeModal}
                    onSave={onCreateProduct}
                />
            )}

            {type === "edit" && isStaff && productId && (
                <EditProductModal
                    isOpen
                    onClose={closeModal}
                    product={productData}
                    loading={isLoadingEditFiles}
                    // onSave ya no dispara updateProduct en el padre
                    onSave={() => {
                        onUpdateProduct && handleSave("¡Producto actualizado con éxito!");
                        closeModal();
                    }}                >
                    {isLoadingEditFiles ? null : editFiles.length > 0 ? (
                        <ProductCarouselOverlay
                            images={editFiles}
                            productId={productId}
                            editable
                            isEmbedded
                        />
                    ) : (
                        <p className="text-center text-gray-600">
                            No hay archivos multimedia.
                        </p>
                    )}
                </EditProductModal >
            )}

            {type === "view" && productId && (
                <ViewProductModal
                    isOpen
                    onClose={closeModal}
                    product={productData}
                />
            )}

            {type === "deleteConfirm" && isStaff && productData && (
                <DeleteMessage
                    isOpen
                    onClose={closeModal}
                    onDelete={() => onDeleteProduct(productData.id)}
                    isDeleting={isDeleting}
                    deleteError={deleteError}
                    clearDeleteError={clearDeleteError}
                    itemName="el producto"
                    itemIdentifier={productData.name || "SIN NOMBRE"}
                />
            )}
        </>
    )
}

export default ProductModals
