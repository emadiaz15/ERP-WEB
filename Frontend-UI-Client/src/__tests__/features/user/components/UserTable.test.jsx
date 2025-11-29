import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import UserTable from '../../../../features/user/components/UserTable';

const queryClient = new QueryClient();

describe('UserTable', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <UserTable users={[]} />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
