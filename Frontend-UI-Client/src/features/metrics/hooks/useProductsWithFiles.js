// src/features/metrics/hooks/useProductsWithFiles.js
import { useQuery } from "@tanstack/react-query";
import { metricsKeys } from "../utils/metricsKeys";
import { getProductsWithFilesPercentage } from "@/features/metrics/services/metricsKeys";

export function useProductsWithFiles() {
  return useQuery({
    queryKey: metricsKeys.productsWithFiles(),
    queryFn: getProductsWithFilesPercentage,
    refetchOnWindowFocus: false,
    staleTime: 10_000,
  });
}