import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthProvider';
import { listIntakeOrders } from '@/features/intake/services/intakeOrders';

import {
  HomeIcon,
  UserIcon,
  CubeIcon,
  ClipboardDocumentListIcon,
  UsersIcon,
  TagIcon,
  Squares2X2Icon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  DocumentDuplicateIcon
} from '@heroicons/react/24/outline';

const Sidebar = ({ onToggle }) => {
  const navigate = useNavigate();
  const { logout, isStaff } = useAuth();
  const [collapsed, setCollapsed] = useState(true);
  const [ingestCount, setIngestCount] = useState(0);
  const [loadingIngest, setLoadingIngest] = useState(false);

  const fetchIngestCount = async () => {
    try {
      setLoadingIngest(true);
      const data = await listIntakeOrders({ flow_status: 'new', page_size: 1 }, { force: true });
      // DRF paginado: count, sino fallback a results length
      const count = data.count ?? data.results?.length ?? 0;
      setIngestCount(count);
    } catch (e) {
      setIngestCount(0);
    } finally {
      setLoadingIngest(false);
    }
  };

  useEffect(() => {
    fetchIngestCount();
    const id = setInterval(fetchIngestCount, 30000); // refresco cada 30s
    return () => clearInterval(id);
  }, []);

  const sidebarItems = [
    { label: 'Inicio', icon: HomeIcon, onClick: () => navigate('/dashboard') },
    { label: 'Productos', icon: CubeIcon, onClick: () => navigate('/product-list') },
    { label: 'Órdenes de Corte', icon: ClipboardDocumentListIcon, onClick: () => navigate('/cutting-orders') },
    { label: 'Notas de Pedidos', icon: DocumentDuplicateIcon, onClick: () => navigate('/intake/orders'), badge: ingestCount },
    { label: 'Usuarios', icon: UsersIcon, onClick: () => navigate('/users-list'), adminOnly: true },
    { label: 'Cerrar Sesión', icon: ArrowRightOnRectangleIcon, onClick: logout, isLogout: true }
  ];

  const toggleCollapsed = () => {
    const newState = !collapsed;
    setCollapsed(newState);
    if (onToggle) onToggle(newState);
  };

  useEffect(() => {
    if (onToggle) onToggle(collapsed);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cerrar sidebar automáticamente en pantallas pequeñas
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setCollapsed(true);
        if (onToggle) onToggle(true);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [onToggle]);

  // Filtrar ítems según rol
  const visibleItems = sidebarItems.filter(item =>
    // siempre mostrar si no es adminOnly, o si lo es y el usuario sí es staff
    (!item.adminOnly || isStaff)
  );

  return (
    <aside
      className={`bg-primary-500 text-white h-screen fixed top-14 left-0 z-40 transition-all duration-300
        ${collapsed ? 'w-20' : 'w-64'} flex flex-col justify-between`}
    >
      <div>
        <div className="px-2 pt-4">
          <button
            onClick={toggleCollapsed}
            className="w-full flex items-center py-3 px-4 mb-2 rounded hover:bg-primary-600 transition-all"
          >
            <Bars3Icon className="h-5 w-5" />
            {!collapsed && <span className="ml-3 text-base">Menú</span>}
          </button>
        </div>

        <div className="flex flex-col px-2">
          {visibleItems.map(({ label, icon: Icon, onClick, isLogout, badge }, idx) => (
            <button
              key={idx}
              onClick={onClick}
              className={`w-full flex items-center py-3 px-4 mb-2 rounded transition-all ${isLogout
                ? 'bg-accent-500 hover:bg-accent-400'
                : 'hover:bg-primary-600'
                }`}
            >
              <Icon className="h-5 w-5" />
              {!collapsed && (
                <span className="ml-3 text-base flex items-center gap-2">
                  {label}
                  {badge > 0 && (
                    <span className="inline-flex items-center justify-center min-w-[1.25rem] h-5 px-1 rounded-full bg-accent-500 text-[10px] font-semibold">
                      {badge > 999 ? '999+' : badge}
                    </span>
                  )}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
