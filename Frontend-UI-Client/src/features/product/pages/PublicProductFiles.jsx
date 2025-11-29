import React, { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Spinner from "@/components/ui/Spinner";
import ProductCarouselOverlay from "@/features/product/components/ProductCarouselOverlay";
import { fetchPublicProductFilesByCode } from "@/features/product/services/products/publicFiles";

const initialState = {
  loading: false,
  error: null,
  product: null,
  files: [],
};

const PublicProductFiles = () => {
  const [searchParams] = useSearchParams();
  const [state, setState] = useState(initialState);

  const code = useMemo(() => (searchParams.get("code") || "").trim(), [searchParams]);

  useEffect(() => {
    if (!code) {
      setState({ ...initialState, error: "Falta el parámetro 'code' en la URL" });
      return;
    }

    let cancelled = false;
    setState({ loading: true, error: null, product: null, files: [] });

    fetchPublicProductFilesByCode(code)
      .then(({ product, files }) => {
        if (cancelled) return;
        setState({ loading: false, error: null, product, files });
      })
      .catch((error) => {
        if (cancelled) return;
        setState({ loading: false, error: error.message, product: null, files: [] });
      });

    return () => {
      cancelled = true;
    };
  }, [code]);

  const { loading, error, product, files } = state;
  const hasFiles = files.length > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black text-white flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-6xl space-y-8">
        <header className="text-center space-y-3">
          <h1 className="text-3xl md:text-4xl font-semibold tracking-tight">
            Archivos del producto #{code || ""}
          </h1>
          <p className="text-white/60">
            Este visor público carga la galería automáticamente usando el código recibido por URL.
          </p>
        </header>

        {loading && (
          <div className="flex justify-center py-24">
            <Spinner size="12" color="text-primary-400" />
          </div>
        )}

        {!loading && error && (
          <div className="bg-red-600/20 border border-red-500/30 text-red-200 rounded-3xl px-6 py-6 text-center">
            {error}
          </div>
        )}

        {!loading && !error && product && (
          <div className="space-y-6">
            <div className="bg-white/5 border border-white/10 rounded-3xl p-6 md:p-8 shadow-2xl backdrop-blur">
              <div className="space-y-2 text-center md:text-left">
                <p className="text-sm uppercase tracking-[0.4em] text-white/40">Código {product.code}</p>
                <h2 className="text-2xl md:text-3xl font-semibold">{product.name || "Producto sin nombre"}</h2>
                {product.description && (
                  <p className="text-white/70 max-w-3xl mx-auto md:mx-0 leading-relaxed">
                    {product.description}
                  </p>
                )}
              </div>
            </div>

            {hasFiles ? (
              <div className="bg-black/50 border border-white/10 rounded-3xl p-4 md:p-6 shadow-2xl">
                <ProductCarouselOverlay images={files} isEmbedded editable={false} />
              </div>
            ) : (
              <div className="text-center text-white/60 py-24 border border-dashed border-white/20 rounded-3xl">
                Este producto todavía no tiene archivos disponibles.
              </div>
            )}
          </div>
        )}

        {!loading && !error && !product && code && (
          <div className="text-center text-white/60 py-16">
            No se encontró un producto activo con el código proporcionado.
          </div>
        )}
      </div>
    </div>
  );
};

export default PublicProductFiles;
