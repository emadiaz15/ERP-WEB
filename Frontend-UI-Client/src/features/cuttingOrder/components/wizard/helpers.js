// src/features/cuttingOrder/components/wizard/helpers.js

/** Visual helpers **/
export const normalizeType = (t) => (t || "").toString().trim().toLowerCase();

export const getTypeLabel = (formType) => {
  const t = normalizeType(formType);
  if (t === "rollo" || t === "roll") return "Rollo";
  if (t === "bobina" || t === "coil") return "Bobina";
  return "Subproducto";
};

export const getDefaultImage = (formType) => {
  const t = normalizeType(formType);
  if (t === "rollo" || t === "roll") return "/rollo.png";
  if (t === "bobina" || t === "coil") return "/bobina.png";
  // Fallback seguro si no tenés /default.png
  return "/bobina.png";
};

/** Parsing robusto de números (soporta comas) */
export const toNumber = (val) => {
  if (val == null) return null;
  if (typeof val === "number") return Number.isFinite(val) ? val : null;
  if (typeof val === "string") {
    const s = val.trim();
    if (!s) return null;
    const n = parseFloat(s.replace(",", "."));
    return Number.isFinite(n) ? n : null;
  }
  // Objetos numéricos simples
  if (typeof val === "object" && "value" in val) {
    return toNumber(val.value);
  }
  return null;
};

/** Stock disponible: intenta nombres comunes (incluye anidados); fallback 0 */
export const getAvailableStock = (sp) => {
  const candidates = [
    sp?.available_stock_quantity,
    sp?.available_stock,
    sp?.current_stock_quantity,
    sp?.current_stock,
    sp?.stock_available,
    sp?.stock_quantity,
    sp?.stock?.quantity,            // anidado
    sp?.subproduct_stock?.quantity, // anidado
    sp?.stock,                      // por si viene plano
    sp?.initial_stock_quantity,     // último recurso
  ];

  for (const v of candidates) {
    const n = toNumber(v);
    if (n != null) return Math.max(0, n);
  }
  return 0;
};

/** DRF error pretty print */
export const stringifyServerError = (data) => {
  if (!data) return null;
  try {
    if (typeof data === "string") return data;
    if (typeof data.detail === "string") return data.detail;

    const parts = [];
    for (const [k, v] of Object.entries(data)) {
      if (Array.isArray(v)) {
        const flat = v
          .map((x) => (typeof x === "string" ? x : JSON.stringify(x)))
          .join(" | ");
        parts.push(`${k}: ${flat}`);
      } else if (typeof v === "object" && v !== null) {
        parts.push(`${k}: ${JSON.stringify(v)}`);
      } else {
        parts.push(`${k}: ${String(v)}`);
      }
    }
    return parts.join("\n");
  } catch {
    return JSON.stringify(data);
  }
};
