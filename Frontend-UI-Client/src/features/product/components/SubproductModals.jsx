import React from "react"
import PropTypes from "prop-types"
import { useAuth } from "@/context/AuthProvider"

import CreateSubproductModal from "./CreateSubproductModal"
import EditSubproductModal from "./EditSubproductModal"
import ViewSubproductModal from "./ViewSubproductModal"
import DeleteMessage from "@/components/common/DeleteMessage"
import SuccessMessage from "@/components/common/SuccessMessage"
import ProductCarouselOverlay from "./ProductCarouselOverlay"

import { useSubproductFilesData } from "@/features/product/hooks/useSubproductFileHooks"

const SubproductModals = ({
    modalState,
    closeModal,
    onCreateSubproduct,
    onUpdateSubproduct,
    onDeleteSubproduct,
    onCreateOrder,           // se mantiene por compatibilidad externa
    isDeleting = false,
    deleteError = null,
    clearDeleteError,
    parentProduct,
}) => {
    const { user } = useAuth()
    const isStaff = user?.is_staff

    const { type, subproductData } = modalState || {}
    const productId = parentProduct?.id
    const subproductId = subproductData?.id

    // Archivos multimedia (sólo cuando hay subproducto seleccionado)
    const {
        files = [],
        isLoading: isLoadingFiles,
    } = useSubproductFilesData(
        type && subproductId ? productId : null,
        type && subproductId ? subproductId : null
    )

    // Toast de éxito no bloqueante a nivel del contenedor (persiste tras cerrar el modal)
    const [successMsg, setSuccessMsg] = React.useState("")

    const handleCreatedWrapper = React.useCallback(async (fd) => {
        const created = await onCreateSubproduct(fd)
        setSuccessMsg("¡Subproducto creado con éxito!")
        return created
    }, [onCreateSubproduct])

    const handleUpdatedWrapper = React.useCallback((payload) => {
        const res = onUpdateSubproduct(payload)
        // si onUpdateSubproduct devuelve promesa, podríamos esperar; pero el toast es informativo
        setSuccessMsg("Subproducto actualizado correctamente")
        return res
    }, [onUpdateSubproduct])

    if (!type) return null

    return (
        <>
            {/* Crear subproducto */}
            {type === "create" && productId && isStaff && (
                <CreateSubproductModal
                    isOpen
                    onClose={closeModal}
                    product={parentProduct}
                    onCreateSubproduct={handleCreatedWrapper}
                />
            )}

            {/* Editar subproducto */}
            {type === "edit" && subproductData && isStaff && (
                <EditSubproductModal
                    isOpen
                    onClose={closeModal}
                    subproduct={subproductData}
                    onSave={handleUpdatedWrapper}
                    loading={isLoadingFiles}
                >
                    {files.length > 0 ? (
                        <ProductCarouselOverlay
                            images={files}
                            productId={productId}
                            subproductId={subproductId}
                            editable
                            isEmbedded
                        />
                    ) : (
                        <p className="p-4 text-center text-sm text-gray-600">
                            No hay archivos multimedia.
                        </p>
                    )}
                </EditSubproductModal>
            )}

            {/* Ver subproducto */}
            {type === "view" && subproductData && (
                <ViewSubproductModal
                    isOpen
                    onClose={closeModal}
                    subproduct={subproductData}
                    loading={isLoadingFiles}
                    mediaPanel={
                        files.length > 0 ? (
                            <ProductCarouselOverlay
                                images={files}
                                productId={productId}
                                subproductId={subproductId}
                                editable={false}
                                isEmbedded
                            />
                        ) : (
                            <p className="p-4 text-center text-sm text-gray-600">
                                No hay archivos multimedia.
                            </p>
                        )
                    }
                />
            )}

            {/* Se acepta "createOrder" para no romper openModal, pero no se renderiza aquí */}

            {/* Confirmar eliminación */}
            {type === "deleteConfirm" && subproductData && isStaff && (
                <DeleteMessage
                    isOpen
                    onClose={closeModal}
                    onDelete={() => onDeleteSubproduct({ id: subproductData.id })}
                    isDeleting={isDeleting}
                    deleteError={deleteError}
                    clearDeleteError={clearDeleteError}
                    itemName="el subproducto"
                    itemIdentifier={subproductData.brand || subproductData.id}
                />
            )}

            {successMsg && (
                <div className="fixed top-20 right-5 z-[10000]">
                    <SuccessMessage message={successMsg} onClose={() => setSuccessMsg("")} />
                </div>
            )}
        </>
    )
}

SubproductModals.propTypes = {
    modalState: PropTypes.shape({
        type: PropTypes.oneOf([
            "create",
            "edit",
            "view",
            "createOrder",     // aceptado pero no renderizado aquí
            "deleteConfirm",
        ]),
        subproductData: PropTypes.object,
    }),
    closeModal: PropTypes.func.isRequired,
    onCreateSubproduct: PropTypes.func.isRequired,
    onUpdateSubproduct: PropTypes.func.isRequired,
    onDeleteSubproduct: PropTypes.func.isRequired,
    onCreateOrder: PropTypes.func.isRequired,
    isDeleting: PropTypes.bool,
    deleteError: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
    clearDeleteError: PropTypes.func.isRequired,
    parentProduct: PropTypes.shape({ id: PropTypes.number }).isRequired,
}

export default SubproductModals
