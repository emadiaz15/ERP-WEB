// src/features/product/hooks/useEditProductForm.jsx
import { useState, useEffect, useCallback, useRef } from "react";
import { getCategoryById } from "@/features/category/services/categories";

export function useEditProductForm({
  product,
  categories,
  products,
  updateProduct,
  uploadMut,
  onSave,
  onClose,
  deleteMut,
}) {
  // 👉 recordamos la última categoría seleccionada (id + name)
  const lastPickedRef = useRef(null);

  const [formData, setFormData] = useState({
    name: "",
    code: "",
    description: "",
    brand: "",
    location: "",
    position: "",
    categoryInput: "",
    category: null, // id (string) o null
    initial_stock_quantity: "",
    has_subproducts: false,
    images: [],
  });

  const [previewFiles, setPreviewFiles] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [fileToDelete, setFileToDelete] = useState(null);

  // -------- Helpers
  const normalizeAccents = useCallback(
    (t) =>
      (t ?? "")
        .trim()
        .toLowerCase()
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, ""),
    []
  );

  // -------- 1) Inicialización al abrir modal (precarga robusta de categoría)
  useEffect(() => {
    if (!product) return;

    setPreviewFiles([]);
    setError("");
    setLoading(false);
    setShowSuccess(false);

    const loadInitial = async () => {
      let categoryId = null;
      let categoryName = "";

      if (product.category) {
        // 1) Buscar en categorías ya cargadas
        const found = categories.find((c) => c.id === product.category);
        if (found) {
          categoryId = String(found.id);
          categoryName = found.name || "";
        } else {
          // 2) Fallback a detalle por id
          try {
            const data = await getCategoryById(product.category);
            categoryId = String(data.id);
            categoryName = data.name || "";
          } catch {
            categoryId = null;
            categoryName = "";
          }
        }
      }

      // 👉 persistimos la selección inicial
      lastPickedRef.current = categoryId ? { id: categoryId, name: categoryName } : null;

      setFormData({
        name: product.name || "",
        code: String(product.code || ""),
        description: product.description || "",
        brand: product.brand || "",
        location: product.location || "",
        position: product.position || "",
        categoryInput: categoryName,
        category: categoryId,
        initial_stock_quantity: String(product.initial_stock_quantity || ""),
        has_subproducts: !!product.has_subproducts,
        images: [],
      });
    };

    loadInitial();
  }, [product, categories]);

  // -------- 2) Sincroniza categoryInput -> category (match exacto, ignora acentos/case)
  useEffect(() => {
    const inputNorm = normalizeAccents(formData.categoryInput);

    // Si coincide con la última selección, preservamos el id
    const picked = lastPickedRef.current;
    const pickedMatch = picked && inputNorm === normalizeAccents(picked.name);

    if (pickedMatch) {
      const pickedId = String(picked.id);
      if (formData.category !== pickedId) {
        setFormData((f) => ({ ...f, category: pickedId }));
      }
      return;
    }

    // Resolver por la lista local `categories`
    const found = categories.find((c) => normalizeAccents(c.name) === inputNorm);
    const newCat = found ? String(found.id) : null;

    // Actualizamos el "último elegido"
    lastPickedRef.current = found ? { id: newCat, name: found.name } : null;

    if (formData.category !== newCat) {
      setFormData((f) => ({
        ...f,
        category: newCat,
      }));
    }
  }, [formData.categoryInput, categories, formData.category, normalizeAccents]);

  // -------- 3) Handlers de inputs/archivos
  const handleChange = useCallback((e) => {
    const { name, value, type, checked } = e.target;
    setFormData((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  }, []);

  const handleStockChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((f) => ({ ...f, [name]: value }));
  }, []);

  const handleFileChange = useCallback(
    (e) => {
      const files = Array.from(e.target.files || []);
      if (formData.images.length + files.length > 5) {
        setError("Máximo 5 archivos permitidos.");
        return;
      }
      setFormData((f) => ({ ...f, images: [...f.images, ...files] }));
      setPreviewFiles((p) => [...p, ...files.map((f) => f.name)]);
    },
    [formData.images]
  );

  const removeFile = useCallback((idx) => {
    setFormData((f) => ({
      ...f,
      images: f.images.filter((_, i) => i !== idx),
    }));
    setPreviewFiles((p) => p.filter((_, i) => i !== idx));
  }, []);

  const normalizeCode = useCallback(
    (t) => (t ?? "").trim().toLowerCase().replace(/\s+/g, ""),
    []
  );

  const validateCodeUnique = useCallback(() => {
    return !products.some(
      (p) =>
        p.id !== product.id &&
        normalizeCode(String(p.code)) === normalizeCode(formData.code)
    );
  }, [products, product.id, normalizeCode, formData.code]);

  // -------- 4) Submit
  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setError("");
      setShowSuccess(false);

      if (!validateCodeUnique()) {
        setError("El código ya está en uso.");
        return;
      }
      if (!formData.category) {
        setError("Selecciona una categoría válida.");
        return;
      }

      const codeNum = parseInt((formData.code ?? "").trim(), 10);
      if (Number.isNaN(codeNum)) {
        setError("El código debe ser numérico.");
        return;
      }

      const fd = new FormData();
      fd.append("name", (formData.name ?? "").trim());
      fd.append("code", codeNum);
      fd.append("description", (formData.description ?? "").trim());
      fd.append("brand", (formData.brand ?? "").trim());
      fd.append("location", (formData.location ?? "").trim());
      fd.append("position", (formData.position ?? "").trim());
      fd.append("category", formData.category);
      fd.append("has_subproducts", formData.has_subproducts ? "true" : "false");

      const stockVal = (formData.initial_stock_quantity ?? "").replace(/[^0-9.]/g, "");
      if (stockVal) fd.append("initial_stock_quantity", stockVal);

      try {
        setLoading(true);
        await updateProduct(product.id, fd);
        if (formData.images.length) {
          await uploadMut.uploadFiles(formData.images);
        }
  setShowSuccess(true);
  onSave?.();
  onClose();
      } catch (err) {
        setError(err?.message || "Error al actualizar el producto.");
      } finally {
        setLoading(false);
      }
    },
    [formData, onClose, onSave, product.id, updateProduct, uploadMut, validateCodeUnique]
  );

  // -------- 5) Delete flow
  const openDeleteRequest = useCallback((file) => {
    setFileToDelete(file);
    setIsDeleteOpen(true);
  }, []);

  const closeDeleteRequest = useCallback(() => setIsDeleteOpen(false), []);

  const confirmDelete = useCallback(async () => {
    if (!fileToDelete) return;
    await deleteMut.deleteFile(fileToDelete.id);
    setIsDeleteOpen(false);
    onSave?.();
  }, [fileToDelete, deleteMut, onSave]);

  // -------- 6) API para CategoryPicker
  const selectCategory = useCallback((cat) => {
    const id = String(cat.id);
    const name = cat.name;
    lastPickedRef.current = { id, name }; // 👉 fijamos selección explícita
    setFormData((f) => ({
      ...f,
      category: id,
      categoryInput: name,
    }));
  }, []);

  return {
    formData,
    previewFiles,
    error,
    loading,
    showSuccess,
    // handlers
    handleChange,
    handleStockChange,
    handleFileChange,
    removeFile,
    handleSubmit,
    // delete flow
    isDeleteOpen,
    fileToDelete,
    openDeleteRequest,
    closeDeleteRequest,
    confirmDelete,
    isDeleting: deleteMut.deleting,
    deleteError: deleteMut.deleteError,
    // category api
    selectCategory,
  };
}
