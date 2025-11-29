import React from 'react';
import { render, screen } from '@testing-library/react';
import Sidebar from '@/components/common/Sidebar';

jest.mock('@heroicons/react/24/outline', () => ({
  HomeIcon: () => <svg />, CubeIcon: () => <svg />, ClipboardDocumentListIcon: () => <svg />, UsersIcon: () => <svg />, ArrowRightOnRectangleIcon: () => <svg />, Bars3Icon: () => <svg />, DocumentDuplicateIcon: () => <svg />
}));

jest.mock('@/context/AuthProvider', () => ({
  useAuth: () => ({ logout: jest.fn(), isStaff: true })
}));

jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn()
}));

describe('Sidebar intake link', () => {
  it('muestra el botón Notas Ingesta', () => {
    render(<Sidebar />);
    expect(screen.getByText('Notas Ingesta')).toBeInTheDocument();
  });
});
