// src/features/stocks/hooks/useCuttingOrderDetail.js
import { useState, useEffect } from 'react';
import { getCuttingOrder } from '@/features/cuttingOrder/services/cuttingOrders';

export function useCuttingOrderDetail(orderId, options = {}) {
  const { enabled = true } = options;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!enabled || !orderId) return;
    setLoading(true);
    setError(null);
    getCuttingOrder(orderId)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [orderId, enabled]);

  return { data, loading, error };
}
