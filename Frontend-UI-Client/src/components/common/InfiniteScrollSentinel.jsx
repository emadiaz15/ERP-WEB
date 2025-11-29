// src/components/common/InfiniteScrollSentinel.jsx
import React, { useEffect, useRef } from 'react';

const InfiniteScrollSentinel = ({
    onLoadMore,
    disabled,
    isLoadingMore,
    root,
    rootMargin = '100px',
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
            io.disconnect();
        };
    }, [onLoadMore, disabled, isLoadingMore, root, rootMargin]);

    return (
        <tr ref={ref}>
            <td colSpan="100%" className="py-4 text-center text-sm text-muted-foreground">
                {disabled
                    ? 'No hay más resultados'
                    : isLoadingMore
                        ? 'Cargando más...'
                        : 'Desplázate para cargar más'}
            </td>
        </tr>
    );
};

export default InfiniteScrollSentinel;
