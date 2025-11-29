import { useEffect, useMemo, useRef } from "react";
import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { BellIcon } from "@heroicons/react/24/outline";
import { Link, useNavigate } from "react-router-dom";
import { useNotificationsStore } from "@/features/notifications/stores/useNotificationsStore";
import { useCuttingOrderModalStore } from "@/features/cuttingOrder/store/useCuttingOrderModalStore";
import React from 'react';

export default function NotificationBell() {
    const navigate = useNavigate();

    const unreadCount = useNotificationsStore((s) => s.unreadCount);
    const items = useNotificationsStore((s) => s.items);
    const fetchPage = useNotificationsStore((s) => s.fetchPage);
    const markAsRead = useNotificationsStore((s) => s.markAsRead);
    const markAllAsRead = useNotificationsStore((s) => s.markAllAsRead);
    // refreshUnreadCount eliminado: contador derivado localmente

    // Prefetch 1 sola vez
    const didPrefetchRef = useRef(false);
    useEffect(() => {
        if (didPrefetchRef.current) return;
        didPrefetchRef.current = true;
        // Bootstrap global ya hizo el primer fetch; aquí sólo aseguramos si faltan datos
        if (!items.length) fetchPage(1, { force: true });
    }, [fetchPage, items.length]);

    // Refrescar al volver a la pestaña
    useEffect(() => {
        const onFocusOrShow = () => {
            if (document.hidden) return;
            // ✅ refresco sin page_size para no pisar con 5
            fetchPage(1, { force: true });
        };
        window.addEventListener("focus", onFocusOrShow);
        document.addEventListener("visibilitychange", onFocusOrShow);
        return () => {
            window.removeEventListener("focus", onFocusOrShow);
            document.removeEventListener("visibilitychange", onFocusOrShow);
        };
    }, [fetchPage]);

    // 🔒 “últimas 5” por created_at DESC, independientemente de la paginación
    const recent = useMemo(() => {
        const sorted = [...items].sort((a, b) => {
            const ta = a?.created_at ? new Date(a.created_at).getTime() : 0;
            const tb = b?.created_at ? new Date(b.created_at).getTime() : 0;
            return tb - ta;
        });
        return sorted.slice(0, 5);
    }, [items]);

    const notifKey = (n, idx) =>
        String(n?.id ?? n?.uuid ?? n?._id ?? `${n?.created_at ?? "ts"}-${idx}`);

    // ✅ navegación robusta para target_url (externo vs interno)
    const go = (url) => {
        try {
            const u = new URL(url, window.location.origin);
            if (u.origin !== window.location.origin) {
                return window.open(u.href, "_blank", "noopener");
            }
            return navigate(u.pathname + u.search + u.hash);
        } catch {
            // si no parsea como URL, intentamos con navigate tal cual
            return navigate(url);
        }
    };

    const openCuttingOrderModal = useCuttingOrderModalStore((s) => s.open);
    const handleClickNotif = async (n) => {
        if (!n.read && n.id) {
            try {
                await markAsRead(n.id);
                // await refreshUnreadCount().catch(() => { }); // refuerzo
            } catch { }
        }

        // Si es una orden de corte, navega a la lista y pide abrir el modal
        if (n?.payload?.order_id) {
            openCuttingOrderModal(n.payload.order_id);
            return;
        }
        if (n?.target_url) {
            go(n.target_url);
            return;
        }
        if (n?.id) {
            navigate(`/notifications/${n.id}`);
            return;
        }
        navigate("/notifications");
    };

    return (
        <Menu as="div" className="relative">
            <MenuButton
                className="relative rounded-full bg-primary-500 p-1 text-neutral-50 hover:text-white focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-primary-500 hover:bg-primary-600 transition-all"
                title="Ver notificaciones"
                aria-label="Ver notificaciones"
                tabIndex={0}
                onClick={() => {
                    fetchPage(1, { force: true });
                }}
                onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                        fetchPage(1, { force: true });
                    }
                }}
            >
                <span className="sr-only">Ver notificaciones</span>
                <BellIcon className="h-6 w-6" aria-hidden="true" />
                {unreadCount > 0 && (
                    <span
                        aria-label={`${unreadCount} notificaciones sin leer`}
                        className="absolute -top-1 -right-1 min-w-[20px] h-5 px-1 flex items-center justify-center rounded-full bg-error-500 text-white text-[10px] font-semibold"
                    >
                        {unreadCount > 99 ? "99+" : unreadCount}
                    </span>
                )}
            </MenuButton>

            <MenuItems
                anchor={{ to: "bottom end", gap: 2 }}
                className="absolute right-0 z-50 mt-6 w-96 origin-top-right rounded-md bg-white py-2 shadow-lg ring-1 ring-black/5 focus:outline-none"
            >
                <div className="px-3 pb-2 flex items-center justify-between">
                    <div className="font-semibold">Notificaciones</div>
                    <button
                        className="text-xs text-blue-600 hover:underline border border-blue-200 rounded px-2 py-1 ml-2"
                        onClick={async () => {
                            await markAllAsRead();
                            // await refreshUnreadCount().catch(() => { }); // refuerzo
                        }}
                        tabIndex={0}
                        aria-label="Marcar todas como leídas"
                    >
                        Marcar todas como leídas
                    </button>
                </div>

                <div className="max-h-96 overflow-y-auto">
                    {recent.length === 0 && (
                        <div className="px-3 py-6 text-sm text-neutral-500">
                            No hay notificaciones
                        </div>
                    )}

                    {recent.map((n, idx) => (
                        <MenuItem key={notifKey(n, idx)}>
                            {({ active }) => (
                                <button
                                    className={`w-full text-left px-3 py-2 border-t text-sm ${active ? "bg-neutral-100" : ""}`}
                                    onClick={() => handleClickNotif(n)}
                                    title={n.message}
                                    tabIndex={0}
                                    aria-label={n.title || "Notificación"}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter" || e.key === " ") {
                                            handleClickNotif(n);
                                        }
                                    }}
                                >
                                    <div className="flex items-start gap-2">
                                        {!n.read && (
                                            <span
                                                aria-hidden
                                                className="mt-1 inline-block h-2 w-2 rounded-full bg-blue-600"
                                            />
                                        )}
                                        <div className="flex-1">
                                            <div className="font-medium line-clamp-1">
                                                {n.title || "Notificación"}
                                            </div>
                                            <div className="text-xs text-slate-600 line-clamp-2">
                                                {n.message}
                                            </div>
                                            <div className="text-[11px] text-slate-400 mt-1">
                                                {n.created_at
                                                    ? new Date(n.created_at).toLocaleString()
                                                    : ""}
                                            </div>
                                        </div>
                                    </div>
                                </button>
                            )}
                        </MenuItem>
                    ))}
                </div>

                <div className="px-3 pt-2">
                    <Link
                        to="/notifications"
                        className="block w-full text-center text-sm text-blue-600 hover:underline py-2"
                        tabIndex={0}
                        aria-label="Ver todas las notificaciones"
                    >
                        Ver todas
                    </Link>
                </div>
            </MenuItems>
        </Menu>
    );
}
