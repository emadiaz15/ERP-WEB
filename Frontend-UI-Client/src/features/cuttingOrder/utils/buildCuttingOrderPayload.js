// src/features/cuttingOrder/utils/buildCuttingOrderPayload.js
// -----------------------------------------------------------------------------
// ÚNICA fuente de verdad para formateo/normalización de payloads de CuttingOrder
// - toDecimalString / compact (helpers internos)
// - sanitizeCreateData  → para CREATE (requiere quantity_to_cut, permite order_number)
// - sanitizeUpdateData  → para UPDATE (NO envía order_number)
// - buildCreateCuttingOrderPayload / buildUpdateCuttingOrderPayload (wrappers)
// - buildCuttingOrderPayload(params, {mode})               (proxy)
// -----------------------------------------------------------------------------

/** Convierte números/strings a string decimal con 2 decimales (evita flotantes JS). */
function toDecimalString(val) {
  if (val === null || val === undefined) return undefined;
  const s = String(val).trim();
  if (s === "") return undefined;
  const n = Number(s.replace(",", ".")); // por si viene "100,5"
  if (Number.isFinite(n)) return n.toFixed(2);
  return s; // fallback: ya es string decimal válido
}

/** Limpia objeto removiendo undefined/null/"" (shallow). */
function compact(obj) {
  return Object.fromEntries(
    Object.entries(obj || {}).filter(([, v]) => v !== undefined && v !== null && v !== "")
  );
}

/**
 * Sanea payload de creación. Requiere quantity_to_cut (string decimal).
 * Permite: product, order_number, customer, assigned_to, operator_can_edit_items, workflow_status, items.
 */
export function sanitizeCreateData(input = {}) {
  const base = compact({
    product: input.product,                 // PK
    order_number: input.order_number,       // int (create only)
    customer: input.customer,
    assigned_to: input.assigned_to ?? null, // PK o null
    operator_can_edit_items: input.operator_can_edit_items ?? false,
    workflow_status: input.workflow_status ?? 'pending',
  });

  // quantity_to_cut obligatorio → string decimal
  const qtc = toDecimalString(input.quantity_to_cut);
  if (!qtc) throw new Error("quantity_to_cut is required");

  const items = Array.isArray(input.items)
    ? input.items
        .filter((it) => it && it.subproduct != null && it.cutting_quantity != null)
        .map((it) => ({
          subproduct: Number(it.subproduct),
          cutting_quantity: toDecimalString(it.cutting_quantity),
        }))
    : undefined;

  return compact({
    ...base,
    quantity_to_cut: qtc,
    ...(items ? { items } : {}),
  });
}

/**
 * Sanea payload de actualización. NO envía order_number.
 * Permite cambiar: customer, workflow_status, assigned_to, product, operator_can_edit_items, quantity_to_cut?, items?
 */
export function sanitizeUpdateData(updateData = {}) {
  const clean = compact({
    customer: updateData.customer,
    workflow_status: updateData.workflow_status,         // 'pending' | 'in_process' | 'completed' | 'cancelled'
    assigned_to: updateData.assigned_to,                 // PK
    product: updateData.product,                         // PK
    operator_can_edit_items: updateData.operator_can_edit_items,
    // order_number: ❌ no enviar en update
  });

  // quantity_to_cut opcional en update → string decimal
  if (
    updateData.quantity_to_cut !== undefined &&
    updateData.quantity_to_cut !== null &&
    updateData.quantity_to_cut !== ""
  ) {
    clean.quantity_to_cut = toDecimalString(updateData.quantity_to_cut);
  }

  if (Array.isArray(updateData.items)) {
    clean.items = updateData.items
      .filter((it) => it && it.subproduct != null && it.cutting_quantity != null)
      .map((it) => ({
        subproduct: Number(it.subproduct),
        cutting_quantity: toDecimalString(it.cutting_quantity),
      }));
  }

  return clean;
}

/** Create payload (atajo) */
export const buildCreateCuttingOrderPayload = (params) => sanitizeCreateData(params);
/** Update payload (atajo, NO incluye order_number) */
export const buildUpdateCuttingOrderPayload = (params) => sanitizeUpdateData(params);
/** Único helper con modo explícito */
export const buildCuttingOrderPayload = (params = {}, { mode = "create" } = {}) =>
  mode === "create" ? sanitizeCreateData(params) : sanitizeUpdateData(params);

export default buildCuttingOrderPayload;
