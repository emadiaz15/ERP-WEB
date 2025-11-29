import React, { useState, useEffect, useMemo, useCallback } from "react";
import PropTypes from "prop-types";
import { useAuth } from "@/context/AuthProvider";
import { listUsers } from "@/features/user/services/listUsers";
import { listSubproducts } from "@/features/product/services/subproducts/subproducts";
import { useProducts } from "@/features/product/hooks/useProductHooks";
import { useListSubproducts } from "@/features/product/hooks/useSubproductHooks";
import { useCreateCuttingOrder } from "@/features/cuttingOrder/hooks/useCuttingOrders";
import { buildCuttingOrderPayload } from "@/features/cuttingOrder/utils/buildCuttingOrderPayload";

import Modal from "@/components/ui/Modal";
import ErrorMessage from "@/components/common/ErrorMessage";

import Step1Form from "./Step1Form";
import Step2Subproducts from "./Step2Subproducts";
import { getAvailableStock, stringifyServerError } from "./helpers";

export default function CreateCuttingOrderWizard({
    isOpen,
    onClose,
    onSave,
    productId,
    preselectedSubproducts = [],
    allowEmptyItemsDefault = true,
    lockToPreselected = false,
    hideOperatorToggle = false,
    embedded = false,
    /** ⬅️ NUEVO: para caso 1 (desde SubproductList) */
    initialRequestedQty = null,
}) {
    const { user } = useAuth();

    // Pasos
    const [step, setStep] = useState(1);

    // Paso 1
    const [orderNumber, setOrderNumber] = useState("");
    const [customer, setCustomer] = useState("");
    const [assignedTo, setAssignedTo] = useState("");
    const [operatorCanEdit, setOperatorCanEdit] = useState(allowEmptyItemsDefault);
    const [quantityToCut, setQuantityToCut] = useState("");

    // Mostrar advertencias de paso 1 cuando el usuario intenta continuar
    const [step1Attempted, setStep1Attempted] = useState(false);

    // Users
    const [users, setUsers] = useState([]);
    const [loadingUsers, setLoadingUsers] = useState(false);
    const [usersError, setUsersError] = useState("");

    // Búsqueda producto por código (solo si no viene productId)
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
        code: productId ? undefined : codeSearch || undefined,
    });

    const [selectedProductId, setSelectedProductId] = useState(productId || "");

    // Autoselección por código SOLO si aún no hay algo elegido
    useEffect(() => {
        if (!isOpen || productId) return;
        if (!codeSearch) return;
        if (selectedProductId) return;

        const matches = (products || []).filter(
            (p) => String(p.code) === String(codeSearch)
        );
        if (matches.length === 1) {
            setSelectedProductId(String(matches[0].id));
        }
    }, [isOpen, productId, codeSearch, products, selectedProductId]);

    const activeProductId = productId || selectedProductId;

    // (Subproducts hook and accumulation defined later)

    // Selección y estado general
    const [selectedItems, setSelectedItems] = useState({});
    const [error, setError] = useState("");
    const [createOrder, { loading, error: errorCreate }] = useCreateCuttingOrder();

    // Reset al abrir
    useEffect(() => {
        if (isOpen) {
            setStep(1);
            setOrderNumber("");
            setCustomer("");
            setAssignedTo("");
            setUsers([]);
            setUsersError("");
            setSelectedItems({});
            setSelectedProductId(productId || "");
            setError("");
            setCodeInput("");
            setCodeSearch("");
            setOperatorCanEdit(allowEmptyItemsDefault);
            setQuantityToCut(
                initialRequestedQty != null && initialRequestedQty !== ""
                    ? String(initialRequestedQty)
                    : ""
            );
            setStep1Attempted(false);
        }
    }, [isOpen, productId, allowEmptyItemsDefault, initialRequestedQty]);

    // Preselección (no poner “1” — dejamos vacío para que el admin distribuya libremente)
    useEffect(() => {
        if (!isOpen) return;
        if (Array.isArray(preselectedSubproducts) && preselectedSubproducts.length) {
            setSelectedItems((prev) => {
                if (Object.keys(prev).length > 0) return prev;
                const next = {};
                preselectedSubproducts.forEach((id) => {
                    next[id] = ""; // ← vacío, no 1
                });
                return next;
            });
        }
    }, [isOpen, preselectedSubproducts]);

    // Users activos
    useEffect(() => {
        if (!isOpen) return;
        setLoadingUsers(true);
        listUsers("/users/list/?status=true")
            .then((data) => setUsers(data.results || []))
            .catch(() => setUsersError("No se pudieron cargar los usuarios"))
            .finally(() => setLoadingUsers(false));
    }, [isOpen]);

    // (useEffect removed, now handled by useListSubproducts)

    // Subproductos: página actual vía hook (paginado)
    const {
        subproducts: pagedSubproducts,
        isLoading: loadingSubs,
        isError: subsErrorFlag,
        error: subsErrorObj,
        nextPageUrl,
    } = useListSubproducts(activeProductId);

    const subsError = subsErrorFlag
        ? subsErrorObj?.message || "No se pudieron cargar subproductos"
        : "";

    // Acumulación local para infinite scroll
    const [accumulatedSubs, setAccumulatedSubs] = useState([]);
    const [localNextUrl, setLocalNextUrl] = useState(null);
    const [isFetchingNextPage, setIsFetchingNextPage] = useState(false);

    // Reset acumulado al abrir/cambiar producto
    useEffect(() => {
        if (!isOpen) return;
        setAccumulatedSubs([]);
        setLocalNextUrl(null);
    }, [isOpen, activeProductId]);

    // Sembrar con la página actual del hook
    useEffect(() => {
        if (!isOpen) return;
        const active = (pagedSubproducts || []).filter((s) => s?.status === true);
        setAccumulatedSubs(active);
        setLocalNextUrl(nextPageUrl || null);
    }, [isOpen, pagedSubproducts, nextPageUrl]);

    const fetchNextPage = useCallback(async () => {
        if (!localNextUrl || isFetchingNextPage) return;
        try {
            setIsFetchingNextPage(true);
            const data = await listSubproducts(activeProductId, localNextUrl);
            const nextActives = (data?.results || []).filter((s) => s?.status === true);
            setAccumulatedSubs((prev) => [...prev, ...nextActives]);
            setLocalNextUrl(data?.next || null);
        } catch (_e) {
            // noop
        } finally {
            setIsFetchingNextPage(false);
        }
    }, [activeProductId, localNextUrl, isFetchingNextPage]);

    // Si cambia producto, limpiar selección
    const prevProductRef = React.useRef(activeProductId);
    useEffect(() => {
        if (!isOpen) return;
        if (prevProductRef.current !== activeProductId) {
            setSelectedItems({});
            prevProductRef.current = activeProductId;
        }
    }, [activeProductId, isOpen]);

    // Filtro por preselección si corresponde
    const filteredSubproducts = useMemo(() => {
        const base = accumulatedSubs;
        if (!lockToPreselected || !preselectedSubproducts?.length) return base;
        const setIds = new Set(preselectedSubproducts.map(Number));
        return base.filter((s) => setIds.has(Number(s.id)));
    }, [accumulatedSubs, lockToPreselected, preselectedSubproducts]);


    const validSubIds = useMemo(
        () => new Set(filteredSubproducts.map((s) => s.id)),
        [filteredSubproducts]
    );

    // Suma total de cantidades seleccionadas en el paso 2
    const sumSelectedQty = useMemo(
        () => Object.values(selectedItems).reduce((acc, v) => acc + (Number(v) || 0), 0),
        [selectedItems]
    );

    // Helpers de validación (Paso 1 ahora exige assignedTo)
    const validateStep1 = () => {
        // Validar campos obligatorios del paso 1
        if (!assignedTo) return false;
        if (!(productId || selectedProductId)) return false;
        // Si operatorCanEdit está activo, cantidad pedida es obligatoria y no se puede avanzar sin completarla
        if (operatorCanEdit) {
            const qty = Number(String(quantityToCut).replace(",", "."));
            if (!(qty > 0)) return false;
        }
        return true;
    };

    // Reglas Paso 2 (según requisitos):
    // - Si operatorCanEdit === true ⇒ exigir cantidad pedida > 0
    // - Si hay cantidad pedida ⇒ sum(items) <= cantidad pedida
    // - Si operatorCanEdit === false ⇒ exigir al menos 1 ítem > 0 (como ya hacías)
    // Permite crear la orden si hay cantidad pedida global > 0, aunque los subproductos seleccionados tengan cantidad vacía o 0
    const validateStep2 = () => {
        const requested = Number(String(quantityToCut).replace(",", "."));

        // Si operatorCanEdit está activo, cantidad pedida es obligatoria y no se puede avanzar sin completarla
        if (operatorCanEdit) {
            if (!(requested > 0)) return false;
            // Permitir crear aunque los subproductos seleccionados tengan cantidad vacía o 0
            if (requested > 0 && sumSelectedQty > requested) return false;
            return true;
        }

        if (requested > 0 && sumSelectedQty > requested) return false;

        // Si operatorCanEdit está inactivo, permitir crear si hay cantidad pedida global > 0, aunque los subproductos seleccionados tengan cantidad vacía o 0
        if (!operatorCanEdit) {
            if (requested > 0) return true;
            // Si no hay cantidad pedida, exigir al menos un subproducto con cantidad > 0
            const anyValid = Object.entries(selectedItems).some(([id, q]) => {
                const qty = Number(q);
                return validSubIds.has(Number(id)) && !Number.isNaN(qty) && qty > 0;
            });
            if (!anyValid) return false;
            for (const [idStr, qty] of Object.entries(selectedItems)) {
                const sp = filteredSubproducts.find(
                    (s) => Number(s.id) === Number(idStr)
                );
                if (!sp) continue;
                if (Number(qty) > getAvailableStock(sp)) return false;
            }
        }
        return true;
    };

    const handleNext = () => {
        setError("");
        setStep1Attempted(true);
        if (!validateStep1()) {
            if (!assignedTo) {
                setError('Debes seleccionar un usuario en "Asignar a".');
            } else if (!(productId || selectedProductId)) {
                setError("Debes seleccionar un producto.");
            } else {
                setError("Rellena todos los campos del paso 1.");
            }
            return;
        }
        setStep(2);
    };

    const handleBack = () => {
        setError("");
        setStep(1);
    };

    const onToggle = (id) => {
        const sp = filteredSubproducts.find((s) => Number(s.id) === Number(id));
        if (!sp) return;
        setSelectedItems((prev) => {
            const nxt = { ...prev };
            if (nxt[id] !== undefined) delete nxt[id];
            else nxt[id] = ""; // ← arranca vacío
            return nxt;
        });
    };

    const onQuantityChange = (id, val) => {
        const n = parseFloat(val);
        setSelectedItems((prev) => ({ ...prev, [id]: Number.isNaN(n) ? "" : n }));
    };

    const onSearchByCode = useCallback(() => {
        setCodeSearch(codeInput.trim());
    }, [codeInput]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        // Validación stock por ítem
        for (const [idStr, qty] of Object.entries(selectedItems)) {
            const sp = filteredSubproducts.find((s) => Number(s.id) === Number(idStr));
            if (!sp) continue;
            const available = getAvailableStock(sp);
            if (Number(qty) > available) {
                setError(
                    `items: Stock insuficiente para el subproducto ID ${sp.id}${sp?.number_coil != null ? ` (N° Bob/Rollo ${sp.number_coil})` : ""
                    }. Necesita ${Number(qty).toFixed(2)}, disponible ${Number(available).toFixed(2)}.`
                );
                return;
            }
        }

        // Reglas adicionales de negocio
        const requested = Number(String(quantityToCut).replace(",", "."));
        if (operatorCanEdit && !(requested > 0)) {
            setError("Debes indicar una 'Cantidad pedida (Mts)' para permitir que el operario seleccione subproductos.");
            return;
        }
        if (requested > 0 && sumSelectedQty > requested) {
            setError(
                `La suma de cantidades (${sumSelectedQty.toFixed(2)} Mts) supera la Cantidad pedida (${requested.toFixed(2)} Mts). Ajusta los valores.`
            );
            return;
        }

        if (!validateStep2()) {
            setError(
                "Revisa el Paso 2: cantidades válidas y reglas de 'Cantidad pedida'."
            );
            return;
        }

        // Objetivo total (= quantityToCut si está, si no la suma de ítems)
        const target = requested > 0 ? requested : sumSelectedQty;
        if (!(target > 0)) {
            setError(
                "Debes indicar un 'Objetivo total (Mts)' mayor a 0 o seleccionar ítems con cantidad."
            );
            return;
        }

        // Ítems: incluir solo los subproductos con cantidad > 0
        const items = Object.entries(selectedItems)
            .filter(([id, q]) => validSubIds.has(Number(id)) && Number(q) > 0)
            .map(([sub, cutting_quantity]) => ({
                subproduct: Number(sub),
                cutting_quantity: Number(cutting_quantity),
            }));

        // Si hay cantidad pedida global, permitir crear aunque items esté vacío
        if (items.length === 0 && !(requested > 0)) {
            setError("Debes seleccionar al menos un subproducto con cantidad o indicar una cantidad pedida.");
            return;
        }

        const payload = buildCuttingOrderPayload({
            product: Number(activeProductId),
            order_number: Number(orderNumber),
            customer: customer.trim(),
            quantity_to_cut: target,
            items,
            assigned_to: assignedTo ? Number(assignedTo) : null,
            operator_can_edit_items: !!operatorCanEdit,
        });

        // setLoading(true) eliminado: el estado loading viene de useCreateCuttingOrder
        try {
            const created = await createOrder(payload);
            if (created && (created.id || created.status === 201 || created.status === 200)) {
                onSave?.(created);
                // Cerrar inmediatamente; el toast se maneja fuera (contenedor padre)
                onClose();
            } else {
                setError("No se pudo crear la orden. Intenta nuevamente.");
            }
        } catch (err) {
            const raw = err?.response?.data;
            const rawMsg = (typeof raw === "string" ? raw : raw?.detail) || "";
            if (/UNIQUE constraint failed.*order_number/i.test(rawMsg)) {
                setError(
                    "El número de pedido ya existe. Probá con otro (o aceptá el sugerido)."
                );
            } else {
                setError(
                    stringifyServerError(raw) ||
                    err?.message ||
                    "Error al crear la orden"
                );
            }
            console.error("CuttingOrder create error:", raw || err);
        }
    };

    const selectedProduct = useMemo(() => {
        const pid = Number(activeProductId);
        return (products || []).find((p) => Number(p.id) === pid);
    }, [products, activeProductId]);

    const selectedProductSummary = selectedProduct ? (
        <div className="mt-2 text-sm text-gray-600">
            <div>
                <strong>Seleccionado:</strong> {selectedProduct.code} —{" "}
                {selectedProduct.name ||
                    selectedProduct.description ||
                    "(sin nombre)"}
            </div>
            {selectedProduct.category_name && (
                <div>Categoría: {selectedProduct.category_name}</div>
            )}
            {selectedProduct.brand && <div>Marca: {selectedProduct.brand}</div>}
        </div>
    ) : null;

    // Accesibilidad: manejar Enter para avanzar o crear
    const handleKeyDown = (e) => {
        if (e.key === "Enter") {
            if (step === 1 && validateStep1()) {
                e.preventDefault();
                handleNext();
            } else if (step === 2 && validateStep2()) {
                e.preventDefault();
                handleSubmit(e);
            }
        }
    };

    const Body = (
        <div className="flex flex-col gap-4 text-text-primary">
            {(error || usersError || subsError || productsError) && (
                <ErrorMessage
                    message={
                        error ||
                        usersError ||
                        subsError ||
                        (productsErrorFlag &&
                            (productsError?.message || "Error con productos"))
                    }
                    onClose={() => setError("")}
                />
            )}

            <form
                onSubmit={step === 2 ? handleSubmit : (e) => e.preventDefault()}
                className="space-y-4"
                tabIndex={0}
                onKeyDown={handleKeyDown}
            >
                <div className="flex flex-col lg:flex-row gap-4 h-full">
                    <div className="flex-1 bg-background-100 p-4 rounded overflow-y-auto max-h-[70vh]">
                        {step === 1 ? (
                            <Step1Form
                                orderNumber={orderNumber}
                                setOrderNumber={setOrderNumber}
                                customer={customer}
                                setCustomer={setCustomer}
                                productId={productId}
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
                                showOperatorToggle={!hideOperatorToggle && !lockToPreselected}
                                quantityToCut={quantityToCut}
                                setQuantityToCut={setQuantityToCut}
                                showAssigneeWarning={step1Attempted && !assignedTo}
                            />
                        ) : (
                            <Step2Subproducts
                                loadingSubs={loadingSubs}
                                subproducts={filteredSubproducts}
                                selectedItems={selectedItems}
                                onToggle={onToggle}
                                onQuantityChange={onQuantityChange}
                                requestedTotal={
                                    Number(String(quantityToCut).replace(",", ".")) || null
                                }
                                nextPageUrl={localNextUrl}
                                fetchNextPage={fetchNextPage}
                                isFetchingNextPage={isFetchingNextPage}
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
                                {loading ? "Guardando..." : "Crear Corte"}
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
                title="Crear Orden de Corte"
                position="center"
                maxWidth="max-w-6xl"
                loading={Boolean(loading || loadingUsers || loadingSubs || loadingProducts)}
            >
                {Body}
            </Modal>
        </>
    );
}

CreateCuttingOrderWizard.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func,
    productId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    preselectedSubproducts: PropTypes.arrayOf(
        PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    ),
    allowEmptyItemsDefault: PropTypes.bool,
    lockToPreselected: PropTypes.bool,
    hideOperatorToggle: PropTypes.bool,
    embedded: PropTypes.bool,
    /** ⬅️ NUEVO */
    initialRequestedQty: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};
