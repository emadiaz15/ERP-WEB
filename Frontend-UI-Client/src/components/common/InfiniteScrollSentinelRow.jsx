// src/components/common/InfiniteScrollSentinelRow.jsx
import React, { useEffect, useRef } from 'react';

const InfiniteScrollSentinelRow = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,                    // contenedor con scroll (HTMLElement)
    rootMargin = '120px',    // dispara antes de llegar al fondo
    colSpan = 100,
    className = '',
}) => {
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el || disabled) return;

        const io = new IntersectionObserver(
            (entries) => {
                const [entry] = entries;
                if (entry.isIntersecting && !isLoadingMore) {
                    onLoadMore();
                }
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
        <tr ref={ref} className={className} aria-live="polite">
            <td colSpan={colSpan} className="py-4 text-center text-sm text-muted-foreground">
                {disabled
                    ? 'No hay más resultados'
                    : isLoadingMore
                        ? 'Cargando más...'
                        : 'Desplázate para cargar más'}
            </td>
        </tr>
    );
};

export default InfiniteScrollSentinelRow;
