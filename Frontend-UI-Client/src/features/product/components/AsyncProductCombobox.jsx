import React, { useEffect, useMemo, useRef, useState, useCallback } from "react";
import PropTypes from "prop-types";
import { djangoApi } from "@/api/clients";
import { getCached, setCached } from "@/utils/httpCache";

const TTL = 30_000;
// Usa el que corresponda a tu baseURL. Si tu backend está en /api/v1/products/,
// y tu axios ya apunta a /api/v1, entonces esto debe ser "/products/".
const BASE_URL = "inventory/products/"; // <-- deja tu valor actual si te funciona

function buildUrl(base, params = {}) {
    try {
        const hasProtocol = /^https?:\/\//i.test(base);
        if (hasProtocol) {
            const u = new URL(base);
            Object.entries(params).forEach(([k, v]) => {
                if (v !== undefined && v !== null && v !== "") u.searchParams.set(k, v);
            });
            return u.toString();
        }
        const [path, existingQuery] = base.split("?");
        const sp = new URLSearchParams(existingQuery || "");
        Object.entries(params || {}).forEach(([k, v]) => {
            if (v !== undefined && v !== null && v !== "") sp.set(k, v);
        });
        const qs = sp.toString();
        return qs ? `${path}?${qs}` : path;
    } catch {
        const qs = new URLSearchParams(
            Object.fromEntries(
                Object.entries(params || {}).filter(([, v]) => v !== undefined && v !== null && v !== "")
            )
        ).toString();
        return qs ? `${base}?${qs}` : base;
    }
}

function normalizeList(data) {
    if (data && Array.isArray(data.results)) return { results: data.results, next: data.next ?? null };
    if (Array.isArray(data)) return { results: data, next: null };
    return { results: data ? [data] : [], next: null };
}

async function fetchPage({ q, pageSize = 20 }) {
    const params = { status: true, has_subproducts: true, page_size: pageSize };
    if (q && q.trim()) {
        const t = q.trim();
        const isDigits = /^[0-9]+$/.test(t);
        if (isDigits) params.code = t;
        else params.name = t;
    }
    const url = buildUrl(BASE_URL, params);
    const cached = getCached(url, TTL);
    if (cached) return normalizeList(cached);
    const { data } = await djangoApi.get(url);
    setCached(url, data);
    return normalizeList(data);
}

async function fetchNext(nextUrl) {
    if (!nextUrl) return { results: [], next: null };
    const cached = getCached(nextUrl, TTL);
    if (cached) return normalizeList(cached);
    const { data } = await djangoApi.get(nextUrl);
    setCached(nextUrl, data);
    return normalizeList(data);
}

async function fetchById(id) {
    const url = `/products/${id}/`;
    const cached = getCached(url, TTL);
    if (cached) return cached;
    const { data } = await djangoApi.get(url);
    setCached(url, data);
    return data;
}

export default function AsyncProductCombobox({
    label = "Producto (con subproductos)",
    placeholder = "Escribe código o nombre…",
    value,
    onChange,
    disabled = false,
    autoFocus = false,
}) {
    const [query, setQuery] = useState("");
    const [opts, setOpts] = useState([]);
    const [next, setNext] = useState(null);
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [loadingMore, setLoadingMore] = useState(false);

    const debRef = useRef(null);
    const listRef = useRef(null);
    const fetchingRef = useRef(false);

    const mergeResults = useCallback((prev, incoming) => {
        const map = new Map(prev.map((p) => [p.id, p]));
        incoming.forEach((p) => map.set(p.id, p));
        return Array.from(map.values());
    }, []);

    // Busca pero YA NO abre el dropdown automáticamente.
    useEffect(() => {
        if (debRef.current) clearTimeout(debRef.current);
        debRef.current = setTimeout(async () => {
            try {
                setLoading(true);
                const { results, next } = await fetchPage({ q: query, pageSize: 20 });
                setOpts(results);
                setNext(next);
                // <- NO setOpen(true) aquí
            } catch (e) {
                console.error("[AsyncProductCombobox] fetch error:", e?.response?.data || e.message);
                setOpts([]);
                setNext(null);
            } finally {
                setLoading(false);
            }
        }, 250);
        return () => clearTimeout(debRef.current);
    }, [query]);

    // Cargar item por id para mostrar etiqueta si ya viene seleccionado
    useEffect(() => {
        if (!value) return;
        const found = opts.find((o) => String(o.id) === String(value));
        if (found) {
            if (!query) setQuery(`${found.code ?? ""}${found.name ? ` — ${found.name}` : ""}`.trim());
            return;
        }
        let cancelled = false;
        (async () => {
            try {
                if (query) return;
                const data = await fetchById(value);
                if (cancelled || !data) return;
                if (data?.has_subproducts) {
                    setQuery(`${data.code ?? ""}${data.name ? ` — ${data.name}` : ""}`.trim());
                }
            } catch { }
        })();
        return () => { cancelled = true; };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [value]);

    // Scroll infinito
    const onScroll = useCallback(async () => {
        if (!listRef.current || !next || loadingMore || fetchingRef.current) return;
        const el = listRef.current;
        const threshold = 48;
        const reachedBottom = el.scrollTop + el.clientHeight >= el.scrollHeight - threshold;
        if (!reachedBottom) return;
        try {
            fetchingRef.current = true;
            setLoadingMore(true);
            const { results, next: nextPage } = await fetchNext(next);
            setOpts((prev) => mergeResults(prev, results));
            setNext(nextPage);
        } catch (e) {
            console.error("[AsyncProductCombobox] fetch next error:", e?.response?.data || e.message);
        } finally {
            setLoadingMore(false);
            fetchingRef.current = false;
        }
    }, [next, loadingMore, mergeResults]);

    const selectedOption = useMemo(
        () => opts.find((o) => String(o.id) === String(value)),
        [opts, value]
    );

    const handlePick = (opt) => {
        onChange?.(String(opt.id));
        setQuery(`${opt.code ?? ""}${opt.name ? ` — ${opt.name}` : ""}`.trim());
        setOpen(false); // <- cerrar siempre al elegir
    };

    // Asegura datos si el usuario abre por primera vez con lista vacía
    const ensureLoadedOnOpen = useCallback(async () => {
        setOpen(true);
        if (opts.length === 0 && !loading) {
            try {
                setLoading(true);
                const { results, next } = await fetchPage({ q: query, pageSize: 20 });
                setOpts(results);
                setNext(next);
            } catch (e) {
                console.error("[AsyncProductCombobox] initial open fetch error:", e?.response?.data || e.message);
            } finally {
                setLoading(false);
            }
        }
    }, [opts.length, loading, query]);

    // Cerrar al presionar ESC
    const onKeyDown = (e) => {
        if (e.key === "Escape") setOpen(false);
    };

    // Cerrar al perder foco (con un pequeño delay para permitir click en items)
    const blurTimeout = useRef(null);
    const onBlur = () => {
        blurTimeout.current = setTimeout(() => setOpen(false), 100);
    };
    const onFocusContainer = () => {
        if (blurTimeout.current) clearTimeout(blurTimeout.current);
    };

    return (
        <div className="w-full" onFocus={onFocusContainer} onBlur={onBlur}>
            {label && (
                <label className="block text-sm font-medium text-text-secondary mb-1">
                    {label}
                </label>
            )}

            <div className="relative">
                <input
                    type="text"
                    autoFocus={autoFocus}
                    disabled={disabled}
                    className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                    placeholder={placeholder}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={ensureLoadedOnOpen}
                    onKeyDown={onKeyDown}
                />

                {open && (
                    <div
                        ref={listRef}
                        onScroll={onScroll}
                        className="absolute z-50 mt-1 w-full bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto"
                    >
                        {loading && opts.length === 0 ? (
                            <div className="py-2 px-3 text-sm text-gray-500">Buscando…</div>
                        ) : opts.length === 0 ? (
                            // Ya no verás "Sin resultados" después de seleccionar, porque setOpen(false) en handlePick
                            <div className="py-2 px-3 text-sm text-gray-500">Sin resultados</div>
                        ) : (
                            <ul className="py-1">
                                {opts.map((p) => (
                                    <li
                                        key={p.id}
                                        className="px-3 py-2 text-sm hover:bg-primary-50 cursor-pointer flex items-center justify-between"
                                        onMouseDown={() => handlePick(p)}
                                    >
                                        <span className="truncate">
                                            <span className="font-medium">{p.code}</span>
                                            {p.name ? ` — ${p.name}` : ""}
                                        </span>
                                        {p.has_subproducts ? (
                                            <span className="ml-2 text-xs rounded px-2 py-0.5 bg-emerald-100 text-emerald-700">
                                                con subproductos
                                            </span>
                                        ) : null}
                                    </li>
                                ))}
                                {loadingMore && (
                                    <li className="px-3 py-2 text-sm text-gray-500">Cargando más…</li>
                                )}
                            </ul>
                        )}
                    </div>
                )}
            </div>

            <p className="mt-1 text-xs text-gray-500">
                Mostrando sólo productos <strong>activos con subproductos</strong>.
            </p>
        </div>
    );
}

AsyncProductCombobox.propTypes = {
    label: PropTypes.string,
    placeholder: PropTypes.string,
    value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    onChange: PropTypes.func.isRequired,
    disabled: PropTypes.bool,
    autoFocus: PropTypes.bool,
};
