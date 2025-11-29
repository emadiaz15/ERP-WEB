// src/features/intake/router/intakeRoutes.jsx
import React from 'react';
import { Route } from 'react-router-dom';
import IntakeOrdersList from '../pages/IntakeOrdersList';

// Rutas de intake (por ahora sólo listado de órdenes)
const intakeRoutes = [
  <Route key="intake-orders" path="/intake/orders" element={<IntakeOrdersList />} />,
];

export default intakeRoutes;
