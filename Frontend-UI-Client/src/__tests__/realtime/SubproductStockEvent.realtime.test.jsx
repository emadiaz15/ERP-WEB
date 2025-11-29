import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SubproductStockEvent from '@/features/stocks/pages/SubproductStockEvent';

// Mock Layout and inner components
jest.mock('@/pages/Layout', () => ({ __esModule: true, default: ({ children }) => <div>{children}</div> }));
jest.mock('@/features/stocks/components/StockEventTable', () => ({ __esModule: true, default: () => <div data-testid="table" /> }));
jest.mock('@/features/stocks/components/StockDateFilter', () => ({ __esModule: true, default: () => <div /> }));
jest.mock('@/features/stocks/components/AdjustStockModal', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/common/Toolbar', () => ({ __esModule: true, default: () => <div /> }));
jest.mock('@/features/cuttingOrder/components/ViewCuttingOrderModal', () => ({ __esModule: true, default: () => null }));

// Intercept the hook to capture fetchStockEvents
const mockFetchStockEvents = jest.fn();
jest.mock('@/features/stocks/hooks/useStockSubproductEvents', () => ({
  useStockSubproductEvents: () => ({
    stockEvents: [],
    loading: false,
    error: null,
    nextPage: null,
    previousPage: null,
  fetchStockEvents: mockFetchStockEvents,
    handleFilterChange: jest.fn(),
    isFetchingNextPage: false,
    hasNextPage: false,
  }),
}));

const renderWithProviders = (ui, { route = '/subproducts/22/stock-history' } = {}) => {
  const queryClient = new QueryClient();
  return render(
    <MemoryRouter initialEntries={[route]}>
      <QueryClientProvider client={queryClient}>
        <Routes>
          <Route path="/subproducts/:subproductId/stock-history" element={ui} />
        </Routes>
      </QueryClientProvider>
    </MemoryRouter>
  );
};

describe('SubproductStockEvent realtime listener', () => {
  beforeEach(() => mockFetchStockEvents.mockClear());

  it('calls fetchStockEvents on StockEvent realtime events', () => {
    renderWithProviders(<SubproductStockEvent />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'StockEvent', event: 'delete' } }));
  expect(mockFetchStockEvents).toHaveBeenCalledTimes(1);
  });

  it('ignores unrelated models', () => {
    renderWithProviders(<SubproductStockEvent />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'Product', event: 'create' } }));
    expect(mockFetchStockEvents).not.toHaveBeenCalled();
  });
});
