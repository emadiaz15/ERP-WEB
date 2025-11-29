// src/features/user/components/UserTable.jsx
import React, { useMemo, useRef, useEffect } from "react";
import { PencilIcon, TrashIcon, EyeIcon } from "@heroicons/react/24/outline";

/** Fila-sentinela que dispara onLoadMore cuando entra en el viewport del contenedor scrolleable */
const SentinelRow = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,                     // HTMLElement del contenedor con overflow (scrollRef.current)
    colSpan = 100,
    rootMargin = "160px",     // precarga un poco antes de tocar fondo
    className = "",
}) => {
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el || disabled) return;

        const io = new IntersectionObserver(
            (entries) => {
                const [entry] = entries;
                if (entry.isIntersecting && !isLoadingMore) {
                    onLoadMore();
                }
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
                {disabled
                    ? "No hay más resultados"
                    : isLoadingMore
                        ? "Cargando más..."
                        : "Desplázate para cargar más"}
            </td>
        </tr>
    );
};

const UserTable = ({
    users,
    openViewModal,
    openEditModal,
    openDeleteConfirmModal,

    /** Props para infinite scroll */
    onLoadMore,          // => fetchNextPage()
    hasNextPage,         // boolean
    isFetchingNextPage,  // boolean
}) => {
    const tableHeaders = useMemo(
        () => ["Usuario", "Nombre Completo", "Email", "DNI", "Rol", "Acciones"],
        []
    );

    const tableRows = useMemo(
        () =>
            users.map((user) => {
                // corregir esquema en local: forzar HTTP si viene con HTTPS
                const rawImageUrl = user.image_signed_url || user.image_url;
                const imageUrl = rawImageUrl?.startsWith("https://localhost:9000")
                    ? rawImageUrl.replace(/^https:\/\//, "http://")
                    : rawImageUrl;

                return {
                    "Usuario": (
                        <div className="flex items-center space-x-3">
                            {imageUrl ? (
                                <img
                                    src={imageUrl}
                                    alt={`Avatar de ${user.username ?? "usuario"}`}
                                    className="w-8 h-8 rounded-full object-cover"
                                    loading="lazy"
                                    referrerPolicy="no-referrer"
                                />
                            ) : (
                                <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-sm text-white font-bold uppercase">
                                    {user.username?.[0] || "U"}
                                </div>
                            )}
                            <span>{user.username || "N/A"}</span>
                        </div>
                    ),
                    "Nombre Completo": `${user.name || ""} ${user.last_name || ""}`.trim() || "N/A",
                    "Email": user.email || "N/A",
                    "DNI": user.dni || "N/A",
                    "Rol": user.is_staff ? "Administrador" : "Operario",
                    "Acciones": (
                        <div className="flex space-x-2 justify-center">
                            <button
                                onClick={() => openViewModal(user)}
                                className="bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors"
                                aria-label="Ver usuario"
                                title="Ver Detalles"
                            >
                                <EyeIcon className="w-5 h-5 text-white" />
                            </button>
                            <button
                                onClick={() => openEditModal(user)}
                                className="bg-primary-500 p-2 rounded hover:bg-primary-600 transition-colors"
                                aria-label="Editar usuario"
                                title="Editar Usuario"
                            >
                                <PencilIcon className="w-5 h-5 text-white" />
                            </button>
                            <button
                                onClick={() => openDeleteConfirmModal(user)}
                                className="bg-red-500 p-2 rounded hover:bg-red-600 transition-colors"
                                aria-label="Eliminar usuario"
                                title="Desactivar Usuario"
                            >
                                <TrashIcon className="w-5 h-5 text-white" />
                            </button>
                        </div>
                    ),
                };
            }),
        [users, openViewModal, openEditModal, openDeleteConfirmModal]
    );

    /** Contenedor scrolleable de la tabla (root del IntersectionObserver) */
    const scrollRef = useRef(null);

    return (
        <div className="relative overflow-x-auto shadow-md sm:rounded-lg mt-4">
            {/* 👇 Solo scrollea la tabla */}
            <div ref={scrollRef} className="max-h-[480px] overflow-y-auto">
                <table className="w-full text-sm text-left text-text-primary">
                    <thead className="sticky top-0 z-10 text-xs text-white uppercase bg-primary-500">
                        <tr>
                            {tableHeaders.map((header, index) => (
                                <th key={index} className="px-6 py-3">{header}</th>
                            ))}
                        </tr>
                    </thead>

                    <tbody>
                        {tableRows.map((row, index) => (
                            <tr
                                key={index}
                                className={`border-b transition-all hover:bg-primary-100 ${index % 2 === 0 ? "bg-background-100" : "bg-background-200"}`}
                            >
                                {tableHeaders.map((header, i) => (
                                    <td key={i} className="px-6 py-3 text-text-primary">
                                        {row[header]}
                                    </td>
                                ))}
                            </tr>
                        ))}

                        {/* Sentinel para infinite scroll, como última fila del tbody */}
                        <SentinelRow
                            onLoadMore={onLoadMore}
                            disabled={!hasNextPage}
                            isLoadingMore={isFetchingNextPage}
                            root={scrollRef.current}
                            colSpan={tableHeaders.length}
                        />
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UserTable;
