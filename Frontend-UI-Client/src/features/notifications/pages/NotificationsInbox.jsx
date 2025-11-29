// src/features/notifications/pages/NotificationsInbox.jsx
import { useEffect, useMemo } from "react";
import Layout from "@/pages/Layout";
import Toolbar from "@/components/common/Toolbar";
import Spinner from "@/components/ui/Spinner";
// (Opcional) si querés mostrar errores de API en UI
// import ErrorMessage from "@/components/common/ErrorMessage";

import { useNotificationsStore } from "../stores/useNotificationsStore";

export default function NotificationsInbox() {
    const {
        items,
        loading,
        page,
        hasMore,
        fetchPage,
        markAsRead,
        markAllAsRead,
    } = useNotificationsStore((s) => ({
        items: s.items,
        loading: s.loading,
        page: s.page,
        hasMore: s.hasMore,
        fetchPage: s.fetchPage,
        markAsRead: s.markAsRead,
        markAllAsRead: s.markAllAsRead,
    }));

    const unreadCount = useMemo(
        () => items.reduce((acc, n) => (n.read ? acc : acc + 1), 0),
        [items]
    );

    useEffect(() => {
        // primera carga
        fetchPage(1);
    }, [fetchPage]);

    return (
        <Layout isLoading={false}>
            <div className="p-3 md:p-4 lg:p-6 mt-6">
                <Toolbar
                    title="Notificaciones"
                    titleRight={
                        <span className="text-sm text-slate-600">
                            No leídas:{" "}
                            <span className="font-semibold">{unreadCount}</span>
                        </span>
                    }
                    buttonText={unreadCount > 0 ? "Marcar todas como leídas" : undefined}
                    onButtonClick={unreadCount > 0 ? () => markAllAsRead() : undefined}
                />

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
                                    <div className="text-sm text-slate-700 mt-0.5">
                                        {n.message}
                                    </div>
                                )}

                                <div className="text-xs text-slate-500 mt-1">
                                    {new Date(n.created_at).toLocaleString()}
                                </div>

                                {/* (Opcional) Mostrar tipo si viene del backend */}
                                {n.type && (
                                    <div className="mt-1 text-[11px] text-slate-500 uppercase tracking-wide">
                                        {n.type}
                                    </div>
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
                </div>

                {/* Estados de carga / vacío / paginado */}
                <div className="mt-6 flex flex-col items-center">
                    {loading && (
                        <div className="flex items-center gap-2 text-slate-600">
                            <Spinner size="5" /> <span>Cargando…</span>
                        </div>
                    )}

                    {!loading && items.length === 0 && (
                        <div className="w-full text-center py-10 px-4 bg-white rounded-lg border text-slate-500">
                            No hay notificaciones.
                        </div>
                    )}

                    {!loading && hasMore && (
                        <button
                            className="mt-2 rounded border px-3 py-1.5 text-sm hover:bg-slate-50"
                            onClick={() => fetchPage(page + 1)}
                        >
                            Cargar más
                        </button>
                    )}
                </div>
            </div>
        </Layout>
    );
}
