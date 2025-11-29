import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import CategoryList from '../../../../features/category/pages/CategoriesList';

const queryClient = new QueryClient();

describe('CategoryList', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <CategoryList />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
