// src/components/kanban/KanbanCard.jsx
import React from "react";
import PropTypes from "prop-types";
import { ClockIcon, UserIcon, ScissorsIcon } from "@heroicons/react/24/outline";

// Fecha segura
const formatDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    return Number.isNaN(d.getTime()) ? "—" : d.toLocaleString("es-AR");
};

// Normaliza datos
function normalizeOrder(input) {
    if (!input || typeof input !== "object") {
        return {
            id: null,
            orderNumber: "—",
            customer: "—",
            assignedTo: "—",
            createdAt: null,
            modifiedAt: null,
            statusLabel: "Estado Desconocido",
            productName: "—",
            totalQty: 0,
            plannedQty: 0,
            rawStatus: null,
        };
    }

    const order = input;

    const hasBackendShape =
        ("workflow_status" in order && order.workflow_status !== undefined) ||
        Array.isArray(order?.items);

    // Status label
    const statusLabel = (() => {
        if (hasBackendShape) {
            const s = order?.workflow_status;
            if (s === "pending") return "Orden Asignada";
            if (s === "in_process") return "Orden en Proceso";
            if (s === "completed") return "Orden Completada";
            return "Estado Desconocido";
        }
        return order?.state || "Estado Desconocido";
    })();

    // Cantidades
    const itemsQty = hasBackendShape
        ? (Array.isArray(order?.items) ? order.items : []).reduce(
            (acc, it) => acc + Number(it?.cutting_quantity || 0),
            0
        )
        : Number(order?.cutting_quantity || 0);

    const plannedQty = Number(order?.quantity_to_cut || 0);
    const displayQty = itemsQty > 0 ? itemsQty : plannedQty;

    // Producto (la API actual devuelve string)
    const productName =
        (typeof order?.product === "string" && order.product.trim()) ||
        order?.name ||
        "—";

    // Usuario asignado (string username en tu API)
    const assigned =
        typeof order?.assigned_to === "string"
            ? order.assigned_to
            : order?.assigned_to != null
                ? String(order.assigned_to)
                : "—";

    return {
        id: order?.id ?? null,
        orderNumber: order?.order_number ?? "—",
        customer: order?.customer || "—",
        assignedTo: assigned || "—",
        createdAt: order?.created_at ?? null,
        modifiedAt: order?.modified_at ?? null,
        statusLabel,
        productName,
        totalQty: displayQty, // ← lo que se muestra en la card
        plannedQty,           // ← disponible si querés mostrar objetivo
        rawStatus: hasBackendShape ? order?.workflow_status : order?.state,
    };
}

// Colores de badge según estado
const statusBadgeClasses = (raw) => {
    const s = String(raw || "").toLowerCase();
    if (s === "pending" || s.includes("asignada") || s.includes("pendiente"))
        return "bg-warning-500 text-black";
    if (s === "in_process" || s === "in process" || s.includes("proceso"))
        return "bg-primary-500 text-white";
    if (s === "completed" || s.includes("complet"))
        return "bg-success-500 text-white";
    return "bg-neutral-500 text-text.white";
};

// Próximo estado válido
const getNextStatus = (raw) => {
    const s = String(raw || "").toLowerCase();
    if (s === "pending") return "in_process";
    if (s === "in_process" || s === "in process") return "completed";
    return null;
};

export default function KanbanCard({ order, currentUser, onAdvance, advancing = false, onClick }) {
    if (!order) return null;

    const o = normalizeOrder(order);
    const badge = statusBadgeClasses(o.rawStatus);

    // Permisos: admins/staff o usuario asignado por username
    const username = currentUser?.username || "";
    const isStaff = !!currentUser?.is_staff;
    const canSeeAdvance =
        isStaff || (o.assignedTo && username && String(o.assignedTo) === String(username));

    const nextStatus = getNextStatus(o.rawStatus);

    return (
        <article
            onClick={onClick}
            title={o.productName}
            className={[
                "group cursor-pointer",
                "bg-white",
                "border border-background-200",
                "rounded-2xl p-3 shadow-sm",
                "hover:shadow-md hover:border-primary-500",
                "transition duration-200 ease-out",
                "focus:outline-none focus:ring-2 focus:ring-primary-500/50",
            ].join(" ")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
                if (onClick && (e.key === "Enter" || e.key === " ")) onClick(e);
            }}
        >
            {/* Header: estado */}
            <div className="flex items-center justify-between">
                <span
                    className={[
                        "inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium",
                        badge,
                    ].join(" ")}
                >
                    {o.statusLabel}
                </span>

                {/* Botón avanzar (solo si hay próximo estado y permisos) */}
                {canSeeAdvance && nextStatus && (
                    <button
                        type="button"
                        disabled={advancing}
                        onClick={(e) => {
                            e.stopPropagation();
                            onAdvance?.(order, nextStatus);
                        }}
                        className={[
                            "text-sm text-white px-5 py-2 rounded-md border",
                            "bg-primary-500",
                            "hover:bg-primary-600 disabled:opacity-60 disabled:cursor-not-allowed",
                            "transition-colors",
                        ].join(" ")}
                        title={
                            advancing
                                ? "Actualizando..."
                                : o.rawStatus === "pending"
                                    ? "Mover a En Proceso"
                                    : "Marcar como Completada"
                        }
                    >
                        {advancing
                            ? "Actualizando..."
                            : o.rawStatus === "pending"
                                ? "Iniciar"
                                : "Completar"}
                    </button>
                )}
            </div>

            {/* Producto */}
            <h3 className="mt-2 text-sm font-bold text-text.primary line-clamp-1">
                {o.productName}
            </h3>

            {/* Cliente */}
            <p className="text-xs mt-1">
                <span className="text-text.secondary/80">Cliente: </span>
                <span className="font-bold text-text.primary">{o.customer}</span>
            </p>

            {/* Cantidad y Pedido */}
            <div className="mt-2 grid grid-cols-2 gap-2">
                <div className="flex items-center gap-2 text-xs text-text.secondary/80">
                    <ScissorsIcon className="w-4 h-4 text-secondary-500" />
                    <span className="font-bold text-xl text-text.primary">{o.totalQty} mts</span>
                </div>
                <div className="text-xs text-text.secondary/80 text-right">
                    <span className="font-bold text-text.primary">Pedido N° {o.orderNumber}</span>
                </div>
            </div>

            {/* Asignado a */}
            <div className="mt-2 flex items-center gap-2 text-xs text-text.secondary/80">
                <UserIcon className="w-4 h-4 text-secondary-500" />
                <span className="font-medium text-text.primary">{o.assignedTo}</span>
            </div>

            {/* Footer: fecha y hora */}
            <footer className="mt-2 text-[11px] text-neutral-500 flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                {formatDate(o.createdAt || o.modifiedAt)}
            </footer>
        </article>
    );
}

KanbanCard.propTypes = {
    order: PropTypes.object,
    currentUser: PropTypes.shape({
        username: PropTypes.string,
        is_staff: PropTypes.bool,
    }),
    onAdvance: PropTypes.func,
    advancing: PropTypes.bool,
    onClick: PropTypes.func,
};
