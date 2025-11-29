import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import EditProductModal from '../../../../features/product/components/EditProductModal';

const queryClient = new QueryClient();

describe('EditProductModal', () => {
    it('se renderiza sin errores', () => {
        const mockProduct = {
            id: 1,
            name: 'Producto de prueba',
            description: 'Descripción',
            stock: 10,
            price: 100,
            category: 1,
            files: [],
        };
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <EditProductModal
                            product={mockProduct}
                            isOpen={true}
                            onClose={() => { }}
                            onSave={() => { }}
                        />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
