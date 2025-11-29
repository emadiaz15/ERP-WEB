import React, { useEffect, useMemo, useState, useCallback } from "react";
import PropTypes from "prop-types";

import { useAuth } from "@/context/AuthProvider";
import { listUsers } from "@/features/user/services/listUsers";
import { useProducts } from "@/features/product/hooks/useProductHooks";
import { useUpdateCuttingOrder } from "@/features/cuttingOrder/hooks/useCuttingOrders";
import { listSubproductsByParent } from "@/features/cuttingOrder/services/cuttingOrders";
import { buildCuttingOrderPayload } from "@/features/cuttingOrder/utils/buildCuttingOrderPayload";

import Modal from "@/components/ui/Modal";
import ErrorMessage from "@/components/common/ErrorMessage";

import Step1Form from "@/features/cuttingOrder/components/wizard/Step1Form";
import Step2Subproducts from "@/features/cuttingOrder/components/wizard/Step2Subproducts";
import { getAvailableStock, stringifyServerError } from "@/features/cuttingOrder/components/wizard/helpers";

/* ============================ Helpers de ID ============================ */
const numOrNull = (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
};

const extractNumericProductId = (order) => {
    if (!order) return null;
    const p = order.product;

    // Objeto con id/pk
    if (p && typeof p === "object") {
        const n = numOrNull(p.id ?? p.pk ?? p.product_id ?? p.product_pk);
        if (n != null) return n;
    }

    // Campos planos
    return (
        numOrNull(order.product_id) ??
        numOrNull(order.product_pk) ??
        numOrNull(p) ?? // solo si es numérico o string numérico
        null
    );
};

/* ===================== Componente principal ===================== */
export default function EditCuttingOrderWizard({
    isOpen,
    onClose,
    onSave,
    order,
    lockProduct = true, // por defecto no permite cambiar el producto en edición
    embedded = false,
}) {
    const { user } = useAuth();
    const orderId = order?.id;

    // ===== Pasos =====
    const [step, setStep] = useState(1);

    // ===== Paso 1 =====
    const [orderNumber, setOrderNumber] = useState("");
    const [customer, setCustomer] = useState("");
    const [assignedTo, setAssignedTo] = useState("");
    const [operatorCanEdit, setOperatorCanEdit] = useState(true);
    const [quantityToCut, setQuantityToCut] = useState("");

    // Users
    const [users, setUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [usersError, setUsersError] = useState("");

    // Resolución de producto (ID y/o por código)
    const [resolvedProductId, setResolvedProductId] = useState(null);
    const [codeInput, setCodeInput] = useState("");
    const [codeSearch, setCodeSearch] = useState("");

    const {
        products,
        loading: loadingProducts,
        isError: productsErrorFlag,
        error: productsError,
    } = useProducts({
        status: true,
        page_size: 100,
        code: lockProduct ? undefined : (codeSearch || undefined),
    });

    // Si lockProduct=true, ocultamos selector pasando productId al Step1Form
    const initialProductId = useMemo(() => extractNumericProductId(order), [order]);
    const [selectedProductId, setSelectedProductId] = useState(
        initialProductId != null ? String(initialProductId) : ""
    );

    // Subproductos
    const [subproducts, setSubproducts] = useState([]);
    const [loadingSubs, setLoadingSubs] = useState(false);
    const [subsError, setSubsError] = useState("");

    // Selección y estado general
    const [selectedItems, setSelectedItems] = useState({});
    const [error, setError] = useState("");
    const [localError, setLocalError] = useState("");
    const [updateOrder, { loading, error: updateError }] = useUpdateCuttingOrder();

    // ===== Reset + Precarga desde la orden =====
    useEffect(() => {
        if (!isOpen || !order) return;

        setStep(1);
        setUsers([]);
        setUsersError("");
        setSubproducts([]);
        setSubsError("");
        setError("");

        setCodeInput("");
        setCodeSearch("");

        // Precarga campos
        setOrderNumber(order?.order_number != null ? String(order.order_number) : String(orderId ?? ""));
        setCustomer(order?.customer || "");
        setAssignedTo(
            order?.assigned_to_id != null
                ? String(order.assigned_to_id)
                : order?.assigned_to != null
                    ? String(order.assigned_to)
                    : ""
        );
        setOperatorCanEdit(
            order?.operator_can_edit_items != null ? !!order.operator_can_edit_items : true
        );
        setQuantityToCut(
            order?.quantity_to_cut != null ? String(order.quantity_to_cut) : ""
        );

        // Precarga ítems
        const next = {};
        (order?.items || []).forEach((it) => {
            const sid = it?.subproduct?.id ?? it?.subproduct;
            const qty = it?.cutting_quantity;
            if (sid != null && qty != null) next[sid] = String(qty);
        });
        setSelectedItems(next);

        // Producto: resolvemos ID
        const npid = extractNumericProductId(order);
        setResolvedProductId(npid);
        setSelectedProductId(npid != null ? String(npid) : "");

        // Si no hubo ID pero tenemos código, podríamos buscarlo (opcional)
        // const productCodeFromOrder =
        //   (typeof order?.product === "object" ? order?.product?.code : null) ||
        //   order?.product_code ||
        //   null;
        // if (!npid && productCodeFromOrder) setCodeSearch(String(productCodeFromOrder));
    }, [isOpen, order, orderId]);

    // Users activos
    useEffect(() => {
        if (!isOpen) return;
        setLoadingUsers(true);
        listUsers("/users/list/?status=true")
            .then((data) => setUsers(data.results || []))
            .catch(() => setUsersError("No se pudieron cargar los usuarios"))
            .finally(() => setLoadingUsers(false));
    }, [isOpen]);

    // ID activo de producto (SIEMPRE numérico o null)
    const activeProductId = useMemo(
        () => numOrNull(resolvedProductId ?? (lockProduct ? initialProductId : selectedProductId)),
        [resolvedProductId, lockProduct, initialProductId, selectedProductId]
    );

    // Subproductos del producto activo (vía service con <int:prod_pk>)
    useEffect(() => {
        if (!isOpen) return;
        const pid = numOrNull(activeProductId);
        if (pid == null) return;

        setLoadingSubs(true);
        listSubproductsByParent(pid, { status: true })
            .then((norm) => {
                const all = norm?.results || [];
                const active = all.filter(
                    (s) => s?.status === true || String(s?.status ?? "").toLowerCase() === "activo"
                );
                setSubproducts(active);
            })
            .catch(() => setSubsError("No se pudieron cargar subproductos"))
            .finally(() => setLoadingSubs(false));
    }, [isOpen, activeProductId]);

    // Si cambia producto en modo desbloqueado, limpiamos selección
    useEffect(() => {
        if (!isOpen || lockProduct) return;
        setSelectedItems({});
    }, [activeProductId, isOpen, lockProduct]);

    // ===== Validaciones =====
    const validateStep1 = () =>
        orderNumber.trim() && customer.trim() && numOrNull(activeProductId) != null;

    const validateStep2 = () => {
        if (operatorCanEdit) return true; // permite guardar sin ítems
        const anyValid = Object.entries(selectedItems).some(([_, q]) => {
            const qty = Number(q);
            return !Number.isNaN(qty) && qty > 0;
        });
        if (!anyValid) return false;

        for (const [idStr, qty] of Object.entries(selectedItems)) {
            const sp = subproducts.find((s) => Number(s.id) === Number(idStr));
            if (!sp) continue;
            if (Number(qty) > getAvailableStock(sp)) return false;
        }
        return true;
    };

    const handleNext = () => {
        setError("");
        if (!validateStep1()) setError("Rellena todos los campos del paso 1");
        else setStep(2);
    };

    const handleBack = () => {
        setError("");
        setStep(1);
    };

    const onToggle = (id) => {
        const sp = subproducts.find((s) => Number(s.id) === Number(id));
        if (!sp || getAvailableStock(sp) <= 0) return;
        setSelectedItems((prev) => {
            const nxt = { ...prev };
            if (nxt[id]) delete nxt[id];
            else nxt[id] = 1;
            return nxt;
        });
    };

    const onQuantityChange = (id, val) => {
        const n = parseFloat(String(val).replace(",", "."));
        setSelectedItems((prev) => ({ ...prev, [id]: Number.isNaN(n) ? "" : n }));
    };

    const onSearchByCode = useCallback(() => {
        if (lockProduct) return;
        setSelectedProductId("");
        setCodeSearch(codeInput.trim());
    }, [codeInput, lockProduct]);

    const sumSelectedQty = useMemo(
        () => Object.values(selectedItems).reduce((acc, v) => acc + (Number(v) || 0), 0),
        [selectedItems]
    );

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        // Validación stock por ítem
        for (const [idStr, qty] of Object.entries(selectedItems)) {
            const sp = subproducts.find((s) => Number(s.id) === Number(idStr));
            if (!sp) continue;
            const available = getAvailableStock(sp);
            if (Number(qty) > available) {
                setLocalError(
                    `items: Stock insuficiente para el subproducto ID ${sp.id}${sp?.number_coil != null ? ` (N° Bob/Rollo ${sp.number_coil})` : ""
                    }. Necesita ${Number(qty).toFixed(2)}, disponible ${Number(available).toFixed(2)}.`
                );
                return;
            }
        }

        if (!validateStep2()) {
            setError(
                "Debes elegir al menos un subproducto y cantidad válidos (o habilitar que el operario asigne luego)."
            );
            return;
        }

        // Objetivo total
        const target = Number(String(quantityToCut).replace(",", ".")) || sumSelectedQty;
        if (!(target > 0)) {
            setError(
                "Debes indicar un 'Objetivo total (Mts)' mayor a 0 o seleccionar ítems con cantidad."
            );
            return;
        }

        // Ítems
        const items = Object.entries(selectedItems)
            .filter(([, q]) => Number(q) > 0)
            .map(([sub, cutting_quantity]) => ({
                subproduct: Number(sub),
                cutting_quantity: Number(cutting_quantity),
            }));

        const payload = buildCuttingOrderPayload({
            product: Number(activeProductId),
            order_number: Number(orderNumber),
            customer: customer.trim(),
            quantity_to_cut: target,
            items,
            assigned_to: assignedTo ? Number(assignedTo) : null,
            operator_can_edit_items: !!operatorCanEdit,
        }, { mode: "update" });

        try {
            const updated = await updateOrder(orderId, payload, "PATCH");
            onSave?.(updated);
            onClose();
        } catch (err) {
            const raw = err?.response?.data;
            const rawMsg = (typeof raw === "string" ? raw : raw?.detail) || "";
            if (/UNIQUE constraint failed.*order_number/i.test(rawMsg)) {
                setError("El número de pedido ya existe. Probá con otro.");
            } else {
                setLocalError(stringifyServerError(raw) || err?.message || "Error al actualizar la orden");
            }
            console.error("CuttingOrder update error:", raw || err);
        }
    };

    // Solo para mostrar resumen de producto (si está disponible en el hook)
    const selectedProduct = useMemo(() => {
        const pid = Number(activeProductId);
        return (products || []).find((p) => Number(p.id) === pid);
    }, [products, activeProductId]);

    const selectedProductSummary = selectedProduct ? (
        <div className="mt-2 text-sm text-gray-600">
            <div>
                <strong>Seleccionado:</strong> {selectedProduct.code} —{" "}
                {selectedProduct.name || selectedProduct.description || "(sin nombre)"}
            </div>
            {selectedProduct.category_name && <div>Categoría: {selectedProduct.category_name}</div>}
            {selectedProduct.brand && <div>Marca: {selectedProduct.brand}</div>}
        </div>
    ) : null;

    const Body = (
        <div className="flex flex-col gap-4 text-text-primary">
            {(error || localError || usersError || subsError || productsError || updateError) && (
                <ErrorMessage
                    message={
                        error ||
                        localError ||
                        usersError ||
                        subsError ||
                        (productsErrorFlag && (productsError?.message || "Error con productos")) ||
                        (updateError && (updateError?.message || String(updateError)))
                    }
                    onClose={() => setError("")}
                />
            )}

            <form
                onSubmit={step === 2 ? handleSubmit : (e) => e.preventDefault()}
                className="space-y-4"
            >
                <div className="flex flex-col lg:flex-row gap-4 h-full">
                    <div className="flex-1 bg-background-100 p-4 rounded overflow-y-auto max-h-[70vh]">
                        {step === 1 ? (
                            <Step1Form
                                orderNumber={orderNumber}
                                setOrderNumber={setOrderNumber}
                                customer={customer}
                                setCustomer={setCustomer}
                                productId={lockProduct ? (activeProductId ?? "") : undefined}
                                codeInput={codeInput}
                                setCodeInput={setCodeInput}
                                onSearchByCode={onSearchByCode}
                                loadingProducts={loadingProducts}
                                products={products}
                                selectedProductId={selectedProductId}
                                setSelectedProductId={setSelectedProductId}
                                selectedProductSummary={selectedProductSummary}
                                userDisplayName={`${user?.username || ""}`}
                                assignedTo={assignedTo}
                                setAssignedTo={setAssignedTo}
                                users={users}
                                loadingUsers={loadingUsers}
                                operatorCanEdit={operatorCanEdit}
                                setOperatorCanEdit={setOperatorCanEdit}
                                showOperatorToggle={true}
                                quantityToCut={quantityToCut}
                                setQuantityToCut={setQuantityToCut}
                            />
                        ) : (
                            <Step2Subproducts
                                loadingSubs={loadingSubs}
                                subproducts={subproducts}
                                selectedItems={selectedItems}
                                onToggle={onToggle}
                                onQuantityChange={onQuantityChange}
                            />
                        )}
                    </div>

                    {selectedProduct && (
                        <div className="flex-1 bg-background-50 p-4 rounded overflow-y-auto max-h-[70vh]">
                            <h4 className="font-semibold mb-2">Producto</h4>
                            {selectedProductSummary || (
                                <div className="text-sm text-gray-600">Sin datos adicionales.</div>
                            )}
                        </div>
                    )}
                </div>

                <div className="flex justify-end gap-2 mt-2">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-4 py-2 bg-neutral-500 text-white rounded hover:bg-neutral-600 transition-colors"
                        disabled={loading}
                    >
                        Cancelar
                    </button>

                    {step === 1 ? (
                        <button
                            type="button"
                            onClick={handleNext}
                            className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
                        >
                            Siguiente →
                        </button>
                    ) : (
                        <div className="flex gap-2">
                            <button
                                type="button"
                                onClick={handleBack}
                                className="px-4 py-2 bg-neutral-500 text-white rounded hover:bg-neutral-600 transition-colors"
                                disabled={loading}
                            >
                                ← Atrás
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
                            >
                                {loading ? "Guardando..." : "Guardar cambios"}
                            </button>
                        </div>
                    )}
                </div>
            </form>
        </div>
    );

    if (embedded) return Body;

    return (
        <>
            <Modal
                isOpen={isOpen}
                onClose={onClose}
                title={`Editar Orden de Corte #${orderId ?? ""}`}
                position="center"
                maxWidth="max-w-6xl"
                loading={Boolean(loading || loadingUsers || loadingSubs || loadingProducts)}
            >
                {Body}
            </Modal>
        </>
    );
}

EditCuttingOrderWizard.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func,       // callback para refrescar/mostrar toast
    order: PropTypes.object.isRequired,
    lockProduct: PropTypes.bool,
    embedded: PropTypes.bool,
};
