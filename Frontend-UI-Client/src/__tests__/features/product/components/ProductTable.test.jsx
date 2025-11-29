import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import ProductTable from '../../../../features/product/components/ProductTable';

const queryClient = new QueryClient();

describe('ProductTable', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <ProductTable />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
