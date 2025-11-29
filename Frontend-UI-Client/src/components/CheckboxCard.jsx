import React from "react";

/**
 * CheckboxCard: Checkbox estilizado tipo card, reutilizable.
 * Props:
 * - id: string (id del input)
 * - checked: boolean
 * - onChange: function
 * - label: string | ReactNode
 * - className: string (opcional)
 * - ...rest: otros props para el input
 */
const CheckboxCard = ({ id, checked, onChange, label, className = "", ...rest }) => (
    <div className={`flex items-center px-0 pb-0 pt-2 bg-bg-background-100 ${className}`} style={{ minHeight: '44px' }}>
        <input
            id={id}
            type="checkbox"
            checked={checked}
            onChange={onChange}
            className="h-5 w-5 text-primary-600 border-background-200 focus:ring-2 focus:ring-primary-500 rounded transition duration-150 ease-in-out bg-white dark:bg-gray-700"
            style={{ marginRight: '0.5rem' }}
            {...rest}
        />
        <label htmlFor={id} className="text-sm font-medium text-text-secondary cursor-pointer select-none">
            {label}
        </label>
    </div>
);

export default CheckboxCard;
