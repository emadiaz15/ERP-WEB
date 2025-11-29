// src/features/product/components/ViewProductModal.jsx
import React, { useEffect } from "react";
import PropTypes from "prop-types";

import Modal from "@/components/ui/Modal";
import { usePrefetchedData } from "@/context/DataPrefetchContext";
import { useProductFilesData } from "@/features/product/hooks/useProductFileHooks";
import ProductCarouselOverlay from "@/features/product/components/ProductCarouselOverlay";
import { useQueryClient } from "@tanstack/react-query";
import { productKeys } from "@/features/product/utils/queryKeys";

const ViewProductModal = ({ product, isOpen, onClose }) => {
    const { categories } = usePrefetchedData();
    const productId = isOpen ? product?.id : null;
    const qc = useQueryClient();

    // 🔄 Refetch al abrir, con DEDUPE por producto para evitar spam de /files/
    useEffect(() => {
        if (!isOpen || !productId) return;
        const WS_DEBUG = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_WS_DEBUG === 'true');
        // Mapa global en window para dedupe entre montajes rápidos del modal
        const map = (typeof window !== 'undefined') ? (window.__filesInvalidateMap ||= new Map()) : new Map();
        const now = Date.now();
        const last = map.get(productId) || 0;
        const TTL = 60_000; // 60s: si se abrió de nuevo en menos de 1 min, no re-fetch
        if (now - last < TTL) {
            if (WS_DEBUG) console.log(`[ViewProductModal] Skip files invalidate for #${productId} (dedup ${now - last}ms < ${TTL}ms)`);
            return;
        }
        const t = setTimeout(() => {
            if (WS_DEBUG) console.log(`[ViewProductModal] Invalidate files for product #${productId}`);
            qc.invalidateQueries(productKeys.files(productId));
            map.set(productId, Date.now());
        }, 100);
        return () => clearTimeout(t);
    }, [isOpen, productId, qc]);

    const {
        files = [],
        isLoading: loadingFiles,
        error: filesError,
    } = useProductFilesData(productId);

    if (!product) return null;

    const categoryName =
        categories.find((c) => c.id === product.category)?.name ||
        product.category_name ||
        "N/A";

    // Eliminado: types y typeName

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Detalles del Producto"
            maxWidth="max-w-6xl"
            loading={loadingFiles}
        >
            {/* Contenedor vertical: cuerpo (grid) + footer fijo con botón */}
            <div className="flex flex-col gap-4 max-h-[80vh]">
                {/* Cuerpo con dos paneles scrolleables */}
                <div className="grid md:grid-cols-2 gap-4 min-h-0 flex-1">
                    {/* — Detalles */}
                    <div className="flex-1 space-y-2 bg-background-100 p-4 rounded overflow-y-auto">
                        <p>
                            <strong>Código:</strong> {product.code ?? "N/A"}
                        </p>
                        <p>
                            <strong>Nombre/Medida:</strong> {product.name || "SIN NOMBRE"}
                        </p>
                        <p>
                            <strong>Descripción:</strong> {product.description || "SIN DESCRIPCIÓN"}
                        </p>
                        <p>
                            <strong>Marca:</strong> {product.brand || "N/A"}
                        </p>
                        <p>
                            <strong>Ubicación:</strong> {product.location || "N/A"}
                        </p>
                        <p>
                            <strong>Posición:</strong> {product.position || "N/A"}
                        </p>
                        <p>
                            <strong>Categoría:</strong> {categoryName}
                        </p>
                        <p>
                            <strong>ID:</strong> {product.id}
                        </p>
                    </div>

                    {/* — Carousel */}
                    <div className="flex-1 bg-background-50 p-4 rounded overflow-y-auto">
                        {filesError ? (
                            <p className="text-red-500">Error cargando archivos.</p>
                        ) : files.length > 0 ? (
                            <ProductCarouselOverlay images={files} productId={product.id} isEmbedded />
                        ) : (
                            <p className="text-center text-gray-600">No hay archivos multimedia.</p>
                        )}
                    </div>
                </div>

                {/* Footer con botón centrado SIEMPRE visible debajo del contenido */}
                <div className="pt-2 border-t border-background-200">
                    <div className="flex justify-center">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
                        >
                            Cerrar
                        </button>
                    </div>
                </div>
            </div>
        </Modal>
    );
};

ViewProductModal.propTypes = {
    product: PropTypes.shape({
        id: PropTypes.number.isRequired,
        code: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        category: PropTypes.number,
        category_name: PropTypes.string,
        type: PropTypes.number,
        type_name: PropTypes.string,
        name: PropTypes.string,
        description: PropTypes.string,
        status: PropTypes.bool,
        has_subproducts: PropTypes.bool,
        current_stock: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        brand: PropTypes.string,
        location: PropTypes.string,
        position: PropTypes.string,
        created_at: PropTypes.string,
        modified_at: PropTypes.string,
        created_by: PropTypes.string,
        modified_by: PropTypes.string,
    }).isRequired,
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
};

export default ViewProductModal;
