
import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import CuttingOrderTable from '../../../../features/cuttingOrder/components/CuttingOrderTable';

const queryClient = new QueryClient();

// Mock de usuario autenticado
const mockUser = { id: 1, username: 'test', is_staff: true };

jest.spyOn(require('@/context/AuthProvider'), 'useAuth').mockImplementation(() => ({
    user: mockUser,
    isStaff: true,
    isAuthenticated: true,
    loading: false,
    error: null,
    profileImage: null,
    login: jest.fn(),
    logout: jest.fn(),
}));

describe('CuttingOrderTable', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <CuttingOrderTable orders={[]} />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
