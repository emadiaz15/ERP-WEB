import { XMarkIcon } from "@heroicons/react/24/outline";

const VARIANTS = {
    info: { box: "text-blue-800 border-blue-300 bg-blue-50 dark:bg-gray-800 dark:text-blue-400 dark:border-blue-800", btn: "text-white bg-blue-800 hover:bg-blue-900 focus:ring-blue-200 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800", ghost: "text-blue-800 border-blue-800 hover:bg-blue-900 hover:text-white focus:ring-blue-200 dark:hover:bg-blue-600 dark:border-blue-600 dark:text-blue-400 dark:hover:text-white dark:focus:ring-blue-800" },
    danger: { box: "text-red-800 border-red-300 bg-red-50 dark:bg-gray-800 dark:text-red-400 dark:border-red-800", btn: "text-white bg-red-800 hover:bg-red-900 focus:ring-red-300 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-800", ghost: "text-red-800 border-red-800 hover:bg-red-900 hover:text-white focus:ring-red-300 dark:hover:bg-red-600 dark:border-red-600 dark:text-red-500 dark:hover:text-white dark:focus:ring-red-800" },
    success: { box: "text-green-800 border-green-300 bg-green-50 dark:bg-gray-800 dark:text-green-400 dark:border-green-800", btn: "text-white bg-green-800 hover:bg-green-900 focus:ring-green-300 dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-green-800", ghost: "text-green-800 border-green-800 hover:bg-green-900 hover:text-white focus:ring-green-300 dark:hover:bg-green-600 dark:border-green-600 dark:text-green-400 dark:hover:text-white dark:focus:ring-green-800" },
    warning: { box: "text-yellow-800 border-yellow-300 bg-yellow-50 dark:bg-gray-800 dark:text-yellow-300 dark:border-yellow-800", btn: "text-white bg-yellow-800 hover:bg-yellow-900 focus:ring-yellow-300 dark:bg-yellow-300 dark:text-gray-800 dark:hover:bg-yellow-400 dark:focus:ring-yellow-800", ghost: "text-yellow-800 border-yellow-800 hover:bg-yellow-900 hover:text-white focus:ring-yellow-300 dark:hover:bg-yellow-300 dark:border-yellow-300 dark:text-yellow-300 dark:hover:text-gray-800 dark:focus:ring-yellow-800" },
    dark: { box: "text-gray-800 border-gray-300 bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300", btn: "text-white bg-gray-700 hover:bg-gray-800 focus:ring-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 dark:focus:ring-gray-800", ghost: "text-gray-800 border-gray-700 hover:bg-gray-800 hover:text-white focus:ring-gray-300 dark:border-gray-600 dark:hover:bg-gray-600 dark:focus:ring-gray-800 dark:text-gray-300" },
};

export default function NotificationToast({ notif, onView, onClose }) {
    const type = (notif?.type || "info").toLowerCase();
    const v = VARIANTS[type] ?? VARIANTS.info;

    return (
        <div
            role="alert"
            className={`p-4 mb-2 border rounded-lg shadow-sm ${v.box}`}
            aria-live="polite"
        >
            <div className="flex items-start gap-2">
                <svg className="shrink-0 w-4 h-4 mt-1" aria-hidden="true" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5ZM9.5 4a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM12 15H8a1 1 0 0 1 0-2h1v-3H8a1 1 0 0 1 0-2h2a1 1 0 0 1 1 1v4h1a1 1 0 0 1 0 2Z" />
                </svg>

                <div className="flex-1 min-w-0">
                    <h3 className="text-base font-medium line-clamp-1">
                        {notif?.title || "Notificación"}
                    </h3>
                    {notif?.message && (
                        <div className="mt-1 text-sm line-clamp-3">{notif.message}</div>
                    )}

                    <div className="mt-3 flex flex-wrap items-center gap-2">
                        {onView && (
                            <button
                                type="button"
                                onClick={onView}
                                className={`inline-flex items-center text-xs font-medium rounded-lg px-3 py-1.5 ${v.btn}`}
                            >
                                <svg className="me-2 h-3 w-3" aria-hidden="true" viewBox="0 0 20 14" fill="currentColor">
                                    <path d="M10 0C4.612 0 0 5.336 0 7c0 1.742 3.546 7 10 7 6.454 0 10-5.258 10-7 0-1.664-4.612-7-10-7Zm0 10a3 3 0 1 1 0-6 3 3 0 0 1 0 6Z" />
                                </svg>
                                Ver más
                            </button>
                        )}
                        <button
                            type="button"
                            onClick={onClose}
                            className={`inline-flex items-center text-xs font-medium rounded-lg px-3 py-1.5 border ${v.ghost}`}
                        >
                            Cerrar
                        </button>
                    </div>
                </div>

                <button
                    onClick={onClose}
                    className="p-1 rounded hover:bg-black/5 focus:outline-none"
                    aria-label="Cerrar"
                >
                    <XMarkIcon className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
