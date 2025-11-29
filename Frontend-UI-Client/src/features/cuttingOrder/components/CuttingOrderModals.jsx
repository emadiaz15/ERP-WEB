// src/features/cuttingOrder/components/CuttingOrderModals.jsx
import React from "react";
import { useAuth } from "@/context/AuthProvider";
import DeleteMessage from "@/components/common/DeleteMessage";
import CreateCuttingOrderWizard from "@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard";
import EditCuttingOrderWizard from "@/features/cuttingOrder/components/wizard/EditCuttingOrderWizard";
import ViewCuttingOrderModal from "./ViewCuttingOrderModal";

/**
 * Modales de Órdenes de Corte
 * - Solo admin: crear, editar, eliminar (cancelar)
 * - No admin: solo ver (y usar filtros fuera de este componente)
 */
const CuttingOrderModals = ({
    modalState,
    closeModal,
    onCreateOrder,     // (opcional) si CreateCuttingOrderWizard delega el POST al padre
    onUpdateOrder,     // (opcional) fallback si el modal de edición NO ejecuta el update internamente
    handleSave,        // (opcional) muestra toast/feedback en el padre
    onDeleteOrder,
    isDeleting,
    deleteError,
    clearDeleteError,
}) => {
    const { user } = useAuth();
    const isStaff = !!user?.is_staff;

    const { type, orderData } = modalState || {};
    const orderId = orderData?.id;

    if (!type) return null;

    return (
        <>
            {/* Crear nueva orden (solo admin) */}
            {type === "create" && isStaff && (
                <CreateCuttingOrderWizard
                    isOpen
                    onClose={closeModal}
                    onSave={onCreateOrder} // Solo delega, no dispara toast aquí
                    productId={null}
                />
            )}

            {/* Editar orden (solo admin) */}
            {type === "edit" && isStaff && orderId && (
                <EditCuttingOrderWizard
                    isOpen
                    onClose={closeModal}
                    order={orderData}
                    lockProduct={true}  // misma apariencia que crear, pero producto fijo; ponlo en false si querés permitir cambiar
                    onSave={() => {
                        if (handleSave) {
                            handleSave("¡Orden de corte actualizada con éxito!");
                        } else if (onUpdateOrder) {
                            onUpdateOrder(orderData);
                        }
                    }}
                />
            )}

            {/* Ver detalles (cualquiera puede ver) */}
            {type === "view" && orderId && (
                <ViewCuttingOrderModal
                    isOpen
                    onClose={closeModal}
                    order={orderData}
                />
            )}

            {/* Confirmación de cancelación (soft cancel por workflow_status) - solo admin */}
            {type === "deleteConfirm" && isStaff && orderData && (
                <DeleteMessage
                    isOpen
                    onClose={closeModal}
                    onDelete={() => onDeleteOrder(orderData.id)}
                    isDeleting={isDeleting}
                    deleteError={deleteError}
                    clearDeleteError={clearDeleteError}
                    itemName="la orden de corte"
                    itemIdentifier={`#${orderId}`}
                />
            )}
        </>
    );
};

export default CuttingOrderModals;
