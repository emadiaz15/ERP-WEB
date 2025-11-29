import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import CreateCuttingOrderWizard from '@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard';

jest.mock('@/features/user/services/listUsers', () => ({
  listUsers: jest.fn().mockResolvedValue({ results: [{ id: 1, username: 'op' }] })
}));

jest.mock('@/features/product/hooks/useProductHooks', () => ({
  useProducts: () => ({ products: [{ id: 10, code: 'P-1', name: 'Prod' }], loading: false, isError: false })
}));

jest.mock('@/features/product/services/subproducts/subproducts', () => ({
  listSubproducts: jest.fn().mockResolvedValue({ results: [] })
}));

jest.mock('@/features/cuttingOrder/hooks/useCuttingOrders', () => ({
  useCreateCuttingOrder: () => [jest.fn().mockResolvedValue({ id: 123 }), { loading: false }]
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

describe('CreateCuttingOrderWizard', () => {
  it('cierra inmediatamente en éxito y llama onSave', async () => {
    const onClose = jest.fn();
    const onSave = jest.fn();

    render(
      <Wrapper>
        {/** Pasamos productId para evitar tener que seleccionar producto en el paso 1 */}
        <CreateCuttingOrderWizard isOpen onClose={onClose} onSave={onSave} productId={10} />
      </Wrapper>
    );

    // Paso 1: completar cantidad y asignar operador (nuevo requisito)
    const qtyInput = await screen.findByLabelText(/cantidad pedida/i);
    fireEvent.change(qtyInput, { target: { value: '100' } });

    // Abrir el select de "Asignar a" y elegir la opción "op" usando roles accesibles
    const assigneeCombobox = screen.getByRole('combobox', { name: /asignar a/i });
    fireEvent.click(assigneeCombobox);
    const listbox = await screen.findByRole('listbox');
    const assigneeOption = within(listbox).getByRole('option', { name: /op/i });
    fireEvent.click(assigneeOption);

    // Paso 1 → Paso 2
    const nextBtn = await screen.findByRole('button', { name: /siguiente/i });
    fireEvent.click(nextBtn);

    // Paso 2: submit directo (sin ítems, permitido porque hay cantidad pedida)
    const submitBtn = await screen.findByRole('button', { name: /crear corte/i });
    fireEvent.click(submitBtn);

    await waitFor(() => expect(onSave).toHaveBeenCalled());
    await waitFor(() => expect(onClose).toHaveBeenCalled());
  });
});
