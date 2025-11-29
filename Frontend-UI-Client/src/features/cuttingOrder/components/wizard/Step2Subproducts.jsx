import React, { useMemo } from "react";
import PropTypes from "prop-types";
import Spinner from "@/components/ui/Spinner";
import SubproductPickerCard from "./SubproductPickerCard";
import { getAvailableStock } from "./helpers";

const Step2Subproducts = ({
    loadingSubs,
    subproducts,
    selectedItems,
    onToggle,
    onQuantityChange,
    requestedTotal = null,
    nextPageUrl,
    fetchNextPage,
    isFetchingNextPage,
}) => {
    // Orden: disponible DESC, number_coil DESC, id DESC
    const sorted = useMemo(() => {
        const list = Array.isArray(subproducts) ? [...subproducts] : [];
        const toNum = (v) => {
            const n = parseFloat(String(v));
            return Number.isNaN(n) ? -Infinity : n;
        };

        list.sort((a, b) => {
            const av = getAvailableStock(a);
            const bv = getAvailableStock(b);
            if (av !== bv) return bv - av;

            const ac = toNum(a?.number_coil ?? a?.coil_number ?? a?.coil);
            const bc = toNum(b?.number_coil ?? b?.coil_number ?? b?.coil);
            if (ac !== bc) return bc - ac;

            return (b?.id ?? 0) - (a?.id ?? 0);
        });

        return list;
    }, [subproducts]);

    if (loadingSubs) {
        return (
            <div className="flex justify-center py-6">
                <Spinner size="6" color="text-primary-500" />
            </div>
        );
    }

    if (!sorted.length) {
        return (
            <div className="text-sm text-gray-500 py-4">
                No hay subproductos activos para este producto.
            </div>
        );
    }

    const totalSelected = Object.values(selectedItems).reduce(
        (acc, v) => acc + (Number(v) || 0),
        0
    );
    const target = Number(requestedTotal) > 0 ? Number(requestedTotal) : null;
    const remaining = target != null ? Math.max(0, target - totalSelected) : null;

    // Normaliza/clamp de cantidad (0..available) y respeta “restante” si hay target
    const handleQuantityChange = (sp, id, raw) => {
        const s = String(raw ?? "").replace(",", ".").trim();
        if (s === "") {
            onQuantityChange(id, "");
            return;
        }
        let n = parseFloat(s);
        if (!Number.isFinite(n)) return;

        // clamp por stock
        const maxByStock = getAvailableStock(sp);
        if (n < 0) n = 0;
        if (n > maxByStock) n = maxByStock;

        // clamp por objetivo restante
        if (target != null) {
            const sumOthers = Object.entries(selectedItems).reduce((acc, [k, v]) => {
                if (String(k) === String(id)) return acc;
                return acc + (Number(v) || 0);
            }, 0);
            const maxForThis = Math.max(0, target - sumOthers);
            if (n > maxForThis) n = maxForThis;
        }

        const fixed = Math.round(n * 100) / 100;
        onQuantityChange(id, String(fixed));
    };

    return (
        <>
            <div className="flex items-baseline justify-between">
                <p className="font-semibold">Selecciona subproductos y cantidades:</p>
                {target != null && (
                    <div className="text-xs text-gray-600">
                        Objetivo: <b>{target.toFixed(2)}</b> — Seleccionado:{" "}
                        <b>{totalSelected.toFixed(2)}</b>{" "}
                        — Restante: <b>{Math.max(0, target - totalSelected).toFixed(2)}</b>
                    </div>
                )}
            </div>

            <div
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-80 overflow-y-auto pr-1"
                style={{ position: "relative" }}
                id="subproducts-scroll-container"
            >
                {sorted.map((sp) => {
                    const available = getAvailableStock(sp);
                    const value = selectedItems[sp.id];
                    const isSelected = Object.prototype.hasOwnProperty.call(
                        selectedItems,
                        sp.id
                    );
                    return (
                        <SubproductPickerCard
                            key={sp.id}
                            subproduct={sp}
                            selected={isSelected}
                            onToggle={onToggle}
                            quantity={value ?? ""}
                            onQuantityChange={(id, val) => handleQuantityChange(sp, id, val)}
                            available={available}
                        />
                    );
                })}
                {/* Infinite scroll sentinel */}
                {nextPageUrl && (
                    <div
                        style={{ height: "32px", display: "flex", alignItems: "center", justifyContent: "center" }}
                        ref={el => {
                            if (!el) return;
                            const container = document.getElementById("subproducts-scroll-container");
                            if (!container) return;
                            const observer = new window.IntersectionObserver((entries) => {
                                if (entries[0].isIntersecting && !isFetchingNextPage) {
                                    fetchNextPage();
                                }
                            }, { root: container, threshold: 0.1 });
                            observer.observe(el);
                            return () => observer.disconnect();
                        }}
                    >
                        {isFetchingNextPage ? <Spinner size="4" color="text-primary-500" /> : <button type="button" className="text-xs px-2 py-1 bg-neutral-100 rounded" onClick={fetchNextPage}>Cargar más</button>}
                    </div>
                )}
            </div>
        </>
    );
};

Step2Subproducts.propTypes = {
    loadingSubs: PropTypes.bool,
    subproducts: PropTypes.array.isRequired,
    selectedItems: PropTypes.object.isRequired,
    onToggle: PropTypes.func.isRequired,
    onQuantityChange: PropTypes.func.isRequired,
    requestedTotal: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default Step2Subproducts;
