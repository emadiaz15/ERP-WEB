
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useProductFilesData } from '../../../../features/product/hooks/useProductFileHooks';

const queryClient = new QueryClient();

describe('useProductFilesData', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useProductFilesData(null), { wrapper });
  });
});
