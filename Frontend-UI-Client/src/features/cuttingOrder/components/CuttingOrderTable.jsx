// src/features/cuttingOrder/components/CuttingOrderTable.jsx
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { EyeIcon, PencilIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useAuth } from "../../../context/AuthProvider";
import { useProducts } from "@/features/product/hooks/useProductHooks";
import { listUsers } from "@/features/user/services/listUsers";

/** Fila-sentinela que dispara onLoadMore cuando entra en el viewport del contenedor scrolleable */
const SentinelRow = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,
    colSpan = 100,
    rootMargin = "160px",
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

// ===== Helpers =====
const sumItemsQuantity = (items = []) =>
    items.reduce((acc, it) => acc + Number(it?.cutting_quantity ?? 0), 0);

const safeDate = (v) => {
    const d = new Date(v);
    return isNaN(d.getTime()) ? null : d;
};

// Fecha y hora en formato dd/mm/aaaa HH:mm (24h)
const formatDateTime = (isoLike) => {
    const d = safeDate(isoLike);
    if (!d) return "—";
    try {
        const fecha = d.toLocaleDateString('es-AR');
        const hora = d.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit', hour12: false });
        return `${fecha} ${hora}`;
    } catch {
        return d.toLocaleString();
    }
};

// Colores y etiquetas por estado
const STATUS_CONFIG = {
    pending: { color: "bg-amber-500", label: "Pendiente" },
    in_process: { color: "bg-primary-500", label: "En Proceso" },
    completed: { color: "bg-green-500", label: "Completada" },
    cancelled: { color: "bg-error-500", label: "Cancelada" },
};

const getStatusConfig = (order) => {
    const cfg = STATUS_CONFIG[order?.workflow_status];
    if (cfg) return { ...cfg, display: order?.workflow_status_display || cfg.label };
    return {
        color: "bg-gray-500",
        label: "Desconocido",
        display: order?.workflow_status_display || order?.workflow_status || "—",
    };
};

const CuttingOrderTable = ({
    orders = [],
    onView,
    onEdit,
    onDelete,
    // Infinite scroll:
    onLoadMore,
    hasNextPage = false,
    isFetchingNextPage = false,
}) => {
    const { user } = useAuth();
    const isStaff = !!user?.is_staff;

    // ORDEN: más recientes primero
    const sortedOrders = useMemo(() => {
        const arr = Array.isArray(orders) ? [...orders] : [];
        arr.sort((a, b) => {
            const ad = safeDate(a?.created_at);
            const bd = safeDate(b?.created_at);
            if (ad && bd && ad.getTime() !== bd.getTime()) return bd - ad;
            const am = safeDate(a?.modified_at);
            const bm = safeDate(b?.modified_at);
            if (am && bm && am.getTime() !== bm.getTime()) return bm - am;
            const aid = Number(a?.id ?? 0);
            const bid = Number(b?.id ?? 0);
            return bid - aid;
        });
        return arr;
    }, [orders]);

    // Mapa de productos (para mostrar nombre si llega solo el id)
    const { products } = useProducts({ status: true, page_size: 2000 });
    const productMap = useMemo(() => {
        const map = new Map();
        for (const p of products || []) map.set(p.id, p);
        return map;
    }, [products]);

    const getProductMainLabel = useCallback(
        (order) => {
            if (order?.product && typeof order.product === "object") {
                return order.product.name || order.product.description || `${order.product.id ?? "?"}`;
            }
            const prodId = order?.product ?? order?.product_id;
            const found = prodId != null ? productMap.get(Number(prodId)) : null;
            return found?.name || found?.description || `${prodId ?? "?"}`;
        },
        [productMap]
    );

    // Mapa de usuarios para "Asignado a"
    const assignedIds = useMemo(() => {
        const ids = new Set();
        for (const o of sortedOrders) {
            const id = Number(o?.assigned_to);
            if (Number.isFinite(id) && id > 0) ids.add(id);
        }
        return Array.from(ids);
    }, [sortedOrders]);

    const assignedIdsKey = useMemo(() => assignedIds.join(","), [assignedIds]);

    const [usersMap, setUsersMap] = useState(() => new Map());
    const [loadingUsers, setLoadingUsers] = useState(false);

    useEffect(() => {
        let cancelled = false;

        if (!assignedIdsKey) {
            setUsersMap(new Map());
            return;
        }

        const url = "/users/list/?status=true&page_size=2000";
        setLoadingUsers(true);
        listUsers(url)
            .then((data) => {
                if (cancelled) return;
                const map = new Map();
                const arr = data?.results || [];
                for (const u of arr) {
                    const label =
                        u.username ||
                        (u.first_name && u.last_name ? `${u.first_name} ${u.last_name}` : u.email) ||
                        `user_${u.id}`;
                    map.set(Number(u.id), { ...u, _label: label });
                }
                setUsersMap(map);
            })
            .catch(() => {
                if (cancelled) return;
                setUsersMap(new Map());
            })
            .finally(() => {
                if (!cancelled) setLoadingUsers(false);
            });

        return () => { cancelled = true; };
    }, [assignedIdsKey]);

    const getAssignedToUsername = useCallback(
        (order) => {
            // 1) Preferimos el detalle del backend (igual que created_by)
            if (order?.assigned_to_detail?.username) return order.assigned_to_detail.username;
            if (order?.assigned_to_detail) {
                const d = order.assigned_to_detail;
                const full = `${d.first_name ?? ""} ${d.last_name ?? ""}`.trim();
                if (full) return full;
                if (d.email) return d.email;
            }

            // 2) Campos “flatten” si los expone el serializer
            if (order?.assigned_to_username) return order.assigned_to_username;
            if (order?.assigned_to_display) return order.assigned_to_display;

            // 3) Si la API manda el username directamente como string
            if (typeof order?.assigned_to === "string" && order.assigned_to.trim()) {
                return order.assigned_to.trim();
            }

            // 4) Lookup local por ID
            const id = Number(order?.assigned_to_id ?? order?.assigned_to_pk ?? order?.assigned_to);
            if (Number.isFinite(id)) {
                const u = usersMap.get(id);
                if (u?.username) return u.username;
                const full = `${u?.first_name ?? ""} ${u?.last_name ?? ""}`.trim();
                if (full) return full;
                if (u?._label) return u._label;
                if (u?.email) return u.email;
                return `ID #${id}`;
            }

            return "Sin asignación";
        },
        [usersMap]
    );

    const getCreatedByLabel = (order) =>
        order?.created_by_username ||
        order?.created_by_detail?.username ||
        order?.created_by ||
        "N/A";

    const headers = useMemo(
        () => [
            "Fecha y Hora (dd/mm/aaaa HH:mm)",
            "Producto",
            "Cliente",
            "Cantidad a cortar",
            "Nro de Pedido",
            "Asignado a",
            "Creado por",
            "Estado",
            "Acciones",
        ],
        []
    );

    const rows = useMemo(
        () =>
            (sortedOrders || []).map((order) => {
                const itemsSum = sumItemsQuantity(order?.items);
                const target = order?.quantity_to_cut ?? 0;
                const statusCfg = getStatusConfig(order); // ← usamos color/label por estado

                // Mostrar siempre la fecha de creación (created_at)
                return {
                    "Fecha y Hora (dd/mm/aaaa HH:mm)": (
                        <div className="w-[150px] truncate text-xs" title={order?.created_at || ''}>
                            {formatDateTime(order?.created_at)}
                        </div>
                    ),
                    "Producto": (
                        <div className="min-w-[300px] max-w-[400px] truncate">
                            {getProductMainLabel(order)}
                        </div>
                    ),
                    "Cliente": (
                        <div className="min-w-[160px] max-w-[240px] truncate">
                            {order?.customer || "Sin cliente"}
                        </div>
                    ),
                    "Cantidad a cortar": (
                        <div
                            className="w-[80px] truncate text-right tabular-nums"
                            title={`Objetivo: ${target} | Ítems: ${itemsSum}`}
                        >
                            {target}
                        </div>
                    ),
                    "Nro de Pedido": (
                        <div className="w-[80px] truncate text-center tabular-nums">
                            {order?.order_number ?? order?.id ?? "—"}
                        </div>
                    ),
                    "Asignado a": (
                        <div className="w-[140px] truncate">
                            {getAssignedToUsername(order)}
                        </div>
                    ),
                    "Creado por": (
                        <div className="w-[140px] truncate">
                            {getCreatedByLabel(order)}
                        </div>
                    ),
                    "Estado": (
                        <div className="w-[100px] truncate">
                            <span
                                className={`inline-flex items-center gap-2 px-2 py-0.5 rounded-full text-white text-xs font-semibold ${statusCfg.color}`}
                                title={statusCfg.display}
                            >
                                <span className="inline-block w-2 h-2 rounded-full bg-white/70" />
                                {statusCfg.display || statusCfg.label}
                            </span>
                        </div>
                    ),
                    "Acciones": (
                        <div className="flex space-x-2 min-w-[220px]">
                            {/* Ver detalles: siempre visible */}
                            <button
                                onClick={() => onView?.(order)}
                                className="bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors"
                                aria-label="Ver detalles de la orden"
                                title="Ver detalles"
                            >
                                <EyeIcon className="w-5 h-5 text-white" />
                            </button>

                            {/* Editar/Cancelar: solo admin y solo si status es pending o in_process */}
                            {isStaff && ["pending", "in_process"].includes(order?.workflow_status) && (
                                <>
                                    <button
                                        onClick={() => onEdit?.(order)}
                                        className="bg-primary-500 p-2 rounded hover:bg-primary-600 transition-colors"
                                        aria-label="Editar orden"
                                        title="Editar"
                                    >
                                        <PencilIcon className="w-5 h-5 text-white" />
                                    </button>
                                    <button
                                        onClick={() => onDelete?.(order?.id)}
                                        className="bg-red-500 p-2 rounded hover:bg-red-600 transition-colors"
                                        aria-label="Cancelar orden"
                                        title="Cancelar"
                                    >
                                        <XMarkIcon className="w-5 h-5 text-white" />
                                    </button>
                                </>
                            )}
                        </div>
                    ),
                };
            }),
        [sortedOrders, isStaff, onView, onEdit, onDelete, getProductMainLabel, getAssignedToUsername]
    );

    // contenedor scrolleable (mismo pattern que ProductTable)
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

export default CuttingOrderTable;
