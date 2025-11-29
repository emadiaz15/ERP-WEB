import React from "react";
import { Route } from "react-router-dom";
import ProtectedRoute from "../../../components/common/ProtectedRoute";
import CuttingOrdersList from "../pages/CuttingOrdersList";

const cuttingOrderRoutes = [
  <Route
    key="cutting-orders"
    path="/cutting-orders"
    element={
      <ProtectedRoute>
        <CuttingOrdersList />
      </ProtectedRoute>
    }
  />

];

export default cuttingOrderRoutes;
