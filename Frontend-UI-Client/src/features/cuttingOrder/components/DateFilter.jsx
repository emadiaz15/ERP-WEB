import React, { useEffect, useMemo, useRef, useState } from "react";
import DatePicker, { registerLocale } from "react-datepicker";
import es from "date-fns/locale/es";
import { format as dfFormat, parse as dfParse } from "date-fns";
import { useDebouncedEffect } from "@/features/product/hooks/useDebouncedEffect";
import CustomDateInput from "@/components/ui/form/CustomDateInput";
import "react-datepicker/dist/react-datepicker.css";

// Locale español
registerLocale("es", es);

// utils
const toYmd = (d) => (d ? dfFormat(d, "yyyy-MM-dd") : "");
const parseDMY = (s) => {
    // acepta "dd/MM/yyyy"
    if (!s) return null;
    try {
        const dt = dfParse(s, "dd/MM/yyyy", new Date());
        return isNaN(dt) ? null : dt;
    } catch {
        return null;
    }
};

export default function DateFilter({ filters = {}, onFilterChange }) {
    // Opcional: si te viene precargado desde arriba
    const initialStart = useMemo(() => (filters.created_from ? new Date(filters.created_from) : null), [filters.created_from]);
    const initialEnd = useMemo(() => (filters.created_to ? new Date(filters.created_to) : null), [filters.created_to]);

    const [startDate, setStartDate] = useState(initialStart);
    const [endDate, setEndDate] = useState(initialEnd);

    // Emitimos como { created_from, created_to } con debounce 300ms
    useDebouncedEffect(
        () => {
            onFilterChange?.({
                created_from: toYmd(startDate),
                created_to: toYmd(endDate),
            });
        },
        300,
        [startDate, endDate]
    );

    // Permite limpiar con el botón "×" del input custom
    const startRef = useRef(null);
    const endRef = useRef(null);
    useEffect(() => {
        const onClearStart = () => setStartDate(null);
        const onClearEnd = () => setEndDate(null);

        const startEl = startRef.current;
        const endEl = endRef.current;

        startEl?.parentElement?.addEventListener("clear-date", onClearStart);
        endEl?.parentElement?.addEventListener("clear-date", onClearEnd);

        return () => {
            startEl?.parentElement?.removeEventListener("clear-date", onClearStart);
            endEl?.parentElement?.removeEventListener("clear-date", onClearEnd);
        };
    }, []);

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Fecha Inicio */}
            <DatePicker
                selected={startDate}
                onChange={(date) => {
                    setStartDate(date);
                    if (endDate && date && endDate < date) setEndDate(null);
                }}
                // Portaliza el calendario para evitar clipping en modales
                withPortal
                popperClassName="z-[10050]"
                locale="es"
                dateFormat="dd/MM/yyyy"
                selectsStart
                startDate={startDate}
                endDate={endDate}
                // Permitir tipear manualmente "dd/MM/yyyy" si querés soportarlo:
                customInput={
                    <CustomDateInput
                        label="Fecha Inicio"
                        name="start_date"
                    />
                }
                onChangeRaw={(e) => {
                    // Si el usuario escribe, parseamos dd/MM/yyyy
                    const parsed = parseDMY(e.target.value);
                    if (parsed) setStartDate(parsed);
                    else if (e.target.value === "") setStartDate(null);
                }}
                ref={startRef}
            />

            {/* Fecha Fin */}
            <DatePicker
                selected={endDate}
                onChange={(date) => setEndDate(date)}
                withPortal
                popperClassName="z-[10050]"
                locale="es"
                dateFormat="dd/MM/yyyy"
                selectsEnd
                startDate={startDate}
                endDate={endDate}
                minDate={startDate || undefined}
                customInput={
                    <CustomDateInput
                        label="Fecha Fin"
                        name="end_date"
                    />
                }
                onChangeRaw={(e) => {
                    const parsed = parseDMY(e.target.value);
                    if (parsed) setEndDate(parsed);
                    else if (e.target.value === "") setEndDate(null);
                }}
                ref={endRef}
            />
        </div>
    );
}
