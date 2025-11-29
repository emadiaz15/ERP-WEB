import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '@/pages/Dashboard';

// Mock AuthProvider/useAuth to provide authenticated user
jest.mock('@/context/AuthProvider', () => {
    const React = require('react');
    const Ctx = React.createContext({ user: { is_staff: true }, isAuthenticated: true, loading: false });
    return {
        AuthProvider: ({ children }) => (
            <Ctx.Provider value={{ user: { is_staff: true }, isAuthenticated: true, loading: false }}>
                {children}
            </Ctx.Provider>
        ),
        useAuth: () => React.useContext(Ctx),
    };
});

// Mock Layout to a lightweight wrapper
jest.mock('@/pages/Layout', () => ({ __esModule: true, default: ({ children }) => <div>{children}</div> }));

// Stub live sync hook used by Dashboard so it doesn't touch websockets in tests
jest.mock('@/features/cuttingOrder/hooks/useCuttingOrderLiveSync', () => ({
    useCuttingOrderLiveSync: () => { },
}));

// Mock the service used by Dashboard to count reload calls
const mockListCuttingOrders = jest.fn().mockResolvedValue({ results: [], next: null });
jest.mock('@/features/cuttingOrder/services/cuttingOrders', () => {
    const actual = jest.requireActual('@/features/cuttingOrder/services/cuttingOrders');
    return {
        ...actual,
        listCuttingOrders: (...args) => mockListCuttingOrders(...args),
    };
});

describe('Dashboard realtime listener', () => {
    beforeEach(() => mockListCuttingOrders.mockClear());

    it('reloads on CuttingOrder realtime events', () => {
        const queryClient = new QueryClient();
        render(
            <MemoryRouter>
                <QueryClientProvider client={queryClient}>
                    <Dashboard />
                </QueryClientProvider>
            </MemoryRouter>
        );

        // Initial load triggers 3 calls (one per column). After event, expect +3
        const initialCalls = mockListCuttingOrders.mock.calls.length;

        window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'CuttingOrder', event: 'update' } }));

        // Allow effect to fire synchronously; Dashboard reloadAll schedules immediate calls
        expect(mockListCuttingOrders.mock.calls.length).toBe(initialCalls + 3);
    });

    it('ignores unrelated models', () => {
        const queryClient = new QueryClient();
        render(
            <MemoryRouter>
                <QueryClientProvider client={queryClient}>
                    <Dashboard />
                </QueryClientProvider>
            </MemoryRouter>
        );

        const initialCalls = mockListCuttingOrders.mock.calls.length;
        window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'User', event: 'create' } }));
        expect(mockListCuttingOrders.mock.calls.length).toBe(initialCalls);
    });
});
