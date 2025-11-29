// src/components/common/Navbar.jsx
import React from 'react';
import { Link } from "react-router-dom";
import NotificationBell from "./NotificationBell";
import CuttingCartButton from "./CuttingCartButton";
import UserMenu from "./UserMenu";
import { useAuth } from "@/context/AuthProvider";

const Navbar = () => {
  const { user } = useAuth(); // ← trae el usuario autenticado

  return (
    <nav className="fixed top-0 z-50 w-full bg-primary-500" aria-label="Barra de navegación">
      <div className="px-3 py-3 lg:px-5 lg:pl-3">
        <div className="flex items-center justify-between">
          {/* Logo e Inicio */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center" aria-label="Ir al dashboard">
              <img src="/home-img.png" className="h-8 me-3" alt="Logo" />
              <span className="self-center text-xl font-semibold sm:text-2xl whitespace-nowrap text-neutral-50">
                Sistema de Gestión Comercial
              </span>
            </Link>
          </div>

          {/* Acciones derecha */}
          <div className="flex items-center space-x-4 relative">
            {/* Mostrar el icono SOLO si el usuario es staff/admin */}
            {user?.is_staff && <CuttingCartButton />}
            <NotificationBell />
            <UserMenu />
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
