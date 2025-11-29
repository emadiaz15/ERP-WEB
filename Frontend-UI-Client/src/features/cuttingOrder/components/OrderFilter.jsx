// src/features/cuttingOrder/components/OrderFilter.jsx
import React, { useState, useCallback, useMemo, forwardRef } from "react";
import { useDebouncedEffect } from "@/features/product/hooks/useDebouncedEffect";
import FormSelect from "@/components/ui/form/FormSelect";

import DatePicker, { registerLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import es from "date-fns/locale/es";
import { format as dfFormat, parseISO, isValid } from "date-fns";
import { CalendarIcon } from "@heroicons/react/24/solid";

registerLocale("es", es);

// Utils fecha
const toYmd = (d) => (d ? dfFormat(d, "yyyy-MM-dd") : "");
const ymdToDate = (s) => {
    if (!s) return null;
    try {
        const d = parseISO(s);
        return isValid(d) ? d : null;
    } catch {
        return null;
    }
};

const DateInput = forwardRef(({ value, onClick, label, name, placeholder = "dd/mm/aaaa" }, ref) => (
    <div className="mb-2 w-full">
        {label && (
            <label htmlFor={name} className="block text-sm font-medium text-text-secondary">
                {label}
            </label>
        )}
        <div className="relative mt-1">
            <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                <CalendarIcon className="h-5 w-5 text-gray-400" />
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
            {value ? (
                <button
                    type="button"
                    onClick={(e) => {
                        e.stopPropagation();
                        const ev = new CustomEvent("date-clear", { bubbles: true, detail: { name } });
                        e.currentTarget.dispatchEvent(ev);
                    }}
                    className="absolute top-1/2 -translate-y-1/2 right-3 text-gray-400 hover:text-gray-600"
                    aria-label="Limpiar fecha"
                >
                    ×
                </button>
            ) : null}
        </div>
    </div>
));
DateInput.displayName = "DateInput";

const OrderFilter = ({ filters = {}, onFilterChange }) => {
    const [local, setLocal] = useState({
        start_date: filters.start_date || "",
        end_date: filters.end_date || "",
        customer: filters.customer || "",
        order_number: filters.order_number || "",
        workflow_status: filters.workflow_status ?? "", // "" = Todas
    });

    const startDateObj = useMemo(() => ymdToDate(local.start_date), [local.start_date]);
    const endDateObj = useMemo(() => ymdToDate(local.end_date), [local.end_date]);

    // Debounce salida UI -> API (con nombres que espera el backend)
    useDebouncedEffect(
        () => {
            const clean = {
                created_from: local.start_date || "",
                created_to: local.end_date || "",
                customer: (local.customer || "").trim(),
                order_number: (local.order_number || "").trim(),
                workflow_status: local.workflow_status || "", // "" = todas → no filtra estado
            };
            onFilterChange?.(clean);
        },
        300,
        [local]
    );

    const handleChange = useCallback((e) => {
        const { name, value } = e.target;
        setLocal((prev) => ({ ...prev, [name]: value }));
    }, []);

    const onChangeStart = (date) => {
        setLocal((prev) => {
            const next = { ...prev, start_date: toYmd(date) };
            if (date && endDateObj && endDateObj < date) next.end_date = "";
            return next;
        });
    };
    const onChangeEnd = (date) => setLocal((prev) => ({ ...prev, end_date: toYmd(date) }));

    const onChangeRawStart = (e) => { if (e.type === "date-clear") setLocal((p) => ({ ...p, start_date: "" })); };
    const onChangeRawEnd = (e) => { if (e.type === "date-clear") setLocal((p) => ({ ...p, end_date: "" })); };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {/* Estado */}
            <div className="mb-0">
                <FormSelect
                    name="workflow_status"
                    label="Estado"
                    value={local.workflow_status}   // "" por defecto → “Todas”
                    onChange={handleChange}
                    options={[
                        { value: "", label: "Todas" },
                        { value: "pending", label: "Pendientes" },
                        { value: "in_process", label: "En proceso" },
                        { value: "completed", label: "Completadas" },
                        { value: "cancelled", label: "Canceladas" },
                    ]}
                />
            </div>

            {/* Nro de Pedido */}
            <div className="mb-2">
                <label htmlFor="order_number" className="block text-sm font-medium text-text-secondary">Nro de Pedido</label>
                <div className="relative mt-1">
                    <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                        <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" />
                        </svg>
                    </div>
                    <input
                        id="order_number"
                        name="order_number"
                        type="text"
                        placeholder="Ej: 1234"
                        value={local.order_number}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                    />
                </div>
            </div>

            {/* Cliente */}
            <div className="mb-2">
                <label htmlFor="customer" className="block text-sm font-medium text-text-secondary">Cliente</label>
                <div className="relative mt-1">
                    <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                        <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" />
                        </svg>
                    </div>
                    <input
                        id="customer"
                        name="customer"
                        type="text"
                        placeholder="Buscar cliente"
                        value={local.customer}
                        onChange={handleChange}
                        className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                    />
                </div>
            </div>

            {/* Fecha Inicio */}
            <DatePicker
                selected={startDateObj}
                onChange={onChangeStart}
                onChangeRaw={onChangeRawStart}
                withPortal
                popperClassName="z-[10050]"
                locale="es"
                dateFormat="dd/MM/yyyy"
                selectsStart
                startDate={startDateObj}
                endDate={endDateObj}
                customInput={<DateInput label="Fecha Inicio" name="start_date" />}
            />

            {/* Fecha Fin */}
            <DatePicker
                selected={endDateObj}
                onChange={onChangeEnd}
                onChangeRaw={onChangeRawEnd}
                withPortal
                popperClassName="z-[10050]"
                locale="es"
                dateFormat="dd/MM/yyyy"
                selectsEnd
                startDate={startDateObj}
                endDate={endDateObj}
                minDate={startDateObj || undefined}
                customInput={<DateInput label="Fecha Fin" name="end_date" />}
            />
        </div>
    );
};

export default OrderFilter;


