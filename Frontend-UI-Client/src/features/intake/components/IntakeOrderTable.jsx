// src/features/intake/components/IntakeOrderTable.jsx
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";
import { EyeIcon, PencilIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { useAuth } from "../../../context/AuthProvider";

// ================= Helpers =================
const safeDate = (v) => {
  if (!v) return null;
  const d = new Date(v);
  return isNaN(d.getTime()) ? null : d;
};

// Fecha y hora en formato dd/mm/aaaa HH:mm
const formatDateTime = (isoLike) => {
  const d = safeDate(isoLike);
  if (!d) return "—";
  try {
    const fecha = d.toLocaleDateString("es-AR");
    const hora = d.toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit", hour12: false });
    return `${fecha} ${hora}`;
  } catch {
    return d.toLocaleString();
  }
};

// Colores y etiquetas por estado (adaptable a flow_status de intake)
const STATUS_CONFIG = {
  pending: { color: "bg-amber-500", label: "Pendiente" },
  in_process: { color: "bg-primary-500", label: "En Proceso" },
  completed: { color: "bg-green-500", label: "Completada" },
  cancelled: { color: "bg-error-500", label: "Cancelada" },
  // intake-specific posibles
  received: { color: "bg-blue-500", label: "Recibida" },
  drafted: { color: "bg-gray-500", label: "Borrador" },
};

const getStatusConfig = (order) => {
  const raw = order?.flow_status || order?.workflow_status; // fallback por si comparte campo
  const cfg = STATUS_CONFIG[raw];
  if (cfg) return { ...cfg, display: order?.flow_status_display || order?.workflow_status_display || cfg.label };
  return {
    color: "bg-gray-500",
    label: "Desconocido",
    display: order?.flow_status_display || raw || "—",
  };
};

/** Fila-sentinela que dispara onLoadMore cuando entra en el viewport */
const SentinelRow = ({
  onLoadMore,
  disabled,
  isLoadingMore,
  root,
  colSpan = 100,
  rootMargin = "160px",
  className = "",
}) => {
  const ref = useRef(null);
  useEffect(() => {
    const el = ref.current;
    if (!el || disabled) return;
    const io = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting && !isLoadingMore) onLoadMore?.();
      },
      { root, rootMargin, threshold: 0 }
    );
    io.observe(el);
    return () => {
      try { io.unobserve(el); } catch { /* noop */ }
      io.disconnect();
    };
  }, [onLoadMore, disabled, isLoadingMore, root, rootMargin]);

  return (
    <tr ref={ref} className={className} aria-live="polite" aria-busy={isLoadingMore || undefined}>
      <td colSpan={colSpan} className="py-4 text-center text-sm text-muted-foreground">
        {disabled ? "No hay más resultados" : isLoadingMore ? "Cargando más..." : "Desplázate para cargar más"}
      </td>
    </tr>
  );
};

const IntakeOrderTable = ({
  orders = [],
  onView,
  onEdit,
  onDelete,
  onLoadMore,
  hasNextPage = false,
  isFetchingNextPage = false,
  loading = false,
}) => {
  const { user } = useAuth();
  const isStaff = !!user?.is_staff;

  // Orden: más recientes primero (creadas/modificadas)
  const sortedOrders = useMemo(() => {
    const arr = Array.isArray(orders) ? [...orders] : [];
    arr.sort((a, b) => {
      const ad = safeDate(a?.created_at);
      const bd = safeDate(b?.created_at);
      if (ad && bd && ad.getTime() !== bd.getTime()) return bd - ad;
      const am = safeDate(a?.modified_at);
      const bm = safeDate(b?.modified_at);
      if (am && bm && am.getTime() !== bm.getTime()) return bm - am;
      return (b?.id ?? 0) - (a?.id ?? 0);
    });
    return arr;
  }, [orders]);

  // Construir headers (alineados con estilo cutting)
  const headers = useMemo(
    () => [
      "Fecha y Hora",
      "Cliente",
      "Orden #",
      "Ítems",
      "Asignado a",
      "Transporte",
      "Notas",
      "Estado",
      "Acciones",
    ],
    []
  );

  // Helper asignado
  const resolveAssignedLabel = useCallback((o) => {
    const toTitle = (s) => s ? s.toString().toLowerCase().replace(/\b\w/g, c => c.toUpperCase()) : '';
    // 1. Si viene ya calculado y parece incluir espacio (nombre + apellido) lo usamos.
    if (o?.assigned_to_name) {
      const name = o.assigned_to_name.trim();
      // Si no contiene espacio pero tenemos campos separados, reconstruimos.
      if (name.includes(' ')) return name;
    }
    // 2. Campos aplanados (posible futura API): assigned_to_first_name / assigned_to_last_name
    if (o?.assigned_to_first_name || o?.assigned_to_last_name) {
      const full = `${toTitle(o.assigned_to_first_name || '')} ${toTitle(o.assigned_to_last_name || '')}`.trim();
      if (full) return full;
    }
    // 3. Estructura anidada assignment.assigned_to
    const nested = o?.assignment?.assigned_to;
    if (nested) {
      const full = `${toTitle(nested.first_name ?? '')} ${toTitle(nested.last_name ?? '')}`.trim();
      if (full) return full;
      return nested.username || nested.email || (nested.id ? `ID #${nested.id}` : '—');
    }
    // 4. Campo assigned_to_name simple (reconstruir mayúsculas)
    if (o?.assigned_to_name) return toTitle(o.assigned_to_name);
    // 5. Campo display genérico
    if (o?.assigned_to_display) return toTitle(o.assigned_to_display);
    // 6. Fallback a string simple
    if (typeof o?.assigned_to === 'string' && o.assigned_to.trim()) return o.assigned_to.trim();
    if (o?.assigned_to_id) return `ID #${o.assigned_to_id}`;
    return '—';
  }, []);

  const rows = useMemo(
    () => (sortedOrders || []).map((order) => {
      const statusCfg = getStatusConfig(order);
      const itemsCount =
        order?.items_count ?? (Array.isArray(order?.items) ? order.items.length : undefined) ?? "—";
      return {
        "Fecha y Hora (dd/mm/aaaa HH:mm)": (
          <div className="w-[150px] truncate text-xs" title={order?.created_at || ""}>
            {formatDateTime(order?.created_at)}
          </div>
        ),
        Cliente: (
          <div className="min-w-[160px] max-w-[240px] truncate" title={order?.customer_name || ""}>
            {order?.customer_name || "Sin cliente"}
          </div>
        ),
        "Orden #": (
          <div className="w-[80px] truncate text-center tabular-nums">{order?.order_number || order?.id || "—"}</div>
        ),
        Ítems: (
          <div className="w-[60px] text-center tabular-nums" title={`${itemsCount} ítems`}>
            {itemsCount}
          </div>
        ),
        "Asignado a": (
          <div className="w-[140px] truncate" title={resolveAssignedLabel(order)}>
            {resolveAssignedLabel(order)}
          </div>
        ),
        Transporte: (
          <div className="min-w-[120px] max-w-[160px] truncate" title={order?.carrier || ""}>
            {order?.carrier || "—"}
          </div>
        ),
        Notas: (
          <div className="min-w-[160px] max-w-[260px] truncate" title={order?.notes || ""}>
            {order?.notes || "—"}
          </div>
        ),
        Estado: (
          <div className="w-[110px] truncate">
            <span
              className={`inline-flex items-center gap-2 px-2 py-0.5 rounded-full text-white text-xs font-semibold ${statusCfg.color}`}
              title={statusCfg.display}
            >
              <span className="inline-block w-2 h-2 rounded-full bg-white/70" />
              {statusCfg.display || statusCfg.label}
            </span>
          </div>
        ),
        Acciones: (
          <div className="flex space-x-2 min-w-[200px]">
            <button
              onClick={() => onView?.(order)}
              className="bg-blue-500 p-2 rounded hover:bg-blue-600 transition-colors"
              aria-label="Ver detalles de la orden"
              title="Ver detalles"
            >
              <EyeIcon className="w-5 h-5 text-white" />
            </button>
            {isStaff && ["pending", "in_process", "drafted", "received"].includes(order?.flow_status || order?.workflow_status) && (
              <>
                <button
                  onClick={() => onEdit?.(order)}
                  className="bg-primary-500 p-2 rounded hover:bg-primary-600 transition-colors"
                  aria-label="Editar orden"
                  title="Editar"
                >
                  <PencilIcon className="w-5 h-5 text-white" />
                </button>
                <button
                  onClick={() => onDelete?.(order?.id)}
                  className="bg-red-500 p-2 rounded hover:bg-red-600 transition-colors"
                  aria-label="Eliminar orden"
                  title="Eliminar"
                >
                  <XMarkIcon className="w-5 h-5 text-white" />
                </button>
              </>
            )}
          </div>
        ),
      };
    }),
    [sortedOrders, isStaff, onView, onEdit, onDelete, resolveAssignedLabel]
  );

  // contenedor scrolleable (igual patrón cutting)
  const scrollRef = useRef(null);

  return (
    <div className="relative overflow-x-auto shadow-md sm:rounded-lg mt-2">
      <div ref={scrollRef} className="max-h-[480px] overflow-y-auto">
        <table className="w-full text-sm text-left text-text-primary">
          <thead className="sticky top-0 z-10 text-xs text-white uppercase bg-primary-500">
            <tr>
              {headers.map((h) => (
                <th key={h} className="px-6 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={headers.length} className="px-6 py-8 text-center text-muted-foreground">Cargando...</td>
              </tr>
            )}
            {!loading && rows.length === 0 && (
              <tr>
                <td colSpan={headers.length} className="px-6 py-8 text-center text-muted-foreground">Sin resultados</td>
              </tr>
            )}
            {!loading && rows.map((row, idx) => (
              <tr
                key={idx}
                className={`border-b transition-all hover:bg-primary-100 ${idx % 2 === 0 ? "bg-background-100" : "bg-background-200"}`}
              >
                {headers.map((h) => (
                  <td key={h} className="px-6 py-3">{row[h]}</td>
                ))}
              </tr>
            ))}

            {/* Sentinel final */}
            {!loading && rows.length > 0 && (
              <SentinelRow
                onLoadMore={onLoadMore}
                disabled={!hasNextPage}
                isLoadingNextPage={isFetchingNextPage}
                isLoadingMore={isFetchingNextPage}
                root={scrollRef.current}
                colSpan={headers.length}
              />
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

IntakeOrderTable.propTypes = {
  orders: PropTypes.array,
  onView: PropTypes.func,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  onLoadMore: PropTypes.func,
  hasNextPage: PropTypes.bool,
  isFetchingNextPage: PropTypes.bool,
  loading: PropTypes.bool,
};

export default IntakeOrderTable;
