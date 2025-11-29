import React, { useState, useEffect, useCallback } from "react";
import PropTypes from "prop-types";
import Modal from "@/components/ui/Modal";
import FormInput from "@/components/ui/form/FormInput";
import FormSelect from "@/components/ui/form/FormSelect";
import ErrorMessage from "@/components/common/ErrorMessage";
import SuccessMessage from "@/components/common/SuccessMessage";

// ✅ sólo para subir archivos desde el modal
import { useUploadSubproductFiles } from "@/features/product/hooks/useSubproductFileHooks";

const locationOptions = [
    { value: "Deposito Principal", label: "Depósito Principal" },
    { value: "Deposito Secundario", label: "Depósito Secundario" },
];

const formTypeOptions = [
    { value: "Bobina", label: "Bobina" },
    { value: "Rollo", label: "Rollo" },
];

const VALID_LOCATIONS = new Set(locationOptions.map((o) => o.value));
const VALID_FORM_TYPES = new Set(formTypeOptions.map((o) => o.value));

const initialState = {
    brand: "",
    number_coil: "",
    initial_enumeration: "",
    final_enumeration: "",
    gross_weight: "",
    net_weight: "",
    initial_stock_quantity: "",
    location: "Deposito Principal",
    form_type: "Bobina",
    observations: "",
    images: [],
};

const CreateSubproductModal = ({ product, isOpen, onClose, onCreateSubproduct }) => {
    const [formData, setFormData] = useState(initialState);
    const [previewFiles, setPreviewFiles] = useState([]);
    const [error, setError] = useState("");
    const [showSuccess, setShowSuccess] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // subida de archivos (opcional)
    const uploadMut = useUploadSubproductFiles();
    const { reset: resetUpload } = uploadMut;

    useEffect(() => {
        if (!isOpen) return;
        setFormData(initialState);
        setPreviewFiles([]);
        setError("");
        setShowSuccess(false);
        setIsSubmitting(false);
        resetUpload();
    }, [isOpen, resetUpload]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files);
        if (formData.images.length + files.length > 5) {
            setError("Máximo 5 archivos permitidos.");
            return;
        }
        setFormData((prev) => ({ ...prev, images: [...prev.images, ...files] }));
        setPreviewFiles((prev) => [...prev, ...files.map((f) => f.name)]);
    };

    const removeFile = (idx) => {
        setFormData((prev) => ({
            ...prev,
            images: prev.images.filter((_, i) => i !== idx),
        }));
        setPreviewFiles((prev) => prev.filter((_, i) => i !== idx));
    };

    // helpers
    const isEmpty = (v) => v == null || String(v).trim() === "";
    const toNum = (v) => {
        const n = parseFloat(String(v).replace(",", "."));
        return Number.isNaN(n) ? null : n;
    };

    const handleSubmit = useCallback(
        async (e) => {
            e.preventDefault();
            if (isSubmitting) return; // evita doble submit
            setIsSubmitting(true);
            setError("");
            setShowSuccess(false);

            try {
                // validaciones
                const nc = String(formData.number_coil || "").trim();
                if (nc && nc.length > 50) {
                    throw new Error("El número de bobina no puede superar 50 caracteres.");
                }

                if (!isEmpty(formData.initial_enumeration) && !isEmpty(formData.final_enumeration)) {
                    const ini = toNum(formData.initial_enumeration);
                    const fin = toNum(formData.final_enumeration);
                    if (ini == null || fin == null) throw new Error("Las enumeraciones deben ser números.");
                    if (fin < ini) throw new Error("La enumeración final debe ser mayor o igual a la inicial.");
                }
                if (!isEmpty(formData.gross_weight) && !isEmpty(formData.net_weight)) {
                    const g = toNum(formData.gross_weight);
                    const n = toNum(formData.net_weight);
                    if (g == null || n == null) throw new Error("Los pesos deben ser números.");
                    if (n > g) throw new Error("El peso neto no puede ser mayor que el peso bruto.");
                }
                const qtyStr = String(formData.initial_stock_quantity || "").trim();
                if (qtyStr === "") throw new Error("El stock inicial es obligatorio y debe ser mayor a 0.");
                const q = toNum(qtyStr);
                if (q == null || q <= 0) throw new Error("El stock inicial debe ser un número mayor a 0.");

                if (!VALID_FORM_TYPES.has(formData.form_type)) throw new Error("Tipo de forma inválido.");
                if (!VALID_LOCATIONS.has(formData.location)) throw new Error("Ubicación inválida.");

                // armar FormData → el modal NO postea archivos acá
                const fd = new FormData();
                Object.entries(formData).forEach(([key, val]) => {
                    if (key === "images") return; // se suben aparte
                    if (val === "" || val == null) return;
                    // ⚠️ number_coil es string (trim). Números siguen normalizando coma->punto.
                    const normalized =
                        key === "number_coil"
                            ? String(val).trim()
                            : (typeof val === "string" ? val.replace(",", ".").trim() : val);
                    fd.append(key, normalized);
                });

                // pedir al padre que cree y devuelva el creado
                const created = await onCreateSubproduct?.(fd);

                // subir archivos (no bloquea el cierre si falla)
                if (created?.id && formData.images.length) {
                    try {
                        await uploadMut.mutateAsync({
                            productId: product.id,
                            subproductId: created.id,
                            files: formData.images,
                        });
                    } catch (e) {
                        console.warn("Upload de archivos falló:", e?.message || e);
                    }
                }

                setShowSuccess(true);
                onClose();
            } catch (err) {
                setError(err.message || "No se pudo crear el subproducto.");
            } finally {
                setIsSubmitting(false);
            }
        },
        [isSubmitting, formData, onCreateSubproduct, uploadMut, product?.id, onClose]
    );

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Crear Subproducto">
            <form onSubmit={handleSubmit} className="space-y-4">
                {error && <ErrorMessage message={error} onClose={() => setError("")} />}
                {showSuccess && (
                    <div className="fixed top-20 right-5 z-[10000]">
                        <SuccessMessage message="¡Subproducto creado con éxito!" />
                    </div>
                )}

                <FormSelect
                    label="Tipo de Forma"
                    name="form_type"
                    value={formData.form_type}
                    onChange={handleChange}
                    options={formTypeOptions}
                    required
                />

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormInput label="Marca" name="brand" value={formData.brand} onChange={handleChange} />
                    <FormInput
                        label="Número de Bobina"
                        name="number_coil"
                        value={formData.number_coil}
                        onChange={handleChange}
                        placeholder="ej: 1843-001"
                        maxLength={50}
                    />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormInput
                        label="Enumeración Inicial"
                        name="initial_enumeration"
                        value={formData.initial_enumeration}
                        onChange={handleChange}
                        type="number"
                        step="0.01"
                        min="0"
                    />
                    <FormInput
                        label="Enumeración Final"
                        name="final_enumeration"
                        value={formData.final_enumeration}
                        onChange={handleChange}
                        type="number"
                        step="0.01"
                        min="0"
                    />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormInput
                        label="Peso Bruto (kg)"
                        name="gross_weight"
                        value={formData.gross_weight}
                        onChange={handleChange}
                        type="number"
                        step="0.01"
                        min="0"
                    />
                    <FormInput
                        label="Peso Neto (kg)"
                        name="net_weight"
                        value={formData.net_weight}
                        onChange={handleChange}
                        type="number"
                        step="0.01"
                        min="0"
                    />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <FormInput
                        label="Stock Inicial"
                        name="initial_stock_quantity"
                        value={formData.initial_stock_quantity}
                        onChange={handleChange}
                        type="number"
                        step="0.01"
                        min="0.01"
                        required
                    />
                    <FormSelect
                        label="Ubicación"
                        name="location"
                        value={formData.location}
                        onChange={handleChange}
                        options={locationOptions}
                        required
                    />
                </div>

                <FormInput
                    label="Observaciones"
                    name="observations"
                    value={formData.observations}
                    onChange={handleChange}
                    textarea
                />

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

                <div className="flex justify-end space-x-2 mt-4">
                    <button
                        type="button"
                        onClick={onClose}
                        disabled={isSubmitting || uploadMut.isLoading}
                        className="bg-neutral-500 text-white py-2 px-4 rounded hover:bg-neutral-600"
                    >
                        Cancelar
                    </button>
                    <button
                        type="submit"
                        disabled={isSubmitting || uploadMut.isLoading}
                        className={`bg-primary-500 text-white py-2 px-4 rounded hover:bg-primary-600 ${isSubmitting || uploadMut.isLoading ? "opacity-50 cursor-not-allowed" : ""
                            }`}
                    >
                        {isSubmitting || uploadMut.isLoading ? "Guardando..." : "Crear Subproducto"}
                    </button>
                </div>
            </form>
        </Modal>
    );
};

CreateSubproductModal.propTypes = {
    product: PropTypes.shape({ id: PropTypes.number.isRequired }).isRequired,
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onCreateSubproduct: PropTypes.func.isRequired,
};

export default CreateSubproductModal;
