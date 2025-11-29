// src/features/category/services/categories.js
import { djangoApi } from "@/api/clients";
import { buildQueryString } from "@/utils/queryUtils";
import { getCached, setCached, invalidatePrefixes } from "@/utils/httpCache";

/**
 * 📋 Listar categorías con paginación/filtros
 */
export const listCategories = async (params = {}) => {
  const qs = buildQueryString(params);
  const url = `/inventory/categories/${qs}`;
  const cached = getCached(url, 60000);
  if (cached) return cached;
  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return data;
};

/**
 * 🆕 Crear nueva categoría
 */
export const createCategory = async (payload) => {
  const { data } = await djangoApi.post("/inventory/categories/create/", payload);
  invalidatePrefixes("/inventory/categories/");
  return data;
};

/**
 * ✏️ Actualizar categoría
 */
export const updateCategory = async (id, payload) => {
  const { data } = await djangoApi.put(`/inventory/categories/${id}/`, payload);
  invalidatePrefixes("/inventory/categories/");
  return data;
};

/**
 * 🗑️ Eliminar (soft-delete) categoría
 */
export const deleteCategory = async (id) => {
  await djangoApi.delete(`/inventory/categories/${id}/`);
  invalidatePrefixes("/inventory/categories/");
  return true;
};


/** Obtener detalle de categoría por ID */
export const getCategoryById = async (id) => {
  const url = `/inventory/categories/${id}/`;
  const cached = getCached(url, 60000);
  if (cached) return cached;
  const { data } = await djangoApi.get(url);
  setCached(url, data);
  return data;
};