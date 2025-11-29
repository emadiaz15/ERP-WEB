// src/features/product/hooks/useSubproductFilesHooks.js
import { useState, useRef, useCallback, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listSubproductFiles,
  uploadSubproductFiles,
  deleteSubproductFile,
  downloadSubproductFile,
} from "@/features/product/services/subproducts/subproductsFiles";
import { productKeys } from "@/features/product/utils/queryKeys";

export function useSubproductFilesData(productId, subproductId) {
  const listKey = productKeys.subproductFiles(productId, subproductId);

  const rawQuery = useQuery({
    queryKey: listKey,
    queryFn: () => listSubproductFiles(productId, subproductId),
    enabled: !!productId && !!subproductId,
    staleTime: 5 * 60_000,
    refetchOnWindowFocus: false,
  });
  // Construye una "revisión" solo con ítems estables (evita tmp- e isUploading)
  const stableRevision = useMemo(() => {
    const raw = rawQuery.data || [];
    return raw
      .filter((f) => {
        const id = String(f?.key || f?.id || "");
        return !f?.isUploading && !id.startsWith("tmp-");
      })
      .map((f) => f.key || f.id)
      .filter(Boolean)
      .join("|");
  }, [rawQuery.data]);

  const enrichedKey = [...listKey, "enriched", stableRevision];
  const enrichedQuery = useQuery({
    queryKey: enrichedKey,
    enabled: rawQuery.isSuccess, // corre cada vez que cambia stableRevision
    staleTime: 5 * 60_000,
    refetchOnWindowFocus: false,
    queryFn: async () => {
      const raw = rawQuery.data || [];
      // Evita presign para placeholders locales
      const stable = raw.filter((f) => {
        const id = String(f?.key || f?.id || "");
        return !f?.isUploading && !id.startsWith("tmp-");
      });
      const enriched = await Promise.all(
        stable.map(async (f) => {
          const id = f.key || f.id;
          if (!id) return null;
          const url = await downloadSubproductFile(productId, subproductId, id);
          if (!url) return null;
          return {
            ...f,
            id,
            url,
            filename: f.filename || f.name || f.key || String(id),
            contentType: f.content_type || f.mime_type || "application/octet-stream",
          };
        })
      );
      return enriched.filter(Boolean);
    },
  });

  return {
    rawFiles: rawQuery.data || [],
    rawStatus: rawQuery.status,
    rawError: rawQuery.error,

    files: enrichedQuery.data || [],
    status: enrichedQuery.status,
    error: enrichedQuery.error || rawQuery.error,

    isLoading: rawQuery.isLoading || enrichedQuery.isLoading,
    isError: rawQuery.isError || enrichedQuery.isError,
        // útil si abrís un modal: forzá refetch explícito
    refetch: () => { rawQuery.refetch(); enrichedQuery.refetch(); },
  };
}

// ✅ Acepta un productId por defecto para no olvidarlo en mutate.
//    Además revoca los ObjectURL de los placeholders al finalizar.
export function useUploadSubproductFiles(defaultProductId = null) {
  const qc = useQueryClient();
  const placeholderUrls = useRef([]);

  return useMutation({
    mutationKey: ["subproductFiles", "upload", defaultProductId],
    mutationFn: async ({ productId, subproductId, files }) => {
      const resolvedProductId = productId ?? defaultProductId;
      const fileArr = Array.isArray(files) ? files : Array.from(files || []);
      if (!resolvedProductId || !subproductId || fileArr.length === 0) {
        throw new Error("Faltan productId, subproductId o archivos para subir al subproducto.");
      }
      return uploadSubproductFiles(resolvedProductId, subproductId, fileArr);
    },

    onMutate: async ({ productId, subproductId, files }) => {
      const resolvedProductId = productId ?? defaultProductId;
      const listKey = productKeys.subproductFiles(resolvedProductId, subproductId);
      const detailKey = productKeys.subproductDetail(resolvedProductId, subproductId);

      await qc.cancelQueries(listKey);
      const previous = qc.getQueryData(listKey) || [];

      const fileArr = Array.isArray(files) ? files : Array.from(files || []);
      const now = Date.now();
      const placeholders = fileArr.map((file, i) => {
        const id = `tmp-${now}-${i}-${file.name}`;
        const url = URL.createObjectURL(file);
        placeholderUrls.current.push(url);
        return {
          id,
          key: id,
          name: file.name,
          filename: file.name,
          mime_type: file.type,
          content_type: file.type,
          url, // preview local
          isUploading: true,
        };
      });

      qc.setQueryData(listKey, (old = []) => [...placeholders, ...old]);
      return { previous, listKey, detailKey };
    },

    onError: (_err, _vars, ctx) => {
      if (ctx?.previous && ctx?.listKey) qc.setQueryData(ctx.listKey, ctx.previous);
    },

    onSettled: (_data, _err, _vars, ctx) => {
      // Revocar URLs locales si las guardaste (opcional)
      // placeholderUrls.current.forEach(u => { try { URL.revokeObjectURL(u) } catch {} });
      // placeholderUrls.current = [];

      if (ctx?.listKey) {
        // 🔑 objeto -> invalidación por prefijo
        qc.invalidateQueries({ queryKey: ctx.listKey }); 
      }
      if (ctx?.detailKey) {
        qc.invalidateQueries({ queryKey: ctx.detailKey });
      }
    },
  });
}

/**
 * 🗑️ Borrar archivo — API uniforme: mutateAsync({ productId, subproductId, fileId })
 * (Matchea el uso en EditSubproductModal)
 */
export function useDeleteSubproductFile() {
  const qc = useQueryClient();

  return useMutation({
    mutationKey: ["subproductFiles", "delete"],
    mutationFn: async ({ productId, subproductId, fileId }) => {
      if (!productId || !subproductId || !fileId) {
        throw new Error("Faltan productId, subproductId o fileId para borrar el archivo.");
      }
      return deleteSubproductFile(productId, subproductId, fileId);
    },

    onMutate: async ({ productId, subproductId, fileId }) => {
      const listKey = productKeys.subproductFiles(productId, subproductId);
      await qc.cancelQueries(listKey);
      const previous = qc.getQueryData(listKey) || [];
      qc.setQueryData(listKey, (old = []) => old.filter((f) => (f.id || f.key) !== fileId));
      return { previous, productId, subproductId };
    },

    onError: (_err, _vars, ctx) => {
      if (ctx?.previous) {
        const listKey = productKeys.subproductFiles(ctx.productId, ctx.subproductId);
        qc.setQueryData(listKey, ctx.previous);
      }
    },

    onSettled: (_data, _err, _vars, ctx) => {
      if (!ctx) return;
      const listKey = productKeys.subproductFiles(ctx.productId, ctx.subproductId);
      const detailKey = productKeys.subproductDetail(ctx.productId, ctx.subproductId);
      qc.invalidateQueries(listKey);
      qc.invalidateQueries(detailKey);
    },
  });
}

export function useDownloadSubproductFile() {
  const [downloading, setDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState(null);
  const controllerRef = useRef(null);

  const downloadFile = useCallback(async (productId, subproductId, fileId) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setDownloading(true);
    setDownloadError(null);

    try {
      return await downloadSubproductFile(productId, subproductId, fileId, controller.signal);
    } catch (err) {
      if (err.name !== "AbortError") setDownloadError(err.message || "Error descargando archivo");
      return null;
    } finally {
      setDownloading(false);
    }
  }, []);

  const abortDownload = () => controllerRef.current?.abort();
  return { downloadFile, downloading, downloadError, abortDownload };
}
