// src/features/cuttingOrder/components/wizard/Step1Form.jsx
import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import FormInput from "@/components/ui/form/FormInput";
import FormSelect from "@/components/ui/form/FormSelect";
import AsyncProductCombobox from "../../../product/components/AsyncProductCombobox";

const Step1Form = ({
    orderNumber, setOrderNumber,
    customer, setCustomer,
    productId,
    codeInput, setCodeInput,
    onSearchByCode,
    loadingProducts,
    products,
    selectedProductId, setSelectedProductId,
    userDisplayName,
    assignedTo, setAssignedTo,
    users, loadingUsers,
    operatorCanEdit, setOperatorCanEdit,
    showOperatorToggle = true,
    quantityToCut, setQuantityToCut,
    showAssigneeWarning = false, // ⬅️ NUEVO
}) => {
    // Asegura que el toggle arranque en true si viene indefinido
    useEffect(() => {
        if (operatorCanEdit == null) setOperatorCanEdit(true);
    }, [operatorCanEdit, setOperatorCanEdit]);

    const debounceRef = useRef(null);
    useEffect(() => {
        if (debounceRef.current) clearTimeout(debounceRef.current);
        debounceRef.current = setTimeout(() => {
            onSearchByCode();
        }, 250);
        return () => clearTimeout(debounceRef.current);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [codeInput]);

    return (
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <div className="sm:col-span-1">
                <FormInput
                    label="N° Pedido"
                    name="order_number"
                    type="number"
                    inputMode="numeric"
                    step={1}
                    min={1}
                    value={orderNumber}
                    onChange={(e) => setOrderNumber(e.target.value)}
                    required
                />
            </div>

            <div className="sm:col-span-3">
                <FormInput
                    label="Cliente"
                    name="customer"
                    value={customer}
                    onChange={(e) => setCustomer(e.target.value)}
                    required
                />
            </div>

            {!productId && (
                <div className="sm:col-span-4">
                    <label className="block text-sm font-medium text-text-secondary">
                        Código del producto
                    </label>
                    <div className="mt-1">
                        <input
                            type="text"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                            placeholder="Ej: 4027025"
                            value={codeInput}
                            onChange={(e) => setCodeInput(e.target.value)}
                        />
                    </div>

                    <div className="mt-3">
                        <AsyncProductCombobox
                            label="Producto (con subproductos)"
                            placeholder="Escribe código o nombre…"
                            value={selectedProductId}
                            onChange={(v) => setSelectedProductId(v)}
                        />
                    </div>
                </div>
            )}

            <div className="mt-2 text-sm text-gray-600 sm:col-span-2">
                <label>Creado por</label>
                <p><strong>{userDisplayName}</strong></p>
            </div>

            <div className="sm:col-span-2">
                <FormInput
                    label="Cantidad pedida (Mts)"
                    name="quantity_to_cut"
                    type="number"
                    inputMode="decimal"
                    step="0.01"
                    min="0.01"
                    value={quantityToCut}
                    onChange={(e) => setQuantityToCut(e.target.value)}
                    placeholder="Ej: 100.00"
                />
                <p className="mt-1 text-xs text-gray-500">
                    Si lo dejás vacío y seleccionás ítems en el paso 2, usaremos la suma de ítems.
                </p>
            </div>

            <div className="sm:col-span-2">
                <FormSelect
                    label="Asignar a"
                    name="assigned_to"
                    value={assignedTo}
                    onChange={(e) => setAssignedTo(e.target.value)}
                    loading={loadingUsers}
                    required
                    options={[
                        { value: "", label: "— Selecciona —" },
                        ...users.map((u) => ({
                            value: String(u.id),
                            label:
                                u.first_name && u.last_name
                                    ? `${u.first_name} ${u.last_name}`
                                    : (u.username || u.email || `user_${u.id}`),
                        })),
                    ]}
                />
                {showAssigneeWarning && (
                    <p className="mt-1 text-xs text-red-600">
                        Debes seleccionar un usuario en “Asignar a”.
                    </p>
                )}
            </div>

            {showOperatorToggle && (
                <div className="col-span-1 sm:col-span-4">
                    <label className="inline-flex items-center space-x-2">
                        <input
                            type="checkbox"
                            checked={!!operatorCanEdit}
                            onChange={(e) => setOperatorCanEdit(e.target.checked)}
                        />
                        <span>Permitir que el operario agregue/edite subproductos luego</span>
                    </label>
                </div>
            )}
        </div>
    );
};

Step1Form.propTypes = {
    orderNumber: PropTypes.string.isRequired,
    setOrderNumber: PropTypes.func.isRequired,
    customer: PropTypes.string.isRequired,
    setCustomer: PropTypes.func.isRequired,
    productId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    codeInput: PropTypes.string.isRequired,
    setCodeInput: PropTypes.func.isRequired,
    onSearchByCode: PropTypes.func.isRequired,
    loadingProducts: PropTypes.bool,
    products: PropTypes.array,
    selectedProductId: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    setSelectedProductId: PropTypes.func.isRequired,
    userDisplayName: PropTypes.string,
    assignedTo: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
    setAssignedTo: PropTypes.func.isRequired,
    users: PropTypes.array.isRequired,
    loadingUsers: PropTypes.bool,
    operatorCanEdit: PropTypes.bool,
    setOperatorCanEdit: PropTypes.func.isRequired,
    showOperatorToggle: PropTypes.bool,
    quantityToCut: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    setQuantityToCut: PropTypes.func.isRequired,
    showAssigneeWarning: PropTypes.bool,
};

export default Step1Form;
