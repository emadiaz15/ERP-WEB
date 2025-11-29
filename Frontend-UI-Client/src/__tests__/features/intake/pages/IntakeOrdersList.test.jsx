import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import IntakeOrdersList from '@/features/intake/pages/IntakeOrdersList';

jest.mock('@/features/intake/services/intakeOrders', () => ({
  listIntakeOrders: jest.fn().mockResolvedValue({ results: [], next: null })
}));

jest.mock('@/context/AuthProvider', () => ({
  useAuth: () => ({ isAuthenticated: true, user: { id:1, is_staff:true } })
}));

jest.mock('@/components/common/Toolbar', () => ({ __esModule: true, default: ({ title }) => <div data-testid="toolbar">{title}</div> }));

describe('IntakeOrdersList', () => {
  it('renderiza y muestra toolbar', async () => {
    render(
      <MemoryRouter initialEntries={['/intake/orders']}>
        <Routes>
          <Route path="/intake/orders" element={<IntakeOrdersList />} />
        </Routes>
      </MemoryRouter>
    );
    expect(await screen.findByTestId('toolbar')).toHaveTextContent('Notas de Pedido');
  });
});
