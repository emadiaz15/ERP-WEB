// src/features/product/components/ProductTable.jsx
import React, { useMemo, useRef, useEffect, memo } from "react";
import {
    PencilIcon,
    EyeIcon,
    TrashIcon,
    FolderIcon,
    ClockIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "@/context/AuthProvider";

/** Fila-sentinela que dispara onLoadMore cuando entra en el viewport del contenedor scrolleable */
const SentinelRow = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,                 // HTMLElement del contenedor con overflow (scrollRef.current)
    colSpan = 100,
    rootMargin = "160px", // precarga antes de tocar fondo
    className = "",
}) => {
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el || disabled) return;

        const io = new IntersectionObserver(
            (entries) => {
                const [entry] = entries;
                if (entry.isIntersecting && !isLoadingMore) onLoadMore();
            },
            { root, rootMargin, threshold: 0 }
        );

        io.observe(el);
        return () => {
            try { io.unobserve(el); } catch { }
            io.disconnect();
        };
    }, [onLoadMore, disabled, isLoadingMore, root, rootMargin]);

    return (
        <tr ref={ref} className={className} aria-live="polite" aria-busy={isLoadingMore || undefined}>
            <td colSpan={colSpan} className="py-4 text-center text-sm text-muted-foreground">
                {disabled ? "No hay más resultados" : isLoadingMore ? "Cargando más..." : "Desplázate para cargar más"}
            </td>
        </tr>
    );
};

const ProductRow = memo(function ProductRow({ row, headers, idx }) {
    return (
        <tr
            className={`border-b transition-all hover:bg-primary-100 ${idx % 2 === 0 ? "bg-background-100" : "bg-background-200"}`}
        >
            {headers.map((h) => (
                <td key={h} className="px-6 py-3">
                    {row[h]}
                </td>
            ))}
        </tr>
    );
}, (prev, next) => {
    // los headers son constantes; compara referencias del contenido visible
    if (prev.idx !== next.idx) return false;
    const H = prev.headers;
    for (let i = 0; i < H.length; i++) {
        const k = H[i];
        if (prev.row[k] !== next.row[k]) return false;
    }
    return true;
});

const ProductTable = ({
    products = [],
    onView,
    onEdit,
    onDelete,
    onShowSubproducts,
    onViewStockHistory,
    // Props para infinite scroll:
    onLoadMore,
    hasNextPage,
    isFetchingNextPage,
}) => {
    const { user } = useAuth();
    const isStaff = !!user?.is_staff;

    const headers = useMemo(
        () => ["Código", "Artículo", "Stock", "Marca", "Categoría", "Acciones"],
        []
    );

    const rows = useMemo(
        () =>
            products.map((p) => ({
                "Código": <div className="w-[90px] truncate">{p.code ?? "N/A"}</div>,
                "Artículo": (
                    <div className="min-w-[300px] max-w-[400px] truncate">
                        {p.type_name ? `${p.type_name} – ${p.name ?? "Sin nombre"}` : p.name ?? "Sin nombre"}
                    </div>
                ),
                "Stock": <div className="w-[80px] truncate">{p.current_stock ?? 0}</div>,
                "Marca": <div className="w-[120px] truncate">{p.brand ?? ""}</div>,
                "Categoría": <div className="w-[140px] truncate">{p.category_name ?? ""}</div>,
                "Acciones": (
                    <div className="flex space-x-2 min-w-[220px]">
                        {/* Ver detalles */}
                        <button
                            onClick={() => onView(p)}
                            className="bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors"
                            aria-label="Ver detalles"
                            title="Ver detalles"
                        >
                            <EyeIcon className="w-5 h-5 text-white" />
                        </button>

                        {/* Ver subproductos (si corresponde) */}
                        {p.has_subproducts && (
                            <button
                                onClick={() => onShowSubproducts?.(p)}
                                className="bg-indigo-500 p-2 rounded hover:bg-indigo-600 transition-colors"
                                aria-label="Ver subproductos"
                                title="Ver subproductos"
                            >
                                <FolderIcon className="w-5 h-5 text-white" />
                            </button>
                        )}

                        {/* Historial de stock de producto */}
                        <button
                            onClick={() => onViewStockHistory?.(p)}
                            className="bg-amber-500 p-2 rounded hover:bg-amber-600 transition-colors"
                            aria-label="Historial de stock"
                            title="Historial de stock"
                        >
                            <ClockIcon className="w-5 h-5 text-white" />
                        </button>

                        {/* Edición / Eliminación (solo staff) */}
                        {isStaff && (
                            <>
                                <button
                                    onClick={() => onEdit(p)}
                                    className="bg-primary-500 p-2 rounded hover:bg-primary-600 transition-colors"
                                    aria-label="Editar producto"
                                    title="Editar"
                                >
                                    <PencilIcon className="w-5 h-5 text-white" />
                                </button>
                                <button
                                    onClick={() => onDelete(p)}
                                    className="bg-red-500 p-2 rounded hover:bg-red-600 transition-colors"
                                    aria-label="Eliminar producto"
                                    title="Eliminar"
                                >
                                    <TrashIcon className="w-5 h-5 text-white" />
                                </button>
                            </>
                        )}
                    </div>
                ),
            })),
        [products, isStaff, onView, onEdit, onDelete, onShowSubproducts, onViewStockHistory]);

    // contenedor scrolleable de la tabla (mismo pattern que CategoryTable)
    const scrollRef = useRef(null);

    return (
        <div className="relative overflow-x-auto shadow-md sm:rounded-lg mt-2">
            {/* Solo scrollea la tabla */}
            <div ref={scrollRef} className="max-h-[480px] overflow-y-auto">
                <table className="w-full text-sm text-left text-text-primary">
                    <thead className="sticky top-0 z-10 text-xs text-white uppercase bg-primary-500">
                        <tr>
                            {headers.map((h) => (
                                <th key={h} className="px-6 py-3">{h}</th>
                            ))}
                        </tr>
                    </thead>

                    <tbody>
                        {rows.map((row, idx) => (
                            <ProductRow key={idx} row={row} headers={headers} idx={idx} />
                        ))}

                        {/* Sentinel para infinite scroll, última fila */}
                        <SentinelRow
                            onLoadMore={onLoadMore}
                            disabled={!hasNextPage}
                            isLoadingMore={isFetchingNextPage}
                            root={scrollRef.current}
                            colSpan={headers.length}
                        />
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default ProductTable;
