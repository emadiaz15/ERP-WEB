
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useInfinitePageQuery } from '../../hooks/useInfinitePageQuery';

const queryClient = new QueryClient();

describe('useInfinitePageQuery', () => {
  it('puede llamarse sin errores', () => {
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useInfinitePageQuery({ key: ['test'], url: '/test/' }), { wrapper });
  });
});
