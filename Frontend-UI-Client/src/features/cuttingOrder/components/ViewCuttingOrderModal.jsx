// src/features/cuttingOrder/components/ViewCuttingOrderModal.jsx
import React from "react";
import PropTypes from "prop-types";
import Modal from "@/components/ui/Modal";
import SubproductMiniCard from "./SubproductMiniCard";

// Colores y etiquetas por estado
const STATUS_CONFIG = {
    pending: { color: "bg-amber-500", label: "Pendiente" },
    in_process: { color: "bg-primary-500", label: "En Proceso" },
    completed: { color: "bg-green-500", label: "Completada" },
    cancelled: { color: "bg-error-500", label: "Cancelada" },
};

const fmtDate = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d)) return String(iso);
    try {
        return new Intl.DateTimeFormat(undefined, { dateStyle: "short", timeStyle: "short" }).format(d);
    } catch {
        return d.toLocaleString();
    }
};

const fmtNum = (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return v ?? "0";
    try {
        return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(n);
    } catch {
        return String(n);
    }
};

const sumItems = (items = []) =>
    items.reduce((acc, it) => acc + Number(it?.cutting_quantity ?? 0), 0);

// 🔹 Muestra asignado a (string actual de tu API o futuros detalles/IDs)
const getAssignedToDisplay = (order) => {
    if (order?.assigned_to_detail?.username) return order.assigned_to_detail.username;
    if (order?.assigned_to_detail) {
        const d = order.assigned_to_detail;
        const full = `${d.first_name ?? ""} ${d.last_name ?? ""}`.trim();
        if (full) return full;
        if (d.email) return d.email;
    }
    if (order?.assigned_to_username) return order.assigned_to_username;
    if (order?.assigned_to_display) return order.assigned_to_display;

    if (typeof order?.assigned_to === "string" && order.assigned_to.trim()) {
        return order.assigned_to.trim(); // API actual
    }
    const id = Number(order?.assigned_to_id ?? order?.assigned_to_pk ?? order?.assigned_to);
    if (Number.isFinite(id)) return `ID #${id}`;
    return "Sin asignación";
};

// 🔹 Etiqueta de producto: soporta string (tu API actual) u objeto
const getProductLabel = (product) => {
    if (!product) return "—";
    if (typeof product === "string") return product;
    return product.name || product.description || product.code || `#${product.id ?? "—"}`;
};

/**
 * `subproductMap` (opcional): Mapa id -> objeto subproducto (para mostrar brand/number_coil/imagen).
 * Si no se pasa, el mini-card usa los fallbacks del ítem.
 */
const ViewCuttingOrderModal = ({ order, isOpen, onClose, subproductMap }) => {
    if (!order) return null;

    const {
        id,
        order_number,
        customer,
        product, // tu API: string
        workflow_status,
        workflow_status_display,
        created_by,
        operator_can_edit_items,
        created_at,
        modified_at,
        completed_at,
        quantity_to_cut,
        items = [],
        warnings = [],
    } = order;

    const cfg = STATUS_CONFIG[workflow_status] || STATUS_CONFIG.pending;
    const statusLabel = workflow_status_display || cfg.label;

    const target = Number(quantity_to_cut ?? 0);
    const totalItems = sumItems(items);

    // Index de warnings por subproduct_id
    const warningsBySubId = new Map((warnings || []).map((w) => [Number(w.subproduct_id), w]));

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title={`Orden de Corte - N°${id}`}
            position="center"
            maxWidth="max-w-5xl"
        >
            <div className="space-y-4 text-text-primary">
                {/* Cabecera */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <div className="min-w-0">
                        <h2 className="text-xl font-bold truncate">Cliente: {customer || "—"}</h2>
                        <p className="text-xl text-muted-foreground truncate">Producto: {getProductLabel(product)}</p>
                    </div>
                    <div className="flex items-center">
                        <span className={`inline-block w-3 h-3 rounded-full mr-2 ${cfg.color}`} />
                        <span className="font-semibold">{statusLabel}</span>
                    </div>
                </div>

                {/* Datos principales */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    <p>
                        <span className="font-semibold">N° de pedido:</span> {order_number ?? "—"}
                    </p>
                    <p>
                        <span className="font-semibold">Asignado a:</span> {getAssignedToDisplay(order)}
                    </p>
                    <p>
                        <span className="font-semibold">Creado por:</span> {created_by || "—"}
                    </p>

                    <p>
                        <span className="font-semibold">Creada:</span> {fmtDate(created_at)}
                    </p>
                    <p>
                        <span className="font-semibold">Modificada:</span> {fmtDate(modified_at)}
                    </p>
                    <p>
                        <span className="font-semibold">Completada:</span> {fmtDate(completed_at)}
                    </p>

                    <p className="sm:col-span-2 lg:col-span-3">
                        <span className="font-semibold">Operario puede editar items:</span>{" "}
                        {operator_can_edit_items ? "Sí" : "No"}
                    </p>
                </div>

                {/* Totales */}
                <div className="flex flex-wrap items-center gap-x-6 gap-y-1 text-sm">
                    <span>
                        <span className="font-semibold">Cantidad pedida:</span> {fmtNum(target)}
                    </span>
                    <span>
                        <span className="font-semibold">Cantidad a cortar:</span> {fmtNum(totalItems)}
                    </span>
                </div>

                {/* Advertencias */}
                {Array.isArray(warnings) && warnings.length > 0 && (
                    <div className="p-3 rounded border border-amber-300 bg-amber-50">
                        <p className="font-semibold text-amber-800 mb-2">
                            Advertencias (otras órdenes <em>pendientes / en proceso</em>)
                        </p>
                        <ul className="list-disc list-inside space-y-1 text-sm text-amber-900">
                            {warnings.map((w, i) => (
                                <li key={`${w.subproduct_id}-${i}`}>
                                    {/* Puedes usar los nuevos campos si querés personalizar el texto */}
                                    Subproducto <strong>{w.subproduct_str ?? w.subproduct_id}</strong> —{" "}
                                    Órdenes activas: <strong>{w.other_active_orders_count}</strong>, Reservado:{" "}
                                    <strong>{fmtNum(w.other_reserved_qty)}</strong>, Disponible (sin reservas):{" "}
                                    <strong>{fmtNum(w.available_excluding_others)}</strong>.
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {/* Ítems */}
                <div>
                    <h3 className="font-semibold mb-2">Ítems</h3>
                    {items.length === 0 ? (
                        <p className="text-sm text-muted-foreground">Sin ítems.</p>
                    ) : (
                        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                            {items.map((it, idx) => {
                                const spId = Number(it.subproduct);
                                const sp = subproductMap?.get?.(spId) || subproductMap?.[spId] || null;
                                const warning = warningsBySubId.get(spId);

                                return (
                                    <SubproductMiniCard
                                        key={it.id ?? `${spId}-${idx}`}
                                        subproductId={spId}
                                        subproduct={sp}
                                        // pasa el valor crudo, el MiniCard lo formatea
                                        quantity={it.cutting_quantity}
                                        // Fallbacks que envía tu API por ítem (nuevos campos)
                                        fallbackBrand={it.subproduct_brand}
                                        fallbackNumberCoil={it.subproduct_number_coil}
                                        fallbackFormType={it.subproduct_form_type}
                                        // Stock previo por ítem
                                        currentStock={it.item_current_stock}
                                        warning={warning}
                                    />
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Cerrar */}
                <div className="flex justify-end pt-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors"
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </Modal>
    );
};

ViewCuttingOrderModal.propTypes = {
    order: PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        order_number: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        product: PropTypes.oneOfType([PropTypes.string, PropTypes.object]), // tu API: string
        customer: PropTypes.string,
        workflow_status: PropTypes.oneOf(["pending", "in_process", "completed", "cancelled"]),
        workflow_status_display: PropTypes.string,
        assigned_to: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        assigned_to_detail: PropTypes.object,
        created_by: PropTypes.string,
        operator_can_edit_items: PropTypes.bool,
        created_at: PropTypes.string,
        modified_at: PropTypes.string,
        completed_at: PropTypes.string,
        quantity_to_cut: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        items: PropTypes.arrayOf(
            PropTypes.shape({
                id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                subproduct: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
                cutting_quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
                // ⬇️ nuevos campos planos del item (fallbacks)
                subproduct_brand: PropTypes.string,
                subproduct_number_coil: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                subproduct_form_type: PropTypes.string, // "Bobina" | "Rollo"
                parent_name: PropTypes.string,
                item_current_stock: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            })
        ),
        warnings: PropTypes.arrayOf(
            PropTypes.shape({
                subproduct_id: PropTypes.number,
                subproduct_brand: PropTypes.string,
                subproduct_number_coil: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                parent_name: PropTypes.string,
                subproduct_str: PropTypes.string,
                other_active_orders_count: PropTypes.number,
                other_reserved_qty: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
                available_excluding_others: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
            })
        ),
    }),
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
    /** opcional: Map<number, Subproduct> para enriquecer cards con brand/number_coil y foto */
    subproductMap: PropTypes.oneOfType([PropTypes.instanceOf(Map), PropTypes.object]),
};

export default ViewCuttingOrderModal;