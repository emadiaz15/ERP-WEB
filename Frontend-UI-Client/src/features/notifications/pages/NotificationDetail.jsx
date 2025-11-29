import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import Layout from "@/pages/Layout";
import Spinner from "@/components/ui/Spinner";
import { useNotificationsStore } from "../stores/useNotificationsStore";
import { fetchNotificationById } from "../services/notifications.api";

export default function NotificationDetail() {
    const { id } = useParams();
    const navigate = useNavigate();

    const items = useNotificationsStore((s) => s.items);
    const markAsRead = useNotificationsStore((s) => s.markAsRead);

    const [notif, setNotif] = useState(null);
    const [loading, setLoading] = useState(true);
    const [err, setErr] = useState(null);

    const cached = useMemo(
        () => items.find((n) => String(n.id) === String(id)),
        [items, id]
    );

    const mountedRef = useRef(true);
    useEffect(() => {
        mountedRef.current = true;
        (async () => {
            try {
                setLoading(true);
                // usar cache inmediato para no “parpadear”
                if (cached) setNotif(cached);

                const data = await fetchNotificationById(id);
                if (!mountedRef.current) return;

                setNotif(data);

                // marcar como leída si no lo está
                if (data && data.id && !data.read) {
                    await markAsRead(data.id);
                }
            } catch (e) {
                if (mountedRef.current) setErr(e);
            } finally {
                if (mountedRef.current) setLoading(false);
            }
        })();

        return () => { mountedRef.current = false; };
    }, [id, cached, markAsRead]);

    const fmt = useMemo(
        () => new Intl.DateTimeFormat("es-AR", { dateStyle: "short", timeStyle: "short" }),
        []
    );

    return (
        <Layout isLoading={false}>
            <div className="p-3 md:p-4 lg:p-6 mt-6 max-w-3xl mx-auto">
                <div className="mb-4 flex items-center justify-between">
                    <h1 className="text-xl font-semibold">Detalle de notificación</h1>
                    <Link to="/notifications" className="text-sm text-blue-600 hover:underline">
                        ← Volver al historial
                    </Link>
                </div>

                {loading && (
                    <div className="bg-white border rounded-md p-6 flex items-center gap-2 text-slate-600">
                        <Spinner size="5" /> Cargando…
                    </div>
                )}

                {!loading && err && (
                    <div className="bg-red-50 border border-red-200 text-red-800 rounded-md p-4">
                        Ocurrió un error al cargar la notificación.
                    </div>
                )}

                {!loading && !err && notif && (
                    <div className="bg-white border rounded-md p-5 shadow-sm">
                        <div className="flex items-start justify-between">
                            <div>
                                <div className="text-sm text-slate-500">ID: {notif.id}</div>
                                <h2 className="text-lg font-semibold mt-1">
                                    {notif.title || "Notificación"}
                                </h2>
                                {notif.type && (
                                    <span className="inline-block mt-2 text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-700 uppercase tracking-wide">
                                        {notif.type}
                                    </span>
                                )}
                            </div>
                            <div className="text-xs text-slate-500">
                                {notif.created_at ? fmt.format(new Date(notif.created_at)) : null}
                            </div>
                        </div>

                        {notif.message && (
                            <p className="mt-4 text-slate-800">{notif.message}</p>
                        )}

                        {/* Detalle útil para órdenes de corte / payload */}
                        {notif.payload && (
                            <div className="mt-5 border-t pt-4 text-sm">
                                <div className="font-semibold mb-2">Datos adicionales</div>
                                <pre className="text-xs bg-slate-50 p-3 rounded overflow-x-auto">
                                    {JSON.stringify(notif.payload, null, 2)}
                                </pre>

                                {/* CTA específica si hay order_id */}
                                {notif.payload.order_id && (
                                    <button
                                        className="mt-3 inline-flex items-center text-sm rounded border px-3 py-1.5 hover:bg-slate-50"
                                        onClick={() => navigate(`/cutting-orders/${notif.payload.order_id}`)}
                                    >
                                        Ver orden de corte #{notif.payload.order_id}
                                    </button>
                                )}
                            </div>
                        )}

                        {/* Enlace destino si viene del backend */}
                        {notif.target_url && (
                            <div className="mt-4">
                                <button
                                    className="text-sm text-blue-600 hover:underline"
                                    onClick={() => navigate(notif.target_url)}
                                >
                                    Abrir enlace relacionado
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Layout>
    );
}
