import React from 'react';
import { Route } from 'react-router-dom';
import ProtectedRoute from '../../../components/common/ProtectedRoute';

import ProductStockEvent from '../pages/ProductStockEvent';
import SubproductStockEvent from '../pages/SubproductStockEvent';

const stocksRoutes = [
    <Route
        key="product-stock-events"
        path="/products/:productId/stock-history"
        element={
            <ProtectedRoute>
                <ProductStockEvent />
            </ProtectedRoute>
        }
    />,
    <Route
        key="subproduct-stock-history"
        path="/subproducts/:subproductId/stock-history"
        element={
            <ProtectedRoute>
                <SubproductStockEvent />
            </ProtectedRoute>
        }
    />
];

export default stocksRoutes;
