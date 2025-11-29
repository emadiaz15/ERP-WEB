// src/features/metrics/services/metrics.js
import { djangoApi } from "@/api/clients";

export async function getProductsWithFilesPercentage() {
  const { data } = await djangoApi.get(
    "/metrics/products/with-files-percentage/"
  ); // baseUrl ya incluye /api/v1
  return data; // { total, with_files, percentage }
}
