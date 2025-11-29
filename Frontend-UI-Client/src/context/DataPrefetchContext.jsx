/** src/context/DataPrefetchContext.jsx
 * Contexto para prefetch de datos comunes como categorías.
 * Utilizado para cargar datos necesarios antes de renderizar componentes.
 * Permite evitar múltiples llamadas a la API en componentes individuales.
 */

/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/context/AuthProvider";
import { listCategories } from "@/features/category/services/categories";

const DataPrefetchContext = createContext({
  categories: [],
  loading: true,
  loaded: false,
});

export const DataPrefetchProvider = ({ children }) => {
  const { isAuthenticated, loading: authLoading } = useAuth();

  const {
    data: catData,
    isLoading: loadingCats,
  } = useQuery({
    queryKey: ["prefetch", "categories"],
    queryFn: () => listCategories({ /* opcional: page_size, etc. */ }),
    staleTime: 5 * 60 * 1000,
    enabled: !authLoading && isAuthenticated,
  });

  const categories = catData?.results || [];

  const loading = authLoading || loadingCats;
  const loaded = !loading && !!catData;

  return (
    <DataPrefetchContext.Provider value={{ categories, loading, loaded }}>
      {children}
    </DataPrefetchContext.Provider>
  );
};

export const usePrefetchedData = () => {
  const ctx = useContext(DataPrefetchContext);
  if (!ctx) {
    throw new Error("usePrefetchedData debe usarse dentro de <DataPrefetchProvider>");
  }
  return ctx;
};
