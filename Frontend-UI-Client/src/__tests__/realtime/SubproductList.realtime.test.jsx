import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SubproductList from '@/features/product/pages/SubproductList';

// Mock AuthProvider/useAuth to provide a user context consumed by Toolbar
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

// Mock Layout and heavy children
jest.mock('@/pages/Layout', () => ({
  __esModule: true,
  default: ({ children }) => <div data-testid="layout">{children}</div>,
}));

jest.mock('@/features/product/components/SubproductCard', () => ({
  __esModule: true,
  default: ({ subproduct }) => <div data-testid="subproduct-card">{subproduct?.id}</div>,
}));

jest.mock('@/features/product/components/SubproductFilter', () => ({
  __esModule: true,
  default: () => <div data-testid="subproduct-filters" />,
}));

jest.mock('@/features/product/components/SubproductModals', () => ({
  __esModule: true,
  default: () => <div data-testid="subproduct-modals" />,
}));

// Mock cutting order wizard to avoid Radix complexity
jest.mock('@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard', () => ({
  __esModule: true,
  default: () => null,
}));

// Mock hook to expose refetch
const mockRefetch = jest.fn();
jest.mock('@/features/product/hooks/useSubproductHooks', () => ({
  useListSubproducts: () => ({
    subproducts: [{ id: 10, status: true, current_stock: 1 }],
    nextPageUrl: null,
    previousPageUrl: null,
    isLoading: false,
    isError: false,
    error: null,
    refetch: mockRefetch,
  }),
  useCreateSubproduct: () => ({ mutateAsync: jest.fn(), isPending: false }),
  useUpdateSubproduct: () => ({ mutateAsync: jest.fn() }),
  useDeleteSubproduct: () => ({ mutateAsync: jest.fn() }),
}));

const renderWithProviders = (ui, { route = '/products/1/subproducts' } = {}) => {
  const queryClient = new QueryClient();
  return render(
    <MemoryRouter initialEntries={[route]}>
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route path="/products/:productId/subproducts" element={ui} />
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>
  );
};

describe('SubproductList realtime listener', () => {
  beforeEach(() => mockRefetch.mockClear());

  it('calls refetch() on Subproduct realtime events', () => {
    renderWithProviders(<SubproductList />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'Subproduct', event: 'update', payload: { id: 10 } } }));
  expect(mockRefetch).toHaveBeenCalledTimes(1);
  });

  it('ignores different models', () => {
    renderWithProviders(<SubproductList />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'User', event: 'create' } }));
    expect(mockRefetch).not.toHaveBeenCalled();
  });
});
