import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import ProductList from '../../../../features/product/pages/ProductList';

const queryClient = new QueryClient();

describe('ProductList', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <ProductList />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
