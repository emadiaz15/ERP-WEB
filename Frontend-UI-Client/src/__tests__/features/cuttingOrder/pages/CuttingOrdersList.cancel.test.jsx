import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CuttingOrdersList from '@/features/cuttingOrder/pages/CuttingOrdersList';

// Mock AuthProvider/useAuth to avoid redirects and get is_staff
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

// Lightweight Layout
jest.mock('@/pages/Layout', () => ({ __esModule: true, default: ({ children }) => <div>{children}</div> }));

// Inline table to expose the cancel button and call the onDelete handler
jest.mock('@/features/cuttingOrder/components/CuttingOrderTable', () => ({
  __esModule: true,
  default: ({ orders, onDelete }) => (
    <div>
      {orders.map((o) => (
        <div key={o.id}>
          <span>Order {o.id}</span>
          <button aria-label="Cancelar orden" onClick={() => onDelete(o.id)}>Cancelar</button>
        </div>
      ))}
    </div>
  ),
}));

// Modal that immediately calls onDelete when rendered (to simulate confirmation)
jest.mock('@/features/cuttingOrder/components/CuttingOrderModals', () => ({
  __esModule: true,
  default: ({ modalState, onDeleteOrder }) => (
    modalState?.type === 'deleteConfirm' ? (
      <button onClick={() => onDeleteOrder(modalState.orderData.id)}>Confirmar Cancelación</button>
    ) : null
  ),
}));

// Wizard is irrelevant here
jest.mock('@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard', () => ({ __esModule: true, default: () => null }));

const mockListCuttingOrders = jest.fn();
const mockCancel = jest.fn();

jest.mock('@/features/cuttingOrder/services/cuttingOrders', () => ({
  __esModule: true,
  listCuttingOrders: (...args) => mockListCuttingOrders(...args),
  cancelCuttingOrder: (...args) => mockCancel(...args),
  updateCuttingOrder: jest.fn(),
}));

const renderWithProviders = (ui) => {
  const qc = new QueryClient();
  return render(
    <MemoryRouter>
      <QueryClientProvider client={qc}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe('CuttingOrdersList cancel flow', () => {
  beforeEach(() => {
    mockListCuttingOrders.mockReset();
    mockCancel.mockReset();
  });

  it('calls cancelCuttingOrder and refreshes list', async () => {
    mockListCuttingOrders
      .mockResolvedValueOnce({ results: [{ id: 1, workflow_status: 'pending' }], next: null }) // initial
      .mockResolvedValueOnce({ results: [{ id: 1, workflow_status: 'cancelled' }], next: null }); // after cancel
    mockCancel.mockResolvedValue({ ok: true });

    renderWithProviders(<CuttingOrdersList />);

    // waits initial load
    await waitFor(() => expect(mockListCuttingOrders).toHaveBeenCalled());

    // user clicks cancel in the row
    const btn = await screen.findByRole('button', { name: /cancelar orden/i });
    fireEvent.click(btn);

    // confirm in modal
    const confirm = await screen.findByRole('button', { name: /confirmar cancelación/i });
    fireEvent.click(confirm);

    // API called
    await waitFor(() => expect(mockCancel).toHaveBeenCalledWith(1));

    // list fetch called again for refresh
    await waitFor(() => expect(mockListCuttingOrders).toHaveBeenCalledTimes(2));

    // shows success message and new state appears
    expect(await screen.findByText(/cancelada/i)).toBeInTheDocument();
  });
});
