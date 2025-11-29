import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import CategoryTable from '../../../../features/category/components/CategoryTable';

const queryClient = new QueryClient();

describe('CategoryTable', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <CategoryTable categories={[]} />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
