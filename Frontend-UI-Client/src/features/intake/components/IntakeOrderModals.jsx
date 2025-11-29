// src/features/intake/components/IntakeOrderModals.jsx
import React from "react";
import { useAuth } from "@/context/AuthProvider";
import DeleteMessage from "@/components/common/DeleteMessage";
import IntakeOrderDetailDrawer from "./IntakeOrderDetailDrawer";

/**
 * Modales/Drawers de Órdenes de Ingreso (Intake)
 * Patron alineado con CuttingOrderModals para consistencia.
 * Actualmente Intake usa un Drawer para ver / editar.
 * - Crear: (placeholder) se puede implementar un wizard similar luego.
 * - Editar / Ver: reutiliza IntakeOrderDetailDrawer (editable interno)
 * - Eliminar: soft delete / confirmación (usa DeleteMessage)
 */
const IntakeOrderModals = ({
  modalState,
  closeModal,
  onCreateOrder,     // futuro: si se agrega wizard de creación
  onUpdateOrder,     // fallback si el drawer no maneja update internamente
  handleSave,        // muestra toast/feedback en el padre
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
      {/* Crear nueva orden (solo admin) - Placeholder: no hay wizard todavía */}
      {type === "create" && isStaff && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-lg">
            <h2 className="text-lg font-semibold mb-2">Crear Orden de Ingreso</h2>
            <p className="text-sm text-gray-600 mb-4">
              El flujo de creación aún no está implementado. Aquí se integrará un wizard similar al de cutting.
            </p>
            <div className="flex gap-2 justify-end">
              <button
                onClick={closeModal}
                className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300 text-gray-800 text-sm"
              >Cancelar</button>
              <button
                onClick={() => {
                  // Ejemplo de futura integración: onCreateOrder?.(payload)
                  closeModal();
                }}
                className="px-4 py-2 rounded bg-primary-600 hover:bg-primary-700 text-white text-sm"
              >Aceptar</button>
            </div>
          </div>
        </div>
      )}

      {/* Drawer ver/editar (staff puede editar dentro) */}
      {type === "view" && orderId && (
        <IntakeOrderDetailDrawer
          isOpen
          order={orderData}
          onClose={closeModal}
          onSaved={(updated, message) => {
            if (handleSave && message) handleSave(message);
            else if (onUpdateOrder && updated) onUpdateOrder(updated);
          }}
        />
      )}

      {/* Atajo para editar explícito, aunque el Drawer ya permite edición inline */}
      {type === "edit" && isStaff && orderId && (
        <IntakeOrderDetailDrawer
          isOpen
          order={orderData}
          onClose={closeModal}
          forceEditMode
          onSaved={(updated, message) => {
            if (handleSave && message) handleSave(message);
            else if (onUpdateOrder && updated) onUpdateOrder(updated);
          }}
        />
      )}

      {/* Confirmación de eliminación (soft delete) - solo admin */}
      {type === "deleteConfirm" && isStaff && orderData && (
        <DeleteMessage
          isOpen
          onClose={closeModal}
          onDelete={() => onDeleteOrder?.(orderData.id)}
          isDeleting={isDeleting}
          deleteError={deleteError}
          clearDeleteError={clearDeleteError}
          itemName="la orden de ingreso"
          itemIdentifier={`#${orderId}`}
        />
      )}
    </>
  );
};

export default IntakeOrderModals;
