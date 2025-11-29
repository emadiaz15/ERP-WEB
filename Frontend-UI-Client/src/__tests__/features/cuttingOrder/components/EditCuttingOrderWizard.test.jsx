import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import EditCuttingOrderWizard from '@/features/cuttingOrder/components/wizard/EditCuttingOrderWizard';

jest.mock('@/features/user/services/listUsers', () => ({
  listUsers: jest.fn().mockResolvedValue({ results: [{ id: 1, username: 'op' }] })
}));

jest.mock('@/features/product/hooks/useProductHooks', () => ({
  useProducts: () => ({ products: [{ id: 10, code: 'P-1', name: 'Prod' }], loading: false, isError: false })
}));

jest.mock('@/features/cuttingOrder/services/cuttingOrders', () => ({
  listSubproductsByParent: jest.fn().mockResolvedValue({ results: [] })
}));

jest.mock('@/features/cuttingOrder/hooks/useCuttingOrders', () => ({
  useUpdateCuttingOrder: () => [jest.fn().mockResolvedValue({ id: 123 }), { loading: false }]
}));

const Wrapper = ({ children }) => {
  const qc = new QueryClient();
  return (
    <MemoryRouter>
      <AuthProvider>
        <QueryClientProvider client={qc}>{children}</QueryClientProvider>
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('EditCuttingOrderWizard', () => {
  it('cierra inmediatamente en éxito y llama onSave', async () => {
    const onClose = jest.fn();
    const onSave = jest.fn();

    render(
      <Wrapper>
        <EditCuttingOrderWizard
          isOpen
          embedded
          onClose={onClose}
          onSave={onSave}
          order={{ id: 55, order_number: 55, customer: 'ACME', product: 10, items: [] }}
        />
      </Wrapper>
    );

    // Rellenar campos mínimos: cantidad pedida (puede ser 0 si hay ítems, pero acá no habrá ítems, así que ponemos >0)
    const qtyInput = await screen.findByLabelText(/cantidad pedida/i);
    fireEvent.change(qtyInput, { target: { value: '50' } });

    // Seleccionar un asignatario válido para evitar restricciones del formulario
    const assignee = await screen.findByLabelText(/asignar a/i);
    fireEvent.change(assignee, { target: { value: '1' } });

    const nextBtn = await screen.findByRole('button', { name: /siguiente/i });
    fireEvent.click(nextBtn);

    const submitBtn = await screen.findByRole('button', { name: /guardar cambios/i });
    fireEvent.click(submitBtn);

    await waitFor(() => expect(onSave).toHaveBeenCalled());
    await waitFor(() => expect(onClose).toHaveBeenCalled());
  });
});
