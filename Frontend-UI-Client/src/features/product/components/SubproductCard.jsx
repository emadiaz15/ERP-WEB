// src/features/product/components/SubproductCard.jsx
import React from "react";
import PropTypes from "prop-types";
import {
    PencilIcon,
    EyeIcon,
    ClockIcon,
    ScissorsIcon,
} from "@heroicons/react/24/outline";
import { useAuth } from "@/context/AuthProvider";
import { useNavigate } from "react-router-dom";

const getDefaultImage = (subType) => {
    const t = (subType || "").toLowerCase();
    if (t === "rollo") return "/rollo.png";
    if (t === "bobina") return "/bobina.png";
    return "/default.png";
};

const toNumber = (v, def = 0) => {
    if (v == null) return def;
    if (typeof v === "number") return Number.isFinite(v) ? v : def;
    const n = parseFloat(String(v).replace(",", "."));
    return Number.isFinite(n) ? n : def;
};

// Preferimos current_stock; si no viene, usamos current_stock_quantity;
// luego initial_stock_quantity. No se suman entre sí.
const getDisplayAvailable = (sp) => {
    const a =
        sp?.current_stock ??
        sp?.current_stock_quantity ??
        sp?.initial_stock_quantity ??
        0;
    return toNumber(a, 0);
};

const SubproductCard = ({
    subproduct,
    onAddToOrder,
    onEdit,
    onDelete, // (por si lo reactivas)
    onViewDetails,
}) => {
    const imageUrl = subproduct?.technical_sheet_photo
        ? subproduct.technical_sheet_photo
        : getDefaultImage(subproduct?.form_type);

    const { user } = useAuth();
    const isStaff = !!user?.is_staff;
    const navigate = useNavigate();

    const handleViewStockHistory = () => {
        if (subproduct?.id) navigate(`/subproducts/${subproduct.id}/stock-history`);
    };

    const available = getDisplayAvailable(subproduct);

    // Badge:
    // - "Disponible" solo si status === true Y hay stock > 0
    // - de lo contrario "Terminada"
    const isAvailable = subproduct?.status === true && available > 0;
    const isDepleted = available <= 0;

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-100 w-full max-w-xl text-sm">
            {/* Header */}
            <div className="flex justify-between items-center px-2 py-1 border-b">
                <span className="text-sm font-semibold truncate">
                    {subproduct?.parent_name || subproduct?.name || "Subproducto"}
                </span>
                <div className="flex items-center text-xs">
                    <span
                        className={`inline-block w-3 h-3 mr-2 rounded-full ${isAvailable ? "bg-green-500" : "bg-red-500"
                            }`}
                    />
                    {isAvailable ? "Disponible" : "Terminada"}
                </div>
            </div>

            {/* Content */}
            <div className="flex flex-col md:flex-row p-2 space-y-2 md:space-y-0 md:space-x-2">
                <img
                    className="object-cover w-full h-24 md:w-24 md:h-24 rounded"
                    src={imageUrl}
                    alt={subproduct?.brand || subproduct?.parent_name || "Subproducto"}
                />
                <ul className="flex-1 text-sm text-gray-700 space-y-1 overflow-hidden">
                    <li>
                        <strong>Marca:</strong> {subproduct?.brand || "—"}
                    </li>
                    <li>
                        <strong>N°:</strong> {subproduct?.number_coil ?? "—"}
                    </li>
                    <li className="pl-14 text-2xl text-black">
                        {available.toFixed(2)} Mts
                    </li>
                </ul>
            </div>

            {/* Actions */}
            <div className="flex flex-wrap justify-center items-center gap-2 p-4 border-t">
                {/* 👁️ Ficha Técnica */}
                <button
                    onClick={onViewDetails}
                    title="Ver Ficha Técnica"
                    className="bg-blue-500 hover:bg-blue-600 transition-colors rounded p-2"
                >
                    <EyeIcon className="w-5 h-5 text-white" />
                </button>

                {/* ⏰ Historial de Stock */}
                <button
                    onClick={handleViewStockHistory}
                    title="Ver Historial de Stock"
                    className="bg-amber-500 hover:bg-amber-600 transition-colors rounded p-2"
                >
                    <ClockIcon className="w-5 h-5 text-white" />
                </button>

                {isStaff && (
                    <>
                        {/* ✂️ Crear Orden desde este subproducto */}
                        <button
                            onClick={() =>
                                onAddToOrder?.({
                                    productId: subproduct?.parent,
                                    subproductId: subproduct?.id,
                                })
                            }
                            title={
                                !isAvailable
                                    ? isDepleted
                                        ? "Sin stock disponible"
                                        : "Subproducto inactivo"
                                    : "Crear Orden de Corte"
                            }
                            disabled={!isAvailable}
                            className={`rounded p-2 transition-colors ${!isAvailable
                                ? "bg-gray-300 cursor-not-allowed"
                                : "bg-indigo-500 hover:bg-indigo-600"
                                }`}
                        >
                            <ScissorsIcon className="w-5 h-5 text-white" />
                        </button>

                        {/* ✏️ Editar */}
                        <button
                            onClick={onEdit}
                            title="Editar Subproducto"
                            className="bg-primary-500 hover:bg-primary-600 transition-colors rounded p-2"
                        >
                            <PencilIcon className="w-5 h-5 text-white" />
                        </button>

                        {/* 🗑️ Eliminar (opcional)
            <button
              onClick={onDelete}
              title="Eliminar Subproducto"
              className="bg-red-500 hover:bg-red-600 transition-colors rounded p-2"
            >
              <TrashIcon className="w-5 h-5 text-white" />
            </button>
            */}
                    </>
                )}
            </div>
        </div>
    );
};

SubproductCard.propTypes = {
    subproduct: PropTypes.object.isRequired,
    onAddToOrder: PropTypes.func,
    onEdit: PropTypes.func,
    onDelete: PropTypes.func,
    onViewDetails: PropTypes.func,
};

export default SubproductCard;
