// src/routes/AppRoutes.jsx
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from '../pages/Home';
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import Unauthorized from '../pages/Unauthorized';
import ProtectedRoute from '../components/common/ProtectedRoute';
import PublicProductFiles from '../features/product/pages/PublicProductFiles';

// rutas “anidadas”
import cuttingOrderRoutes from '../features/cuttingOrder/router/cuttingOrderRoutes';
import productRoutes from '../features/product/router/productRoutes';
import userRoutes from '../features/user/router/userRoutes';           // ahora sólo user-list
import categoryRoutes from '../features/category/router/categoryRoutes';
import notificationsRoutes from '../features/notifications/router/NotificationsRoutes';
import stocksRoutes from '../features/stocks/router/stocksRoutes';
import intakeRoutes from '../features/intake/router/intakeRoutes'; // <-- agregado

// importa aquí MyProfile directamente
import MyProfile from '../features/user/pages/MyProfile';

const AppRoutes = () => (
  <Routes>
    {/* PÚBLICAS */}
    <Route path="/" element={<Login />} />
    <Route path="/unauthorized" element={<Unauthorized />} />
    <Route path="/public/product-files" element={<PublicProductFiles />} />

    {/* CUALQUIERA autenticado */}
    <Route element={<ProtectedRoute />}>
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/my-profile" element={<MyProfile />} />
      {cuttingOrderRoutes}
      {productRoutes}
      {notificationsRoutes}
      {stocksRoutes}
      {intakeRoutes}{/* nuevas rutas intake */}
    </Route>

    {/* SOLO staff */}
    <Route element={<ProtectedRoute adminOnly />}>
      {userRoutes}       {/* aquí userRoutes exportará sólo /users-list */}
      {categoryRoutes}
    </Route>

    {/* fallback */}
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

export default AppRoutes;
