// src/features/metrics/utils/metricsKeys.js
export const metricsKeys = {
  all: ["metrics"],
  productsWithFiles: () => [...metricsKeys.all, "products-with-files"],
};