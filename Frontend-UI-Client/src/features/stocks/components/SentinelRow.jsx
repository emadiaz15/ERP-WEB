import React, { useRef } from "react";

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

    React.useEffect(() => {
        const el = ref.current;
        if (!el || disabled) return;

        const io = new window.IntersectionObserver(
            (entries) => {
                const [entry] = entries;
                if (entry.isIntersecting && !isLoadingMore) onLoadMore();
            },
            { root, rootMargin, threshold: 0 }
        );

        io.observe(el);
        return () => {
            try { io.unobserve(el); } catch { }
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

export default SentinelRow;
