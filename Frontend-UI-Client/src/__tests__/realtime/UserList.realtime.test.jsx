import React from 'react';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import UserList from '@/features/user/pages/UserList';

// Mock Layout and heavy children
jest.mock('@/pages/Layout', () => ({
  __esModule: true,
  default: ({ children }) => <div data-testid="layout">{children}</div>,
}));

jest.mock('@/features/user/components/UserFilters', () => ({
  __esModule: true,
  default: () => <div data-testid="user-filters" />,
}));

jest.mock('@/features/user/components/UserTable', () => ({
  __esModule: true,
  default: ({ users = [] }) => <div data-testid="user-table">{users.length} users</div>,
}));

jest.mock('@/features/user/components/UserModals', () => ({
  __esModule: true,
  default: () => <div data-testid="user-modals" />,
}));

// Provide a minimal Auth context
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

// Mock pagination hook to intercept invalidate
const mockInvalidate = jest.fn();
jest.mock('@/hooks/useInfinitePageQuery', () => ({
  useInfinitePageQuery: () => ({
    items: [{ id: 1, username: 'test' }],
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
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </MemoryRouter>
  );
};

describe('UserList realtime listener', () => {
  beforeEach(() => mockInvalidate.mockClear());

  it('calls invalidate() on realtime User events', () => {
    renderWithProviders(<UserList />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'User', event: 'delete', payload: { id: 99 } } }));
  expect(mockInvalidate).toHaveBeenCalledTimes(1);
  });

  it('ignores unrelated models', () => {
    renderWithProviders(<UserList />);
    window.dispatchEvent(new CustomEvent('realtime-crud-event', { detail: { model: 'Product', event: 'update', payload: { id: 1 } } }));
    expect(mockInvalidate).not.toHaveBeenCalled();
  });
});
