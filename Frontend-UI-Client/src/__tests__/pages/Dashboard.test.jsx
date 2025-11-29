import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import Dashboard from '../../pages/Dashboard';

const queryClient = new QueryClient();

describe('Dashboard', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <Dashboard />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
