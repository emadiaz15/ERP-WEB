import React, { useMemo, useRef, useEffect } from "react";
import { PencilIcon, TrashIcon, EyeIcon } from "@heroicons/react/24/outline";

/** Fila-sentinela que dispara onLoadMore cuando entra en el viewport del contenedor scrolleable */
const SentinelRow = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,                     // HTMLElement del contenedor con overflow (scrollRef.current)
    colSpan = 100,
    rootMargin = "160px",     // precarga antes de tocar fondo
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

const CategoryTable = ({
    categories,
    openViewModal,
    openEditModal,
    openDeleteConfirmModal,

    // 👇 Props para infinite scroll
    onLoadMore,
    hasNextPage,
    isFetchingNextPage,
}) => {
    const headers = useMemo(() => ["Nombre", "Descripción", "Acciones"], []);

    const rows = useMemo(
        () =>
            categories.map((category) => ({
                Nombre: category.name || "N/A",
                Descripción: category.description || "N/A",
                Acciones: (
                    <div className="flex space-x-2">
                        <button
                            onClick={() => openViewModal(category)}
                            className="bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors"
                            aria-label={`Ver detalles de la categoría ${category.name}`}
                            title="Ver detalles"
                        >
                            <EyeIcon className="w-5 h-5 text-white" />
                        </button>
                        <button
                            onClick={() => openEditModal(category)}
                            className="bg-primary-500 p-2 rounded hover:bg-primary-600 transition-colors"
                            aria-label={`Editar la categoría ${category.name}`}
                            title="Editar"
                        >
                            <PencilIcon className="w-5 h-5 text-white" />
                        </button>
                        <button
                            onClick={() => openDeleteConfirmModal(category)}
                            className="bg-red-500 p-2 rounded hover:bg-red-600 transition-colors"
                            aria-label={`Eliminar la categoría ${category.name}`}
                            title="Eliminar"
                        >
                            <TrashIcon className="w-5 h-5 text-white" />
                        </button>
                    </div>
                ),
            })),
        [categories, openViewModal, openEditModal, openDeleteConfirmModal]
    );

    // contenedor scrolleable de la tabla
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
                            <tr
                                key={idx}
                                className={`border-b transition-all hover:bg-primary-100 ${idx % 2 === 0 ? "bg-background-100" : "bg-background-200"}`}
                            >
                                {headers.map((h) => (
                                    <td key={h} className="px-6 py-3">
                                        {row[h]}
                                    </td>
                                ))}
                            </tr>
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

export default CategoryTable;
