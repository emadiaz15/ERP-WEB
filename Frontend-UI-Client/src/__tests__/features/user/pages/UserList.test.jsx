import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import UserList from '../../../../features/user/pages/UserList';

const queryClient = new QueryClient();

describe('UserList', () => {
    it('se renderiza sin errores', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <UserList />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
    });
});
