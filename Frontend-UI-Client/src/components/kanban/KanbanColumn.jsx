import React from "react";
import PropTypes from "prop-types";

const colorMap = {
    warning: "bg-backgroud-100",
    success: "bg-backgroud-100",
    primary: "bg-backgroud-100",
    neutral: "bg-backgroud-100",
};

export default function KanbanColumn({
    title,
    count = 0,
    color = "neutral",
    children,
    onLoadMore,          // 👈 opcional
    hasNext = false,     // 👈 opcional
    isLoadingMore = false, // 👈 opcional
}) {
    const box = colorMap[color] || colorMap.neutral;
    const childCount = React.Children.count(children);
    const shouldScroll = childCount > 4;

    return (
        <section className={`rounded-2xl border ${box} p-1 min-h-[280px]`}>
            {/* Header */}
            <header className="flex items-center justify-between mb-3">
                <h2 className="text-base font-semibold text-text.primary">{title}</h2>
                <span className="text-xs px-2 py-1 rounded-full bg-white border text-text.secondary">
                    {count}
                </span>
            </header>

            {/* Contenido */}
            <div
                className={[
                    "space-y-3",
                    shouldScroll
                        ? "overflow-y-auto pr-1 max-h-[70vh] custom-thin-scroll"
                        : "overflow-visible",
                ].join(" ")}
            >
                {children}

                {/* Footer: botón "Cargar más" por columna */}
                {hasNext && (
                    <div className="pt-2">
                        <button
                            type="button"
                            onClick={onLoadMore}
                            disabled={isLoadingMore}
                            className="w-full text-sm border rounded-lg py-2 bg-white hover:bg-neutral-50 transition"
                        >
                            {isLoadingMore ? "Cargando…" : "Cargar más"}
                        </button>
                    </div>
                )}
            </div>
        </section>
    );
}

KanbanColumn.propTypes = {
    title: PropTypes.string.isRequired,
    count: PropTypes.number,
    color: PropTypes.oneOf(["warning", "success", "primary", "neutral"]),
    children: PropTypes.node,
    onLoadMore: PropTypes.func,
    hasNext: PropTypes.bool,
    isLoadingMore: PropTypes.bool,
};
