// src/components/ui/form/FormSelect.jsx
import React from "react";
import * as Select from "@radix-ui/react-select";

const EMPTY_SENTINEL = "__EMPTY__";

const FormSelect = ({
    label,
    name,
    value,
    onChange,           // sigue recibiendo (e) => ...
    options = [],
    required = false,
    loading = false,
    disabled = false,
    placeholder = "todas",   // 👈 por defecto mostramos "todas"
    className = "",
    noMargin = false,   // nuevo: elimina mb-4 por defecto
}) => {
    // Normalizo el value a string (Radix Select trabaja en strings)
    const normalizedValue =
        value === undefined || value === null ? "" : String(value);

    // Adaptador para conservar la firma onChange(e)
    const handleValueChange = (v) => {
        const finalValue = v === EMPTY_SENTINEL ? "" : v;
        if (typeof onChange === "function") {
            onChange({ target: { name, value: finalValue } });
        }
    };

    // Aseguro que cada item tenga value NO vacío al renderizar (Radix no acepta "")
    const safeOptions = (Array.isArray(options) ? options : []).map((opt) => {
        const raw = opt?.value;
        const str =
            raw === undefined || raw === null || String(raw) === ""
                ? EMPTY_SENTINEL
                : String(raw);
        return { ...opt, _safeValue: str };
    });

    // Si hay una opción con value === "", usamos su label como "placeholder" visual
    const emptyLabel =
        (options.find((o) => String(o?.value ?? "") === "")?.label ?? "").trim();

    // Cuando value === "", Radix no tiene item seleccionado (porque usamos sentinel),
    // por eso usamos el placeholder para mostrar "todas" (o el label de esa opción vacía).
    const displayedPlaceholder = loading
        ? "Cargando…"
        : emptyLabel || placeholder || "todas";

    return (
        <div className={`${noMargin ? '' : 'mb-4'} ${className}`}>
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-text-secondary">
                    {label}
                </label>
            )}

            <Select.Root
                name={name}
                value={normalizedValue === "" ? "" : String(normalizedValue)}
                onValueChange={handleValueChange}
                disabled={disabled || loading}
                required={required}
            >
                <Select.Trigger
                    id={name}
                    className="mt-1 inline-flex w-full items-center justify-between rounded-md border border-gray-300 bg-white text-text-primary px-3 py-2 text-left shadow-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                    aria-label={label || name}
                >
                    {/* 👇 si value === "" mostramos "todas" (o el label de la opción vacía) */}
                    <Select.Value placeholder={displayedPlaceholder} />
                    <Select.Icon className="ml-2 text-primary-500">
                        <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path
                                fillRule="evenodd"
                                d="M5.23 7.21a.75.75 0 011.06.02L10 10.939l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z"
                                clipRule="evenodd"
                            />
                        </svg>
                    </Select.Icon>
                </Select.Trigger>

                <Select.Portal>
                    <Select.Content
                        position="popper"
                        sideOffset={6}
                        className="z-[10050] overflow-hidden rounded-md border bg-white shadow-lg"
                    >
                        <Select.ScrollUpButton className="px-2 py-1 text-sm">▲</Select.ScrollUpButton>
                        <Select.Viewport className="p-1 max-h-64">
                            {loading ? (
                                <Select.Item
                                    disabled
                                    value="__loading__"
                                    className="cursor-default select-none rounded px-2 py-1.5 text-gray-500"
                                >
                                    <Select.ItemText>Cargando…</Select.ItemText>
                                </Select.Item>
                            ) : safeOptions.length > 0 ? (
                                safeOptions.map((opt) => (
                                    <Select.Item
                                        key={opt._safeValue}
                                        value={opt._safeValue}
                                        className="cursor-pointer select-none rounded px-2 py-1.5 outline-none data-[highlighted]:bg-primary-50"
                                    >
                                        <Select.ItemText>{opt.label}</Select.ItemText>
                                    </Select.Item>
                                ))
                            ) : (
                                <Select.Item
                                    disabled
                                    value="__empty__"
                                    className="cursor-default select-none rounded px-2 py-1.5 text-gray-500"
                                >
                                    <Select.ItemText>Sin opciones</Select.ItemText>
                                </Select.Item>
                            )}
                        </Select.Viewport>
                        <Select.ScrollDownButton className="px-2 py-1 text-sm">▼</Select.ScrollDownButton>
                    </Select.Content>
                </Select.Portal>
            </Select.Root>
        </div>
    );
};

export default FormSelect;
