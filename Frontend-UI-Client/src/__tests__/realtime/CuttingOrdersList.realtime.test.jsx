import React from 'react';
import { render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CuttingOrdersList from '@/features/cuttingOrder/pages/CuttingOrdersList';

// Mock AuthProvider/useAuth to avoid null context and redirects
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

// Mock Layout and inner heavy components
jest.mock('@/pages/Layout', () => ({ __esModule: true, default: ({ children }) => <div>{children}</div> }));
jest.mock('@/features/cuttingOrder/components/CuttingOrderTable', () => ({ __esModule: true, default: () => <div data-testid="table" /> }));
jest.mock('@/features/cuttingOrder/components/CuttingOrderModals', () => ({ __esModule: true, default: () => null }));
// Mock wizard to avoid invoking hooks inside it (useCreateCuttingOrder)
jest.mock('@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard', () => ({ __esModule: true, default: () => null }));

// Mock service used by the page to load data
const mockListCuttingOrders = jest.fn().mockResolvedValue({ results: [], next: null });
jest.mock('@/features/cuttingOrder/services/cuttingOrders', () => ({
  __esModule: true,
  listCuttingOrders: (...args) => mockListCuttingOrders(...args),
  updateCuttingOrder: jest.fn(),
  deleteCuttingOrder: jest.fn(),
}));

const renderWithProviders = (ui) => {
  const queryClient = new QueryClient();
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe('CuttingOrdersList realtime listener', () => {
  beforeEach(() => mockListCuttingOrders.mockClear());

  it('refetches on CuttingOrder realtime events', async () => {
    renderWithProviders(<CuttingOrdersList />);
    // initial load
    await waitFor(() => expect(mockListCuttingOrders).toHaveBeenCalled());
    mockListCuttingOrders.mockClear();
    // realtime event for this model should trigger another fetch
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'CuttingOrder', event: 'update' } }));
    await waitFor(() => expect(mockListCuttingOrders).toHaveBeenCalledTimes(1));
  });

  it('ignores unrelated models', async () => {
    renderWithProviders(<CuttingOrdersList />);
    await waitFor(() => expect(mockListCuttingOrders).toHaveBeenCalled());
    mockListCuttingOrders.mockClear();
    // event for another model should not trigger fetch
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'User', event: 'update' } }));
    // Give a tick to ensure no calls happen
    await new Promise((r) => setTimeout(r, 0));
    expect(mockListCuttingOrders).not.toHaveBeenCalled();
  });
});
