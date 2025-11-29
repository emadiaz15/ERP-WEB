// src/features/cuttingOrder/components/SubproductMiniCard.jsx
import React from "react";
import PropTypes from "prop-types";

/** Ícono estático según form_type (en /public) */
function getStaticIcon(formType) {
    const t = String(formType || "").toLowerCase().trim();
    if (t === "bobina") return "/bobina.png";
    if (t === "rollo") return "/rollo.png";
    return "/bobina.png";
}

function fmt(n) {
    const v = Number(n);
    if (!Number.isFinite(v)) return "—";
    try {
        return new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(v);
    } catch {
        return String(v.toFixed ? v.toFixed(2) : v);
    }
}

/** Resuelve marca (brand) probando varias claves habituales */
function resolveBrand(sp = {}) {
    return (
        sp.brand ||
        sp.parent_brand ||
        sp.product_brand ||
        sp.parent?.brand ||
        ""
    );
}

/** Resuelve N° de bobina/rollo probando varias claves habituales */
function resolveNumberCoil(sp = {}) {
    const v =
        sp.number_coil ??
        sp.coil_number ??
        sp.coil ??
        sp.roll_number ??
        sp.numero_bobina ??
        sp.numero_rollo;
    return (v ?? "");
}

/** Intenta inferir el stock actual del subproducto si no se pasa currentStock */
function inferCurrentStock(sp, warning) {
    const candidates = [
        sp?.stock?.quantity,
        sp?.subproduct_stock?.quantity,
        sp?.current_stock,
        sp?.current_stock_quantity,
        sp?.stock_quantity,
        sp?.available_stock,
        sp?.quantity,
    ];
    for (const c of candidates) {
        const n = Number(c);
        if (Number.isFinite(n)) return n;
    }
    // Fallback: disponible sin reservas (de otras órdenes) desde warnings
    const w = warning?.available_excluding_others;
    if (w != null && Number.isFinite(Number(w))) return Number(w);
    return undefined;
}

const SubproductMiniCard = ({
    subproductId,
    subproduct,
    quantity,
    currentStock,        // preferido para "Stock antes"
    warning,             // { other_active_orders_count, other_reserved_qty, available_excluding_others }
    // ⬇️ Fallbacks provenientes del item de la API (nuevos campos)
    fallbackBrand,
    fallbackNumberCoil,
    fallbackFormType,
}) => {
    const sp = subproduct || {};

    // form_type (para el ícono): usa el del subproducto o el fallback del item
    const formType = sp.form_type ?? fallbackFormType;
    const imageSrc = getStaticIcon(formType);

    // Marca: primero la del subproducto, si no hay usa la del item
    const brandFromSp = resolveBrand(sp);
    const brand = (brandFromSp || fallbackBrand || "—");

    // N° Bob/Rollo: primero el del subproducto, si no hay usa el del item
    const numberFromSp = resolveNumberCoil(sp);
    const numberCoil = (numberFromSp || fallbackNumberCoil || "—");

    // Stock antes / después
    const qty = Number(quantity) || 0;
    const before = (currentStock ?? inferCurrentStock(sp, warning));
    const after = Number.isFinite(before) ? Math.max(0, before - qty) : undefined;

    // Advertencia (otras órdenes PENDING/IN_PROCESS)
    const hasWarning = !!(warning && Number(warning.other_active_orders_count) > 0);

    return (
        <div
            className={`relative border rounded-xl p-4 shadow-sm bg-white transition-all duration-200
      ${hasWarning ? "ring-1 ring-amber-300" : "hover:border-primary-300 hover:bg-primary-50/40"}`}
        >
            {hasWarning && (
                <span className="absolute -top-2 -right-2 text-xs px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 border border-amber-300">
                    Reserva detectada
                </span>
            )}

            <div className="flex items-start gap-3">
                <img
                    src={imageSrc}
                    alt={formType || "—"}
                    className="w-14 h-14 object-contain rounded bg-white"
                    loading="lazy"
                    onError={(e) => {
                        e.currentTarget.src = getStaticIcon(formType);
                    }}
                />

                <div className="min-w-0">
                    {/* Marca */}
                    <div className="font-semibold text-sm leading-snug truncate">{brand}</div>

                    {/* N° Bob/Rollo */}
                    <div className="text-xs text-gray-600 mt-1">
                        <span className="font-medium">N° Bob/Rollo:</span> {numberCoil}
                    </div>

                    {/* Stock antes/después */}
                    <div className="text-xs text-gray-700 mt-1 flex flex-col gap-1">
                        <span>
                            <span className="font-medium">Antes:</span> {fmt(before)} Mts
                        </span>
                        <span>
                            <span className="font-medium">Después:</span> {fmt(after)} Mts
                        </span>
                    </div>
                </div>

                {/* Cantidad del ítem (derecha) */}
                <div className="ml-auto text-right">
                    <div className="text-[10px] uppercase text-gray-500">Cantidad</div>
                    <div className="text-base font-semibold tabular-nums">{fmt(qty)}</div>
                </div>
            </div>

            {hasWarning && (
                <div className="mt-3 text-[12px] text-amber-900 bg-amber-50 border border-amber-200 rounded p-2">
                    <div>
                        Órdenes activas: <strong>{warning.other_active_orders_count}</strong>
                    </div>
                    <div>
                        Reservado: <strong>{fmt(warning.other_reserved_qty)}</strong>
                    </div>
                    <div>
                        Disponible (sin reservas): <strong>{fmt(warning.available_excluding_others)}</strong>
                    </div>
                </div>
            )}
        </div>
    );
};

SubproductMiniCard.propTypes = {
    subproductId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    subproduct: PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        brand: PropTypes.string,                     // título
        form_type: PropTypes.string,                 // "Bobina" | "Rollo"
        number_coil: PropTypes.oneOfType([PropTypes.string, PropTypes.number]), // N° bob/rollo
        // posibles fuentes de stock
        stock: PropTypes.shape({ quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]) }),
        subproduct_stock: PropTypes.shape({ quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]) }),
        current_stock: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        current_stock_quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        stock_quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        available_stock: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        parent: PropTypes.shape({ brand: PropTypes.string }),
    }),
    quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    currentStock: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    warning: PropTypes.shape({
        other_active_orders_count: PropTypes.number,
        other_reserved_qty: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        available_excluding_others: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    }),
    // ⬇️ fallbacks del item (nuevos)
    fallbackBrand: PropTypes.string,
    fallbackNumberCoil: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    fallbackFormType: PropTypes.string,
};

export default SubproductMiniCard;
