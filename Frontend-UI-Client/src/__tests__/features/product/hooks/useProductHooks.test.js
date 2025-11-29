
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProducts } from '../../../../features/product/hooks/useProductHooks';

const queryClient = new QueryClient();

describe('useProducts', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useProducts(), { wrapper });
  });
});
