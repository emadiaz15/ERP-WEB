import React from "react";
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../context/AuthProvider';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../App';

describe('App', () => {
    it('renderiza el título principal', () => {
        const queryClient = new QueryClient();
        render(
            <MemoryRouter>
                <AuthProvider>
                    <QueryClientProvider client={queryClient}>
                        <App />
                    </QueryClientProvider>
                </AuthProvider>
            </MemoryRouter>
        );
        // Cambia el texto según el título real de tu app
        expect(screen.getByText(/gestión comercial|seryon/i)).toBeInTheDocument();
    });
});
