// src/App.jsx
import React, { useState, useEffect } from 'react';
import { useRealtimeSync } from '@/features/realtime/useRealtimeSync';
import { useNavigate, useLocation } from 'react-router-dom';
import AppRoutes from "./router/Routes";                // ✅ ruta correcta
import { useSession } from "./hooks/useSession";
import SessionExpiredModal from "./components/SessionExpiredModal";
import NotificationsBridge from "@/features/notifications/components/NotificationsBridge"; // ✅
import NotificationsBootstrap from "@/features/notifications/components/NotificationsBootstrap"; // nuevo bootstrap
import NotificationsPrefetchIdle from '@/features/notifications/components/NotificationsPrefetchIdle';
import { useCuttingOrderModalStore } from "@/features/cuttingOrder/store/useCuttingOrderModalStore";
import ViewCuttingOrderModal from "@/features/cuttingOrder/components/ViewCuttingOrderModal";
import { useAuth } from "./context/AuthProvider";

const App = () => {
  const [sessionExpired, setSessionExpired] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuth();

  // Sincronización en tiempo real global (WebSocket + React Query)
  useRealtimeSync({ enabled: isAuthenticated });
  useSession({ intervalMs: 30000 });

  useEffect(() => {
    const handleSessionExpired = () => {
      const path = location.pathname;
      const isPublicRoute = path === '/' || path === '/login' || path.startsWith('/public/');
      if (!isPublicRoute) {
        setSessionExpired(true);
      }
    };

    window.addEventListener('sessionExpired', handleSessionExpired);
    return () => window.removeEventListener('sessionExpired', handleSessionExpired);
  }, [location.pathname]);

  const handleCloseSessionModal = () => {
    setSessionExpired(false);
    navigate('/');
  };
  const { isOpen, order, close, loading } = useCuttingOrderModalStore();

  return (
    <>
      {isAuthenticated && (
        <>
          <NotificationsBootstrap page={1} pageSize={10} />
          <NotificationsPrefetchIdle maxDepth={2} intervalMs={8000} />
          {/* 🔌 Bridge WS → store (montado una sola vez dentro del árbol autenticado) */}
          <NotificationsBridge />
        </>
      )}

      <AppRoutes />

      <SessionExpiredModal
        isOpen={sessionExpired}
        onConfirm={handleCloseSessionModal}
      />
      <ViewCuttingOrderModal
        isOpen={isOpen}
        order={order}
        onClose={close}
        loading={loading}
      />
    </>
  );
};

export default App;
