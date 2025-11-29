// src/features/category/components/CategoryPicker.jsx
import React, { useEffect, useRef, useState } from "react";
import { useInfinitePageQuery } from "@/hooks/useInfinitePageQuery";
import { categoryKeys } from "@/features/category/utils/queryKeys";

export default function CategoryPicker({
    id = "category-input",
    name = "categoryInput",
    value,
    onChange,
    selectCategory,
    selectedId,
    isOpen,
}) {
    const [searchText, setSearchText] = useState("");
    const [open, setOpen] = useState(false);
    const listRef = useRef(null);

    // Debounce 250ms sobre el value controlado
    useEffect(() => {
        const t = setTimeout(() => setSearchText((value ?? "").trim()), 250);
        return () => clearTimeout(t);
    }, [value]);

    const {
        items: categories,
        isLoading,
        isFetchingNextPage,
        hasNextPage,
        fetchNextPage,
    } = useInfinitePageQuery({
        key: categoryKeys.list({ name: searchText }),
        url: "/inventory/categories/",
        params: { name: searchText || undefined, status: true },
        pageSize: 20,
        enabled: !!isOpen, // solo carga cuando el componente está visible
    });

    const handleScroll = () => {
        if (isFetchingNextPage || !hasNextPage) return;
        const el = listRef.current;
        if (!el) return;
        if (el.scrollHeight - el.scrollTop - el.clientHeight < 10) {
            fetchNextPage();
        }
    };

    const handleFocus = () => setOpen(true);
    const handleBlur = () => setTimeout(() => setOpen(false), 100);
    const handleKeyDown = (e) => {
        if (e.key === "Escape") {
            setOpen(false);
            e.currentTarget.blur();
        }
    };

    return (
        <div className="relative mt-1">
            <input
                id={id}
                name={name}
                type="text"
                role="combobox"
                aria-expanded={open}
                aria-controls={`${id}-listbox`}
                aria-autocomplete="list"
                value={value}
                onChange={onChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                onKeyDown={handleKeyDown}
                autoComplete="off"
                placeholder="Busca y selecciona una categoría"
                className="mt-1 block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
            />

            {open && (
                <ul
                    id={`${id}-listbox`}
                    ref={listRef}
                    role="listbox"
                    // ⬇️ Aseguramos que quede por encima del header sticky de la tabla
                    className="absolute left-0 right-0 z-50 mt-1 max-h-56 w-full overflow-auto bg-white border border-gray-300 rounded-md text-sm shadow-lg"
                    onScroll={handleScroll}
                >
                    {isLoading && (
                        <li className="px-4 py-2 text-gray-500">Cargando...</li>
                    )}

                    {categories.map((cat) => (
                        <li
                            key={cat.id}
                            role="option"
                            aria-selected={String(cat.id) === String(selectedId)}
                            onMouseDown={() => selectCategory(cat)}
                            className={`cursor-pointer px-4 py-2 hover:bg-primary-100 ${String(cat.id) === String(selectedId) ? "bg-primary-100" : ""
                                }`}
                        >
                            {cat.name}
                        </li>
                    ))}

                    {!isLoading && categories.length === 0 && (
                        <li className="px-4 py-2 text-gray-500">Sin resultados</li>
                    )}

                    {isFetchingNextPage && (
                        <li className="px-4 py-2 text-gray-500">Cargando más...</li>
                    )}
                </ul>
            )}
        </div>
    );
}
