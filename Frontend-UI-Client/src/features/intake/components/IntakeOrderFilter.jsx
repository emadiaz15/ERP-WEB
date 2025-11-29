// src/features/intake/components/IntakeOrderFilter.jsx
import React, { useState, useCallback, useMemo, forwardRef, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { useDebouncedEffect } from "@/features/product/hooks/useDebouncedEffect";
import DatePicker, { registerLocale } from "react-datepicker";
import es from "date-fns/locale/es";
import { format as dfFormat, parseISO, isValid } from "date-fns";
import { CalendarIcon } from "@heroicons/react/24/solid";
import { filterUsers } from "@/features/user/services/filterUsers";
import FormSelect from "@/components/ui/form/FormSelect";
import "react-datepicker/dist/react-datepicker.css";

registerLocale("es", es);

// Utils fecha
const toYmd = (d) => (d ? dfFormat(d, "yyyy-MM-dd") : "");
const ymdToDate = (s) => {
  if (!s) return null;
  try { const d = parseISO(s); return isValid(d) ? d : null; } catch { return null; }
};

// Custom input (igual patrón que Cutting OrderFilter)
const DateInput = forwardRef(({ value, onClick, label, name, placeholder = "dd/mm/aaaa" }, ref) => (
  <div className="mb-2 w-full">
    {label && (
      <label htmlFor={name} className="block text-sm font-medium text-text-secondary">{label}</label>
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

// Custom popover select to avoid native select positioning issues inside portals/overlays
const AssignedUserSelect = ({ label = "Asignado a", value, onChange, users = [] }) => {
  const [open, setOpen] = useState(false);
  const anchorRef = useRef(null);
  const popRef = useRef(null);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return users;
    return users.filter(u => {
      const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.toLowerCase();
      return full.includes(q) || (u.username || '').toLowerCase().includes(q) || (u.email || '').toLowerCase().includes(q);
    });
  }, [users, query]);

  // Close on outside click / escape
  useEffect(() => {
    if (!open) return;
    const onDoc = (e) => {
      if (e.key === 'Escape') { setOpen(false); return; }
      if (popRef.current && !popRef.current.contains(e.target) && !anchorRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onDoc);
    document.addEventListener('keydown', onDoc);
    return () => {
      document.removeEventListener('mousedown', onDoc);
      document.removeEventListener('keydown', onDoc);
    };
  }, [open]);

  const currentLabel = useMemo(() => {
    if (!value) return 'Todos';
    const u = users.find(u => String(u.id) === String(value));
    if (!u) return '—';
    const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
    return full || u.username || u.email || `ID ${u.id}`;
  }, [value, users]);

  return (
    <div className="mb-2 relative" ref={anchorRef}>
      <label className="block text-sm font-medium text-text-secondary">{label}</label>
      <button
        type="button"
        onClick={() => setOpen(o => !o)}
        className={`mt-1 w-full px-3 py-2 border rounded-md text-left text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200 bg-white flex items-center justify-between transition-colors ${open ? 'ring-2 ring-primary-500' : ''}`}
        aria-haspopup="listbox"
        aria-expanded={open}
      >
        <span className={`truncate mr-2 ${!value ? 'text-text-secondary' : ''}`}>{currentLabel}</span>
        <svg className={`w-5 h-5 text-gray-500 transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.24a.75.75 0 01-1.06 0L5.21 8.29a.75.75 0 01.02-1.08z" clipRule="evenodd" /></svg>
      </button>
      {open && (
        <div
          ref={popRef}
          className="absolute z-50 mt-1 w-full max-h-64 overflow-y-auto rounded-md border border-background-200 bg-white shadow-lg animate-fade-in"
        >
          <div className="p-2 border-b bg-background-100 sticky top-0">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Buscar usuario..."
              className="w-full px-2 py-1 text-sm border border-background-200 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>
          <ul role="listbox" className="py-1 text-sm">
            <li>
              <button
                type="button"
                onClick={() => { onChange(""); setOpen(false); }}
                className={`w-full text-left px-3 py-2 hover:bg-primary-50 ${!value ? 'bg-primary-100 font-medium' : ''}`}
              >Todos</button>
            </li>
            {filtered.map(u => {
              const id = String(u.id);
              const full = `${u.first_name ?? ''} ${u.last_name ?? ''}`.trim();
              return (
                <li key={id}>
                  <button
                    type="button"
                    onClick={() => { onChange(id); setOpen(false); }}
                    className={`w-full text-left px-3 py-2 hover:bg-primary-50 ${String(value) === id ? 'bg-primary-100 font-medium' : ''}`}
                  >
                    {full || u.username || u.email || `ID ${id}`}
                  </button>
                </li>
              );
            })}
            {filtered.length === 0 && (
              <li className="px-3 py-2 text-xs text-muted-foreground">Sin resultados</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
};

const IntakeOrderFilter = ({ value = {}, onChange }) => {
  const [local, setLocal] = useState({
    start_date: value.start_date || value.created_from || "",
    end_date: value.end_date || value.created_to || "",
    customer_name: value.customer_name || "",
    carrier: value.carrier || "",
    assigned_to: value.assigned_to || "",
    flow_status: value.flow_status || "", // "" = todas
  });

  const startDateObj = useMemo(() => ymdToDate(local.start_date), [local.start_date]);
  const endDateObj = useMemo(() => ymdToDate(local.end_date), [local.end_date]);

  // Usuarios para asignación
  const [users, setUsers] = useState([]);
  useEffect(() => {
    let active = true;
    filterUsers({ is_active: "true", page_size: 1000 })
      .then((res) => {
        if (!active) return;
        const results = res?.results || res?.data || res || [];
        setUsers(results);
      })
      .catch(() => { });
    return () => { active = false; };
  }, []);

  // Debounce salida para notificar al padre en formato que espera IntakeOrdersList
  const didInitialEmitRef = useRef(false);
  useDebouncedEffect(() => {
    if (!didInitialEmitRef.current) {
      // Evita emisión inicial para no disparar refetch redundante
      didInitialEmitRef.current = true;
      return;
    }
    const clean = {
      created_from: local.start_date || "",
      created_to: local.end_date || "",
      customer_name: (local.customer_name || "").trim(),
      carrier: (local.carrier || "").trim(),
      assigned_to: local.assigned_to || "",
      flow_status: local.flow_status || "", // si vacío no filtra
    };
    onChange?.(clean);
  }, 300, [local]);

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

  // Reset eliminado: se dejó fuera el botón de limpiar a pedido del usuario

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-4">
      {/* Estado / Flow Status */}
      <div className="mb-0">
        <FormSelect
          name="flow_status"
          label="Estado"
          value={local.flow_status}
          onChange={handleChange}
          options={[
            { value: "", label: "Todas" },
            { value: "pending", label: "Pendientes" },
            { value: "in_process", label: "En proceso" },
            { value: "received", label: "Recibidas" },
            { value: "drafted", label: "Borrador" },
            { value: "completed", label: "Completadas" },
            { value: "cancelled", label: "Canceladas" },
          ]}
          noMargin
        />
      </div>

      {/* Cliente */}
      <div className="mb-2">
        <label htmlFor="customer_name" className="block text-sm font-medium text-text-secondary">Cliente</label>
        <div className="relative mt-1">
          <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" /></svg>
          </div>
          <input
            id="customer_name"
            name="customer_name"
            type="text"
            placeholder="Buscar cliente"
            value={local.customer_name}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
          />
        </div>
      </div>

      {/* Transporte */}
      <div className="mb-2">
        <label htmlFor="carrier" className="block text-sm font-medium text-text-secondary">Transporte</label>
        <div className="relative mt-1">
          <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
            <svg className="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" /></svg>
          </div>
          <input
            id="carrier"
            name="carrier"
            type="text"
            placeholder="Carrier"
            value={local.carrier}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
          />
        </div>
      </div>

      {/* Asignado a (custom popover select) */}
      <AssignedUserSelect
        label="Asignado a"
        value={local.assigned_to}
        onChange={(val) => setLocal(prev => ({ ...prev, assigned_to: val }))}
        users={users}
      />

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

      {/* Botón Limpiar removido para simplificar UI */}
    </div>
  );
};

IntakeOrderFilter.propTypes = {
  value: PropTypes.object,
  onChange: PropTypes.func,
};

export default IntakeOrderFilter;
