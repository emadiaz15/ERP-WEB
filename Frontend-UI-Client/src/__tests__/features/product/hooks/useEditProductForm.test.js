
import React from 'react';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useEditProductForm } from '../../../../features/product/hooks/useEditProductForm';

const queryClient = new QueryClient();

describe('useEditProductForm', () => {
  it('puede llamarse sin errores', () => {
    // Mock completo esperado por el hook
    // Mock completo esperado por el hook
    const mockProduct = {
      id: 1,
      code: 'P001',
      name: 'Producto Test',
      category: { id: 1, name: 'Cat', description: '' },
      description: '',
      price: 0,
      stock: 0,
    };
    const mockProducts = [
      { id: 1, code: 'P001', name: 'Producto Test', category: { id: 1, name: 'Cat', description: '' }, description: '', price: 0, stock: 0 },
      { id: 2, code: 'P002', name: 'Otro', category: { id: 2, name: 'Cat2', description: '' }, description: '', price: 0, stock: 0 }
    ];
    const mockCategories = [
      { id: 1, name: 'Cat', description: '' },
      { id: 2, name: 'Cat2', description: '' }
    ];
    const mockDeleteMut = { deleting: false, deleteError: null };
    const mockUpdateProduct = jest.fn();
    const mockUploadMut = {};
    const mockOnSave = jest.fn();
    const mockOnClose = jest.fn();
    const wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    renderHook(() => useEditProductForm({
      product: mockProduct,
      products: mockProducts,
      categories: mockCategories,
      deleteMut: mockDeleteMut,
      updateProduct: mockUpdateProduct,
      uploadMut: mockUploadMut,
      onSave: mockOnSave,
      onClose: mockOnClose
    }), { wrapper });
  });
});
