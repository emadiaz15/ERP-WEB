import React, { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { getTypeLabel, getDefaultImage } from "./helpers";

const SubproductPickerCard = ({
    subproduct,
    selected,
    onToggle,
    quantity,
    onQuantityChange,
    available,
    disableToggle = false, // 💡 nuevo
}) => {
    const typeLabel = getTypeLabel(subproduct.form_type);
    const imageSrc = subproduct.technical_sheet_photo || getDefaultImage(subproduct.form_type);
    const outOfStock = available <= 0;

    const inputRef = useRef(null);

    // Cuando se selecciona por primera vez y no hay cantidad, deja VACÍO y enfoca
    useEffect(() => {
        if (selected && (quantity === undefined || quantity === null)) {
            onQuantityChange(subproduct.id, ""); // ← vacío (no 1)
            setTimeout(() => inputRef.current?.focus(), 0);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selected]);

    // Valor controlado (permite "")
    const controlledValue =
        quantity === undefined || quantity === null ? "" : String(quantity);

    const handleCardClick = () => {
        if (disableToggle) return;
        // Permitir marcar/desmarcar aunque la cantidad sea 0 o vacía
        onToggle(subproduct.id);
    };

    const handleCheckboxChange = (e) => {
        e.stopPropagation();
        if (disableToggle) return;
        onToggle(subproduct.id);
    };

    const handleInputChange = (e) => {
        // Permitimos vacío para edición fluida
        const raw = e.target.value;
        if (raw !== "" && !Number.isNaN(Number(raw))) {
            const asNum = Number(raw);
            if (asNum > Number(available)) {
                onQuantityChange(subproduct.id, Number(available));
                return;
            }
        }
        onQuantityChange(subproduct.id, raw);
    };

    const handleInputClick = (e) => {
        e.stopPropagation();
    };

    const handleKeyDown = (e) => {
        if (e.key === "Delete" || e.key === "Backspace" || e.key === "Escape") {
            e.stopPropagation();
        }
    };

    const handleWheel = (e) => {
        e.preventDefault();
        e.currentTarget.blur();
    };

    const showQtyWarning =
        selected && !outOfStock && (controlledValue === "" || Number(controlledValue) <= 0);

    return (
        <div
            className={`relative border rounded-xl p-4 shadow-sm transition-all duration-200 ${disableToggle ? "cursor-default" : "cursor-pointer"
                }
      ${selected
                    ? "border-primary-500 bg-primary-50 ring-1 ring-primary-200"
                    : "hover:border-primary-300 hover:bg-primary-50/40"
                }
      ${outOfStock ? "opacity-60 grayscale " : ""}`}
            onClick={handleCardClick}
            title={outOfStock ? "Sin stock" : undefined}
        >
            <div className="absolute top-3 right-3">
                <input
                    type="checkbox"
                    checked={selected}
                    disabled={disableToggle}
                    onChange={handleCheckboxChange}
                    onClick={(e) => e.stopPropagation()}
                />
            </div>

            <div className="flex items-start gap-3">
                <img
                    src={imageSrc}
                    alt={typeLabel}
                    className="w-14 h-14 object-cover rounded"
                    loading="lazy"
                />
                <div className="min-w-0">
                    <div className="font-semibold text-sm leading-snug truncate">
                        {subproduct.parent_name}
                    </div>
                    <div className="text-xs text-gray-600 mt-1">
                        <span className="font-medium">N° Bob/Rollo:</span>{" "}
                        {subproduct?.number_coil ?? "—"}
                    </div>
                    <div className="text-xs text-gray-700">
                        {outOfStock ? (
                            <span className="inline-block px-2 py-0.5 rounded bg-red-100 text-red-700">
                                Sin stock
                            </span>
                        ) : (
                            <>Stock: {Number(available).toFixed(2)} Mts</>
                        )}
                    </div>
                </div>
            </div>

            {selected && !outOfStock && (
                <div className="mt-3">
                    <label className="block text-xs text-gray-500 mb-1">Cantidad</label>
                    <input
                        ref={inputRef}
                        type="number"
                        min="0"
                        step="0.01"
                        max={available}
                        className="w-full border rounded-md px-2 py-1 text-sm"
                        value={controlledValue}
                        onChange={handleInputChange}
                        onClick={handleInputClick}
                        onKeyDown={handleKeyDown}
                        onWheel={handleWheel}
                        inputMode="decimal"
                        placeholder="0"
                    />
                    {showQtyWarning && (
                        <p className="mt-1 text-[11px] text-red-600">
                            La cantidad debe ser mayor a 0.
                        </p>
                    )}
                </div>
            )}
        </div>
    );
};

SubproductPickerCard.propTypes = {
    subproduct: PropTypes.object.isRequired,
    selected: PropTypes.bool,
    onToggle: PropTypes.func.isRequired,
    quantity: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    onQuantityChange: PropTypes.func.isRequired,
    available: PropTypes.number.isRequired,
    disableToggle: PropTypes.bool,
};

export default SubproductPickerCard;
