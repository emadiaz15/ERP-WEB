
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSubproductFilesData } from '../../../../features/product/hooks/useSubproductFileHooks';

const queryClient = new QueryClient();

describe('useSubproductFilesData', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useSubproductFilesData(null, null), { wrapper });
  });
});
