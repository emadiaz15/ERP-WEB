// src/components/CuttingCartButton.jsx (o donde lo tengas)
import React, { useState } from "react";
import { ClipboardDocumentListIcon } from "@heroicons/react/24/outline";
import { useNavigate } from "react-router-dom";
import CreateCuttingOrderWizard from "@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard";
import SuccessMessage from "@/components/common/SuccessMessage";

/**
 * Props opcionales:
 * - productId: number|string (si querés fijar el producto del corte)
 * - preselectedSubproducts: number[]|string[] (si venís desde un carrito/selección previa)
 * - allowEmptyItemsDefault: boolean (igual que en el wizard; por defecto true)
 * - lockToPreselected: boolean (filtra subproductos solo a los preseleccionados)
 * - hideOperatorToggle: boolean (oculta el toggle del operario)
 * - afterCreate: 'stay' | 'list' | 'detail'
 *    'stay'   -> cierra el modal y se queda donde está (por defecto)
 *    'list'   -> navega a /cutting/cutting-orders
 *    'detail' -> navega a /cutting/cutting-orders/:id si existe
 */
export default function CuttingCartButton({
    productId,
    preselectedSubproducts = [],
    allowEmptyItemsDefault = true,
    lockToPreselected = false,
    hideOperatorToggle = false,
    afterCreate = "stay",
}) {
    const navigate = useNavigate();
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const [showSuccess, setShowSuccess] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    const handleOpen = () => setIsCreateOpen(true);
    const handleClose = () => setIsCreateOpen(false);

    const handleSave = (created) => {
        // Toast de éxito local cuando permanecemos en la misma vista
        if (afterCreate === "stay") {
            const msg = created?.id
                ? `Orden #${created.id} creada correctamente`
                : "Orden creada correctamente";
            setSuccessMessage(msg);
            setShowSuccess(true);
            // autocierre del toast manejado por SuccessMessage; lo ocultamos luego
            setTimeout(() => setShowSuccess(false), 3000);
        }

        // Opcionalmente redirigir
        if (afterCreate === "list") {
            navigate("/cutting/cutting-orders");
        } else if (afterCreate === "detail" && created?.id) {
            navigate(`/cutting/cutting-orders/${created.id}`);
        }

        handleClose();
    };

    return (
        <>
            {showSuccess && (
                <div className="fixed top-20 right-5 z-[10000]">
                    <SuccessMessage message={successMessage} onClose={() => setShowSuccess(false)} />
                </div>
            )}
            <button
                type="button"
                onClick={handleOpen}
                className="relative rounded-full bg-primary-500 p-1 text-neutral-50 hover:text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-500 hover:bg-primary-600 transition-all"
                title="Crear Orden de Corte"
            >
                <span className="sr-only">Crear Orden de Corte</span>
                <ClipboardDocumentListIcon className="h-6 w-6" aria-hidden="true" />
            </button>

            {/* 🔁 Mismo wizard que en el toolbar */}
            <CreateCuttingOrderWizard
                isOpen={isCreateOpen}
                onClose={handleClose}
                onSave={handleSave}
                productId={productId}
                preselectedSubproducts={preselectedSubproducts}
                allowEmptyItemsDefault={allowEmptyItemsDefault}
                lockToPreselected={lockToPreselected}
                hideOperatorToggle={hideOperatorToggle}
                embedded={false}
            />
        </>
    );
}
