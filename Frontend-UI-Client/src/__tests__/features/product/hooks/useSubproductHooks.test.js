
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useListSubproducts } from '../../../../features/product/hooks/useSubproductHooks';

const queryClient = new QueryClient();

describe('useListSubproducts', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useListSubproducts(null), { wrapper });
  });
});
