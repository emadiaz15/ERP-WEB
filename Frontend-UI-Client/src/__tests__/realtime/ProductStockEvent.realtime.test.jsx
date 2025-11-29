import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ProductStockEvent from '@/features/stocks/pages/ProductStockEvent';

// Mock Layout and inner components
jest.mock('@/pages/Layout', () => ({ __esModule: true, default: ({ children }) => <div>{children}</div> }));
jest.mock('@/features/stocks/components/StockEventToolbar', () => ({ __esModule: true, default: () => <div /> }));
jest.mock('@/features/stocks/components/StockDateFilter', () => ({ __esModule: true, default: () => <div /> }));
jest.mock('@/features/stocks/components/StockEventTable', () => ({ __esModule: true, default: () => <div data-testid="table" /> }));
jest.mock('@/features/stocks/components/SentinelRow', () => ({ __esModule: true, default: () => null }));
jest.mock('@/features/cuttingOrder/components/ViewCuttingOrderModal', () => ({ __esModule: true, default: () => null }));
jest.mock('@/features/stocks/components/AdjustStockModal', () => ({ __esModule: true, default: () => null }));

// Intercept useInfinitePageQuery invalidate
const mockInvalidate = jest.fn();
jest.mock('@/hooks/useInfinitePageQuery', () => ({
  useInfinitePageQuery: () => ({
    items: [],
    isLoading: false,
    isError: false,
    error: null,
    fetchNextPage: jest.fn(),
    hasNextPage: false,
    isFetchingNextPage: false,
    invalidate: mockInvalidate,
  }),
}));

const renderWithProviders = (ui, { route = '/products/1/stock-history' } = {}) => {
  const queryClient = new QueryClient();
  return render(
    <MemoryRouter initialEntries={[route]}>
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route path="/products/:productId/stock-history" element={ui} />
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>
  );
};

describe('ProductStockEvent realtime listener', () => {
  beforeEach(() => mockInvalidate.mockClear());

  it('invalidates on StockEvent realtime events', () => {
    renderWithProviders(<ProductStockEvent />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'StockEvent', event: 'create' } }));
  expect(mockInvalidate).toHaveBeenCalledTimes(1);
  });

  it('does not invalidate on other models', () => {
    renderWithProviders(<ProductStockEvent />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'Product', event: 'update' } }));
    expect(mockInvalidate).not.toHaveBeenCalled();
  });
});
