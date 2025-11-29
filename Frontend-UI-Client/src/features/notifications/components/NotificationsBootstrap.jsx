import { useEffect, useRef } from 'react';
import { useNotificationsStore } from '../stores/useNotificationsStore';
import { useAuth } from '@/context/AuthProvider';

/**
 * Ensures notifications initial page is fetched exactly once at app startup.
 * Place this high in the tree (e.g. inside App before routes) so that bell, inbox, etc.
 * don't all trigger their own first fetch.
 */
export default function NotificationsBootstrap({ page = 1, pageSize, children }) {
  const fetchPage = useNotificationsStore(s => s.fetchPage);
  const did = useRef(false);
  const { isAuthenticated } = useAuth();
  useEffect(() => {
    if (!isAuthenticated) return;
    if (did.current) return;
    did.current = true;
    fetchPage(page, { page_size: pageSize, force: true });
  }, [fetchPage, page, pageSize, isAuthenticated]);
  return children || null;
}
