import React, { forwardRef } from "react";
import { CalendarIcon } from "@heroicons/react/24/solid";

const CustomDateInput = forwardRef(
    ({ value, onClick, label, name, placeholder = "dd/mm/aaaa" }, ref) => (
        <div className="mb-2 w-full">
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-text-secondary">
                    {label}
                </label>
            )}
            <div className="relative mt-1">
                <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                    <CalendarIcon className="w-5 h-5 text-gray-400" />
                </div>
                <input
                    id={name}
                    name={name}
                    type="text"
                    readOnly
                    ref={ref}
                    onClick={onClick}
                    value={value || ""}
                    placeholder={placeholder}
                    className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200 cursor-pointer"
                />
                {/* Botón clear */}
                {value ? (
                    <button
                        type="button"
                        onClick={(e) => {
                            e.stopPropagation();
                            // disparamos click en el input para que DatePicker maneje focus si hace falta
                            if (ref && typeof ref !== "function" && ref?.current) ref.current.blur();
                            const clearEvent = new Event("clear-date", { bubbles: true });
                            e.currentTarget.dispatchEvent(clearEvent);
                        }}
                        className="absolute top-1/2 -translate-y-1/2 right-3 text-gray-400 hover:text-gray-600"
                        aria-label="Limpiar fecha"
                    >
                        ×
                    </button>
                ) : null}
            </div>
        </div>
    )
);

CustomDateInput.displayName = "CustomDateInput";
export default CustomDateInput;
