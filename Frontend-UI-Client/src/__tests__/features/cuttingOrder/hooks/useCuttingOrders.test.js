
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCuttingOrders } from '../../../../features/cuttingOrder/hooks/useCuttingOrders';

const queryClient = new QueryClient();

describe('useCuttingOrders', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useCuttingOrders(), { wrapper });
  });
});
