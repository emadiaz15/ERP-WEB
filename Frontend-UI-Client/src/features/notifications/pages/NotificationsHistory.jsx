import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import Layout from "@/pages/Layout";
import Toolbar from "@/components/common/Toolbar";
import Spinner from "@/components/ui/Spinner";
import { useNotificationsStore } from "../stores/useNotificationsStore";
import FormSelect from "@/components/ui/form/FormSelect";

// Hook pequeño para infinite scroll con IntersectionObserver
function useInfiniteScroll({ enabled, loading, hasMore, onLoadMore }) {
    const sentinelRef = useRef(null);
    const lockRef = useRef(false);

    useEffect(() => {
        if (!enabled || !hasMore || loading) return;
        const el = sentinelRef.current;
        if (!el) return;

        const observer = new IntersectionObserver(
            (entries) => {
                const [entry] = entries;
                if (entry.isIntersecting && !lockRef.current && !loading && hasMore) {
                    lockRef.current = true;
                    onLoadMore?.().finally(() => {
                        lockRef.current = false;
                    });
                }
            },
            { rootMargin: "200px" }
        );

        observer.observe(el);
        return () => observer.disconnect();
    }, [enabled, loading, hasMore, onLoadMore]);

    return sentinelRef;
}

export default function NotificationsHistory() {
    // ✅ selectores independientes (evita objetos nuevos por render)
    const items = useNotificationsStore((s) => s.items);
    const loading = useNotificationsStore((s) => s.loading);
    const page = useNotificationsStore((s) => s.page);
    const hasMore = useNotificationsStore((s) => s.hasMore);
    const fetchPage = useNotificationsStore((s) => s.fetchPage);
    const markAsRead = useNotificationsStore((s) => s.markAsRead);
    const markAllAsRead = useNotificationsStore((s) => s.markAllAsRead);
    const resetPagination = useNotificationsStore((s) => s.resetPagination); // si existe en tu store
    const [total, setTotal] = useState(null);

    // Filtros locales
    const [readFilter, setReadFilter] = useState("all"); // all | unread | read
    const [typeFilter, setTypeFilter] = useState("");

    // Guard para primer fetch y para evitar bucles si las refs de funciones cambian tras cada set del store.
    const didInitRef = useRef(false);
    const prevFiltersRef = useRef({ readFilter, typeFilter });
    useEffect(() => {
        const filtersChanged =
            prevFiltersRef.current.readFilter !== readFilter ||
            prevFiltersRef.current.typeFilter !== typeFilter;
        if (!didInitRef.current || filtersChanged) {
            const read =
                readFilter === "all" ? undefined : readFilter === "read" ? true : false;
            prevFiltersRef.current = { readFilter, typeFilter };
            (async () => {
                resetPagination?.();
                const data = await fetchPage(1, { read, type: typeFilter || undefined, force: true });
                if (data && typeof data.count === "number") setTotal(data.count); else setTotal(null);
            })();
            didInitRef.current = true;
        }
    // ONLY re-run when the filter values actually change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [readFilter, typeFilter]);

    const onLoadMore = useCallback(async () => {
        if (!hasMore || loading) return;
        const read =
            readFilter === "all" ? undefined : readFilter === "read" ? true : false;
        const data = await fetchPage(page + 1, { read, type: typeFilter || undefined });
        if (data && typeof data.count === "number") setTotal(data.count);
    }, [page, readFilter, typeFilter, fetchPage, hasMore, loading]);

    const sentinelRef = useInfiniteScroll({
        enabled: true,
        loading,
        hasMore,
        onLoadMore,
    });

    const unreadCount = useMemo(
        () => items.reduce((acc, n) => (n.read ? acc : acc + 1), 0),
        [items]
    );

    // Tipos dinámicos vistos en el historial
    const types = useMemo(
        () => Array.from(new Set(items.map((n) => n.type).filter(Boolean))).sort(),
        [items]
    );

    // Formateo de fecha local (es-AR)
    const fmt = useMemo(
        () =>
            new Intl.DateTimeFormat("es-AR", {
                dateStyle: "short",
                timeStyle: "short",
            }),
        []
    );

    return (
        <Layout isLoading={false}>
            <div className="p-3 md:p-4 lg:p-6 mt-6 max-w-4xl mx-auto">
                <Toolbar
                    title="Historial de notificaciones"
                    titleRight={
                        <span className="text-sm text-slate-600">
                            Total: <span className="font-semibold">{total !== null ? total : "…"}</span>
                            {" | "}
                            No leídas: <span className="font-semibold">{unreadCount}</span>
                        </span>
                    }
                    buttonText={unreadCount > 0 ? "Marcar todas como leídas" : undefined}
                    onButtonClick={
                        unreadCount > 0
                            ? async () => {
                                await markAllAsRead();
                                const read =
                                    readFilter === "all"
                                        ? undefined
                                        : readFilter === "read"
                                            ? true
                                            : false;
                                resetPagination?.();
                                const data = await fetchPage(1, { read, type: typeFilter || undefined });
                                if (data && typeof data.count === "number") setTotal(data.count);
                            }
                            : undefined
                    }
                />

                {/* Filtros */}
                <div className="mt-4 bg-white border rounded-md p-3 flex flex-col items-center gap-3">
                    <div className="flex flex-row items-center gap-4 w-full justify-center mt-2">
                        <FormSelect
                            name="readFilter"
                            value={readFilter}
                            onChange={(e) => setReadFilter(e.target.value)}
                            options={[
                                { value: "all", label: "Todas" },
                                { value: "unread", label: "No leídas" },
                                { value: "read", label: "Leídas" },
                            ]}
                            className="min-w-[120px]"
                        />
                        <FormSelect
                            name="typeFilter"
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                            options={[
                                { value: "", label: "Todos los tipos" },
                                ...types.map((t) => ({ value: t, label: t })),
                            ]}
                            className="min-w-[140px]"
                        />
                    </div>

                    {loading && (
                        <div className="flex items-center gap-2 text-slate-600">
                            <Spinner size="5" /> <span>Cargando…</span>
                        </div>
                    )}
                </div>

                {/* Lista */}
                <div className="mt-4 space-y-2">
                    {items.map((n) => (
                        <div
                            key={n.id}
                            className={`border rounded-md p-3 bg-white shadow-sm flex items-start justify-between ${!n.read ? "border-yellow-300" : "border-slate-200"
                                }`}
                        >
                            <div className="pr-4">
                                <div className="flex items-center gap-2">
                                    <div className="font-semibold text-slate-900">
                                        {n.title || "Notificación"}
                                    </div>
                                    {!n.read && (
                                        <span className="ml-1 text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">
                                            No leída
                                        </span>
                                    )}
                                </div>

                                {n.message && (
                                    <div className="text-sm text-slate-700 mt-0.5">{n.message}</div>
                                )}

                                <div className="text-xs text-slate-500 mt-1">
                                    {n.created_at ? fmt.format(new Date(n.created_at)) : null}
                                </div>

                                {n.type && (
                                    <div className="mt-1 text-[11px] text-slate-500 uppercase tracking-wide">
                                        {n.type}
                                    </div>
                                )}

                                {/* Si tu backend envía un URL relacionado (opcional) */}
                                {n.target_url && (
                                    <a
                                        className="mt-2 inline-block text-sm text-blue-600 hover:underline"
                                        href={n.target_url}
                                    >
                                        Ver detalle
                                    </a>
                                )}
                            </div>

                            {!n.read && (
                                <button
                                    className="text-sm text-blue-600 hover:underline shrink-0"
                                    onClick={() => markAsRead(n.id)}
                                >
                                    Marcar como leída
                                </button>
                            )}
                        </div>
                    ))}

                    {/* Estado vacío */}
                    {!loading && items.length === 0 && (
                        <div className="w-full text-center py-10 px-4 bg-white rounded-lg border text-slate-500">
                            No hay notificaciones con los filtros actuales.
                        </div>
                    )}

                    {/* Sentinel para infinite scroll */}
                    <div
                        ref={sentinelRef}
                        className="h-8 w-full"
                        style={{ display: hasMore && !loading ? undefined : "none" }}
                    />
                </div>

                {/* Botón alternativo por si el observer no dispara (accesibilidad) */}
                {!loading && hasMore && (
                    <div className="mt-4 flex justify-center">
                        <button
                            className="rounded border px-3 py-1.5 text-sm hover:bg-slate-50"
                            onClick={onLoadMore}
                            disabled={!hasMore}
                        >
                            Cargar más
                        </button>
                    </div>
                )}
            </div>
        </Layout>
    );
}
