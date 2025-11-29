import React, { useState, useMemo } from "react";
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

const DateInput = React.forwardRef(({ value, onClick, label, name, placeholder = "dd/mm/aaaa" }, ref) => (
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

/**
 * Filtro de fechas para historial de stock, estilo OrderFilter.
 * Props:
 *   - onFilterChange: function({ start_date, end_date })
 */
const StockDateFilter = ({ onFilterChange }) => {
    const [local, setLocal] = useState({ start_date: "", end_date: "" });

    const startDateObj = useMemo(() => ymdToDate(local.start_date), [local.start_date]);
    const endDateObj = useMemo(() => ymdToDate(local.end_date), [local.end_date]);

    // Evita loop infinito: solo llama onFilterChange si los valores realmente cambian
    const lastSent = React.useRef({ start_date: '', end_date: '' });
    React.useEffect(() => {
        const { start_date, end_date } = local;
        if (
            start_date !== lastSent.current.start_date ||
            end_date !== lastSent.current.end_date
        ) {
            lastSent.current = { start_date, end_date };
            onFilterChange?.({ start_date, end_date });
        }
    }, [local, onFilterChange]);

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
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-4">
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

export default StockDateFilter;
