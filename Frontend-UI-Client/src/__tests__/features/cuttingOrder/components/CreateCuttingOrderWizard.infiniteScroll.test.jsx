import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/context/AuthProvider';
import CreateCuttingOrderWizard from '@/features/cuttingOrder/components/wizard/CreateCuttingOrderWizard';

// Mock users
jest.mock('@/features/user/services/listUsers', () => ({
  listUsers: jest.fn().mockResolvedValue({ results: [{ id: 1, username: 'op' }] })
}));

// Mock products hook
jest.mock('@/features/product/hooks/useProductHooks', () => ({
  useProducts: () => ({ products: [{ id: 10, code: 'P-1', name: 'Prod' }], loading: false, isError: false })
}));

// Mock create order
jest.mock('@/features/cuttingOrder/hooks/useCuttingOrders', () => ({
  useCreateCuttingOrder: () => [jest.fn().mockResolvedValue({ id: 999 }), { loading: false }]
}));

// Mock listSubproducts service for next pages
const listSubproductsMock = jest.fn();
jest.mock('@/features/product/services/subproducts/subproducts', () => ({
  listSubproducts: (...args) => listSubproductsMock(...args)
}));

// Mock useListSubproducts hook (first page)
jest.mock('@/features/product/hooks/useSubproductHooks', () => ({
  useListSubproducts: () => ({
    subproducts: [
      { id: 1, status: true, stock: { available_meters: 10 } },
      { id: 2, status: true, stock: { available_meters: 8 } },
    ],
    isLoading: false,
    isError: false,
    error: null,
    nextPageUrl: '/inventory/products/10/subproducts/?page=2',
  })
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

describe('CreateCuttingOrderWizard - Infinite Scroll', () => {
  beforeEach(() => {
    listSubproductsMock.mockReset();
  });

  it('carga la siguiente página al activar el sentinel y via botón', async () => {
    // Configure next page response
    listSubproductsMock.mockResolvedValueOnce({
      results: [
        { id: 3, status: true, stock: { available_meters: 5 } },
        { id: 4, status: true, stock: { available_meters: 3 } },
      ],
      next: null,
    });

    render(
      <Wrapper>
        <CreateCuttingOrderWizard isOpen onClose={() => {}} onSave={() => {}} productId={10} />
      </Wrapper>
    );

    // Ir a Paso 2 rápidamente: completar requisitos mínimos del Paso 1
    fireEvent.change(await screen.findByLabelText(/cantidad pedida/i), { target: { value: '10' } });
    const assignee = screen.getByRole('combobox', { name: /asignar a/i });
    fireEvent.click(assignee);
    const option = await screen.findByRole('option', { name: /op/i });
    fireEvent.click(option);
    fireEvent.click(screen.getByRole('button', { name: /siguiente/i }));

    // Debe mostrar cards de la primera página
    expect(await screen.findAllByRole('button', { name: /seleccionar/i })).toBeTruthy();

    // Forzar el sentinel: como jsdom no implementa IntersectionObserver real,
    // invocamos manualmente el botón de "Cargar más"
    const loadMoreBtn = await screen.findByRole('button', { name: /cargar más/i });
    fireEvent.click(loadMoreBtn);

    await waitFor(() => {
      expect(listSubproductsMock).toHaveBeenCalled();
    });
  });
});
