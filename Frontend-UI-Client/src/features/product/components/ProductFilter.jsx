// src/features/product/components/ProductFilter.jsx
import React, { useState } from "react";
import CheckboxCard from "@/components/CheckboxCard";
import { useDebouncedEffect } from "@/features/product/hooks/useDebouncedEffect";
// Usa la misma ruta donde tengas el componente. Si lo moviste a "category", deja este import:
import CategoryPicker from "@/features/product/components/CategoryPicker";

const ProductFilter = ({ filters, onFilterChange }) => {
    const [localFilters, setLocalFilters] = useState({
        name: filters.name || "",
        code: filters.code || "",
        categoryInput: filters.category || "",
        category: "",
        has_subproducts: filters.has_subproducts || false,
    });

    // Sincroniza localFilters cuando cambian los filtros externos (ej: al limpiar desde el padre)
    React.useEffect(() => {
        setLocalFilters((prev) => ({
            ...prev,
            name: filters.name || "",
            code: filters.code || "",
            categoryInput: filters.category || "",
            has_subproducts: filters.has_subproducts || false,
        }));
    }, [filters.name, filters.code, filters.category, filters.has_subproducts]);

    // 🔁 Emitimos cambios con debounce (300ms)
    useDebouncedEffect(
        () => {
            const clean = {
                name: (localFilters.name || "").trim(),
                code: localFilters.code,
                category: (localFilters.categoryInput || "").trim(),
            };
            // Solo agregamos has_subproducts si está activo
            if (localFilters.has_subproducts) {
                clean.has_subproducts = true;
            }
            // Si está desmarcado, simplemente no se agrega la propiedad y el backend lista todos

            if (clean.code && !/^\d+$/.test(clean.code)) {
                return;
            }
            onFilterChange(clean);
        },
        300,
        [localFilters, onFilterChange]
    );
    // Handler para el checkbox de subproductos
    const handleHasSubproductsChange = (e) => {
        setLocalFilters((prev) => ({ ...prev, has_subproducts: e.target.checked }));
    };

    // Handlers
    const handleNameChange = (e) => {
        const { value } = e.target;
        setLocalFilters((prev) => ({ ...prev, name: value }));
    };

    const handleCodeChange = (e) => {
        const { value } = e.target;
        setLocalFilters((prev) => ({ ...prev, code: value }));
    };

    // El CategoryPicker dispara onChange con un evento "input"
    const handleCategoryInputChange = (e) => {
        const { value } = e.target;
        // Cuando el usuario tipea, limpiamos el id hasta que seleccione una opción
        setLocalFilters((prev) => ({ ...prev, categoryInput: value, category: "" }));
    };

    // Cuando el usuario selecciona una categoría del dropdown
    const selectCategory = (cat) => {
        setLocalFilters((prev) => ({
            ...prev,
            category: String(cat.id),
            categoryInput: cat.name,
        }));
        // (No emitimos inmediato; el debounce se encarga)
    };

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            {/* Nombre — mismo look & feel que CategoryPicker */}
            <div className="mb-2">
                <label htmlFor="name" className="block text-sm font-medium text-text-secondary">
                    Nombre
                </label>
                <div className="relative mt-1">
                    {/* icono */}
                    <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                        <svg
                            className="h-5 w-5 text-gray-400"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        name="name"
                        id="name"
                        placeholder="Filtrar Nombre"
                        value={localFilters.name}
                        onChange={handleNameChange}
                        // 👇 mismas clases base que el CategoryPicker
                        className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                    />
                </div>
            </div>

            {/* Código — mismo look & feel que CategoryPicker */}
            <div className="mb-2">
                <label htmlFor="code" className="block text-sm font-medium text-text-secondary">
                    Código
                </label>
                <div className="relative mt-1">
                    {/* icono */}
                    <div className="absolute inset-y-0 left-0 pl-2 flex items-center pointer-events-none">
                        <svg
                            className="h-5 w-5 text-gray-400"
                            xmlns="http://www.w3.org/2000/svg"
                            fill="none" viewBox="0 0 24 24" stroke="currentColor"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M21 21l-4.35-4.35m0 0A7.5 7.5 0 1010.5 18a7.5 7.5 0 006.15-3.35z" />
                        </svg>
                    </div>
                    <input
                        type="text"
                        name="code"
                        id="code"
                        inputMode="numeric"
                        placeholder="Filtrar Código"
                        value={localFilters.code}
                        onChange={handleCodeChange}
                        className="mt-1 block w-full px-3 py-2 pl-9 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 border-background-200"
                    />
                </div>
            </div>

            {/* Categoría (CategoryPicker con búsqueda server + infinite scroll) */}
            <div className="mb-2">
                <label htmlFor="category-filter-input" className="block text-sm font-medium text-text-secondary">
                    Categoría
                </label>
                <CategoryPicker
                    id="category-filter-input"
                    name="categoryInput"
                    value={localFilters.categoryInput}
                    onChange={handleCategoryInputChange}
                    selectCategory={selectCategory}
                    selectedId={localFilters.category}
                    isOpen={true} // el filtro está visible, habilitamos fetch
                />
            </div>
            {/* Solo productos con subproductos */}
            <div className="mb-2 flex items-end">
                <CheckboxCard
                    id="has-subproducts-checkbox"
                    checked={!!localFilters.has_subproducts}
                    onChange={handleHasSubproductsChange}
                    label="Cables"
                />
            </div>
        </div>
    );
};

export default ProductFilter;
