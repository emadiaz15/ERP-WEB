import React, { useState, useEffect } from "react"
import PropTypes from "prop-types"

import Modal from "@/components/ui/Modal"
import FormInput from "@/components/ui/form/FormInput"
import FormSelect from "@/components/ui/form/FormSelect"
import ErrorMessage from "@/components/common/ErrorMessage"
import SuccessMessage from "@/components/common/SuccessMessage"
import DeleteMessage from "@/components/common/DeleteMessage"

import ProductCarouselOverlay from "@/features/product/components/ProductCarouselOverlay"

import { useUpdateSubproduct } from "@/features/product/hooks/useSubproductHooks"
import {
    useUploadSubproductFiles,
    useDeleteSubproductFile,
} from "@/features/product/hooks/useSubproductFileHooks"

const locationOptions = [
    { value: "Deposito Principal", label: "Depósito Principal" },
    { value: "Deposito Secundario", label: "Depósito Secundario" },
]

const formTypeOptions = [
    { value: "Bobina", label: "Bobina" },
    { value: "Rollo", label: "Rollo" },
]

// 🔄 Sin campo de stock: la edición de stock se hace en StockHistory
const initialState = {
    brand: "",
    number_coil: "",
    initial_enumeration: "",
    final_enumeration: "",
    gross_weight: "",
    net_weight: "",
    location: "Deposito Principal",
    form_type: "Bobina",
    observations: "",
    images: [],
}

export default function EditSubproductModal({
    isOpen,
    onClose,
    onSave,
    subproduct,
    children,
    loading = false,
}) {
    const [formData, setFormData] = useState(initialState)
    const [previewFiles, setPreviewFiles] = useState([])
    const [error, setError] = useState("")
    const [showSuccess, setShowSuccess] = useState(false)
    const [fileToDelete, setFileToDelete] = useState(null)
    const [isDeleteOpen, setIsDeleteOpen] = useState(false)

    // IDs del contexto actual
    const productId = subproduct?.parent
    const subproductId = subproduct?.id

    // Hooks
    const updateMut = useUpdateSubproduct(productId)
    const {
        mutateAsync: uploadFiles,
        isLoading: uploading,
        error: uploadError,
        reset: clearUploadError,
    } = useUploadSubproductFiles()
    const {
        mutateAsync: deleteFile,
        isLoading: deleting,
        error: deleteError,
    } = useDeleteSubproductFile()

    // Inyectar handler de borrado en el carousel si corresponde
    const childrenWithProps = React.Children.map(children, (child) =>
        React.isValidElement(child) && child.type === ProductCarouselOverlay
            ? React.cloneElement(child, {
                onDeleteRequest: (file) => {
                    setFileToDelete(file)
                    setIsDeleteOpen(true)
                },
            })
            : child
    )

    // Inicializar formulario al abrir
    useEffect(() => {
        if (!isOpen || !subproduct) return
        clearUploadError()
        setError("")
        setShowSuccess(false)
        setPreviewFiles([])
        setFormData({
            brand: subproduct.brand || "",
            number_coil: subproduct.number_coil || "",
            initial_enumeration: subproduct.initial_enumeration || "",
            final_enumeration: subproduct.final_enumeration || "",
            gross_weight: subproduct.gross_weight || "",
            net_weight: subproduct.net_weight || "",
            location: subproduct.location || "Deposito Principal",
            form_type: subproduct.form_type || "Bobina",
            observations: subproduct.observations || "",
            images: [],
        })
    }, [isOpen, subproduct, clearUploadError])

    // Handlers
    const handleChange = (e) => {
        const { name, type, value, checked } = e.target
        setFormData((f) => ({
            ...f,
            [name]: type === "checkbox" ? checked : value,
        }))
    }

    const handleFileChange = (e) => {
        const files = Array.from(e.target.files || [])
        if (!files.length) return
        if (formData.images.length + files.length > 5) {
            setError("Máximo 5 archivos permitidos.")
            return
        }
        setFormData((f) => ({ ...f, images: [...f.images, ...files] }))
        setPreviewFiles((p) => [...p, ...files.map((f) => f.name)])
    }

    const removeFile = (idx) => {
        setFormData((f) => ({
            ...f,
            images: f.images.filter((_, i) => i !== idx),
        }))
        setPreviewFiles((p) => p.filter((_, i) => i !== idx))
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setError("")

        if (!productId || !subproductId) {
            setError("Faltan identificadores de producto o subproducto.")
            return
        }

        // Armar FormData (sin los archivos)
        const fd = new FormData()
        Object.entries(formData).forEach(([key, val]) => {
            if (key === "images" || val == null || val === "") return
            if (key === "number_coil") {
                const s = String(val).trim()
                if (s.length > 50) {
                    setError("El número de bobina no puede superar 50 caracteres.")
                    return
                }
                fd.append(key, s)
            } else {
                fd.append(key, val)
            }
        })

        try {
            // 1) Actualizar subproducto
            const updated = await updateMut.mutateAsync({
                subproductId,
                formData: fd,
            })

            // 2) Subir archivos (si hay)
            if (formData.images.length) {
                await uploadFiles({
                    productId,
                    subproductId,
                    files: formData.images,
                })
            }

            setShowSuccess(true)
            onSave?.(updated)
            // Cerrar inmediatamente; el toast se auto-cierra
            onClose()
        } catch (err) {
            setError(err?.message || "No se pudo actualizar el subproducto.")
        }
    }

    const confirmDelete = async () => {
        if (!fileToDelete || !productId || !subproductId) return
        try {
            await deleteFile({
                productId,
                subproductId,
                fileId: fileToDelete.id ?? fileToDelete.key,
            })
            setIsDeleteOpen(false)
            onSave?.(subproduct)
        } catch {
            // DeleteMessage ya muestra deleteError
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Editar Subproducto" maxWidth="max-w-6xl" loading={loading}>
            <div className="flex flex-col md:flex-row gap-4 h-full">
                <div className="flex-1 p-4 bg-background-100 rounded overflow-y-auto max-h-[80vh]">
                    <form onSubmit={handleSubmit} className="space-y-4">
                        {error && <ErrorMessage message={error} onClose={() => setError("")} />}
                        {uploadError && (
                            <ErrorMessage message={uploadError.message} onClose={clearUploadError} />
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
                            <FormInput label="Enumeración Inicial" name="initial_enumeration" value={formData.initial_enumeration} onChange={handleChange} />
                            <FormInput label="Enumeración Final" name="final_enumeration" value={formData.final_enumeration} onChange={handleChange} />
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <FormInput label="Peso Bruto (kg)" name="gross_weight" value={formData.gross_weight} onChange={handleChange} />
                            <FormInput label="Peso Neto (kg)" name="net_weight" value={formData.net_weight} onChange={handleChange} />
                        </div>

                        {/* Sin "Stock Inicial": se edita desde StockHistory */}
                        <FormSelect
                            label="Ubicación"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            options={locationOptions}
                            required
                        />

                        <FormInput
                            label="Observaciones"
                            name="observations"
                            value={formData.observations}
                            onChange={handleChange}
                            textarea
                        />

                        {/* Archivos */}
                        <div>
                            <label className="block mb-2 text-sm font-medium">Archivos (máx. 5)</label>
                            <div className="flex items-center space-x-4">
                                <label htmlFor="images" className="cursor-pointer bg-info-500 text-white px-4 py-2 rounded hover:bg-info-600">
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
                                disabled={uploading || updateMut.isLoading}
                                className="bg-neutral-500 text-white px-4 py-2 rounded hover:bg-neutral-600"
                            >
                                Cancelar
                            </button>
                            <button
                                type="submit"
                                disabled={uploading || updateMut.isLoading}
                                className="bg-primary-500 text-white px-4 py-2 rounded hover:bg-primary-600"
                            >
                                {(uploading || updateMut.isLoading) ? "Guardando..." : "Actualizar Subproducto"}
                            </button>
                        </div>

                        {showSuccess && (
                            <div className="fixed top-20 right-5 z-[10000]">
                                <SuccessMessage
                                    message="¡Subproducto actualizado con éxito!"
                                    onClose={() => setShowSuccess(false)}
                                />
                            </div>
                        )}
                    </form>
                </div>

                {childrenWithProps && (
                    <div className="flex-1 p-4 bg-background-50 rounded overflow-y-auto max-h-[80vh]">
                        {childrenWithProps}
                    </div>
                )}
            </div>

            <DeleteMessage
                isOpen={isDeleteOpen}
                onClose={() => setIsDeleteOpen(false)}
                onDelete={confirmDelete}
                isDeleting={deleting}
                deleteError={deleteError}
                itemName="el archivo"
                itemIdentifier={fileToDelete?.name || fileToDelete?.key || ""}
            />
        </Modal>
    )
}

EditSubproductModal.propTypes = {
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    onSave: PropTypes.func,
    subproduct: PropTypes.shape({
        id: PropTypes.number.isRequired,
        parent: PropTypes.number.isRequired,
    }).isRequired,
    children: PropTypes.node,
    loading: PropTypes.bool,
}
