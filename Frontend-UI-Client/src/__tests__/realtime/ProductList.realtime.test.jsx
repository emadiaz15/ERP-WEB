import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductList from '@/features/product/pages/ProductList';

// Mock AuthProvider/useAuth to avoid network calls and provide staff
jest.mock('@/context/AuthProvider', () => {
  const React = require('react');
  const Ctx = React.createContext({ user: { is_staff: true } });
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
jest.mock('@/pages/Layout', () => ({
  __esModule: true,
  default: ({ children }) => <div data-testid="layout">{children}</div>,
}));

// Mock heavy child components to avoid IntersectionObserver and UI complexity
jest.mock('@/features/product/components/ProductTable', () => ({
  __esModule: true,
  default: ({ products = [] }) => <div data-testid="product-table">{products.length} products</div>,
}));

jest.mock('@/features/product/components/ProductFilter', () => ({
  __esModule: true,
  default: () => <div data-testid="product-filter" />,
}));

jest.mock('@/features/product/components/ProductModals', () => ({
  __esModule: true,
  default: () => <div data-testid="product-modals" />,
}));

// Mock KPI hook
jest.mock('@/features/metrics/hooks/useProductsWithFiles', () => ({
  useProductsWithFiles: () => ({ data: { total: 2, with_files: 1, percentage: 50 }, isLoading: false }),
}));

// Mock the pagination hook to capture invalidate calls
const mockInvalidate = jest.fn();
jest.mock('@/hooks/useInfinitePageQuery', () => ({
  useInfinitePageQuery: () => ({
    items: [
      { id: 1, name: 'A', code: 'A-1', has_subproducts: false },
      { id: 2, name: 'B', code: 'B-2', has_subproducts: true },
    ],
    isLoading: false,
    isError: false,
    error: null,
    fetchNextPage: jest.fn(),
    hasNextPage: false,
    isFetchingNextPage: false,
    invalidate: mockInvalidate,
  }),
}));

const renderWithProviders = (ui) => {
  const queryClient = new QueryClient();
  return render(
    <MemoryRouter>
      {/* Use the mocked AuthProvider via context module */}
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe('ProductList realtime listener', () => {
  beforeEach(() => mockInvalidate.mockClear());

  it('calls invalidate() on realtime Product events', () => {
    renderWithProviders(<ProductList />);

    const detail = { model: 'Product', event: 'create', payload: { id: 3 } };
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail }));

  expect(mockInvalidate).toHaveBeenCalledTimes(1);
  });

  it('ignores unrelated models', () => {
    renderWithProviders(<ProductList />);

    const detail = { model: 'User', event: 'update', payload: { id: 1 } };
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail }));

    expect(mockInvalidate).not.toHaveBeenCalled();
  });
});
