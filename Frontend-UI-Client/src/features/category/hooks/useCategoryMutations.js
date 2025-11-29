// src/features/category/hooks/useCategoryMutations.js
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createCategory,
  updateCategory,
  deleteCategory,
} from "../services/categories";
import { categoryKeys } from "../utils/queryKeys"

const updateAllCategoryPages = (qc, transformResults) => {
  // Aplica transformaciones a todas las queries bajo la raíz 'categories'
  qc.setQueriesData(
    {
      predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'categories',
    },
    (old) => {
      if (!old) return old;
      // Soporta tanto infiniteQuery ({pages}) como listas simples ({results})
      if (Array.isArray(old.pages)) {
        const pages = old.pages.map((p) => {
          if (!Array.isArray(p?.results)) return p;
          const results = transformResults(p.results);
          return { ...p, results };
        });
        return { ...old, pages };
      }
      if (Array.isArray(old.results)) {
        return { ...old, results: transformResults(old.results) };
      }
      return old;
    }
  );
};

export const useCreateCategory = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCategory,
    onSuccess: (newCat) => {
      // Patch local: insertar al inicio de la primera página de cada listado activo
      qc.setQueriesData(
        { predicate: (q) => Array.isArray(q.queryKey) && q.queryKey[0] === 'categories' },
        (old) => {
          if (!old) return old;
          if (Array.isArray(old.pages)) {
            const pages = old.pages.slice();
            const first = pages[0] || {};
            const results = Array.isArray(first.results) ? first.results : [];
            if (results.some((c) => c?.id === newCat.id)) return old;
            const nextResults = [newCat, ...results];
            pages[0] = { ...first, results: nextResults, count: typeof first.count === 'number' ? first.count + 1 : first.count };
            return { ...old, pages };
          }
          if (Array.isArray(old.results)) {
            if (old.results.some((c) => c?.id === newCat.id)) return old;
            return { ...old, results: [newCat, ...old.results], count: typeof old.count === 'number' ? old.count + 1 : old.count };
          }
          return old;
        }
      );
      // Invalidar para recomputar pertenencia con filtros activos
      qc.invalidateQueries({ queryKey: categoryKeys.all });
      qc.invalidateQueries({ queryKey: categoryKeys.prefetch() });
    },
  });
};

export const useUpdateCategory = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }) => updateCategory(id, payload),
    onSuccess: (updatedCat) => {
      updateAllCategoryPages(qc, (cats) => cats.map((cat) => (cat?.id === updatedCat.id ? { ...cat, ...updatedCat } : cat)));
      qc.invalidateQueries({ queryKey: categoryKeys.all });
      qc.invalidateQueries({ queryKey: categoryKeys.prefetch() });
    },
  });
};

export const useDeleteCategory = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id) => deleteCategory(id),
    onSuccess: (_resp, id) => {
      updateAllCategoryPages(qc, (cats) => cats.filter((cat) => cat?.id !== id));
      qc.invalidateQueries({ queryKey: categoryKeys.all });
      qc.invalidateQueries({ queryKey: categoryKeys.prefetch() });
    },
  });
};
