import React from "react";
import { Route } from "react-router-dom";
import ProtectedRoute from "@/components/common/ProtectedRoute";

// Páginas
import NotificationsInbox from "../pages/NotificationsInbox";
import NotificationsHistory from "../pages/NotificationsHistory";
import NotificationDetail from "../pages/NotificationDetail";

const notificationsRoutes = [
    // Historial (es la ruta que usa el "Ver todas" del bell)
    <Route
        key="notifications-history"
        path="/notifications"
        element={
            <ProtectedRoute>
                <NotificationsHistory />
            </ProtectedRoute>
        }
    />,

    // Bandeja simple / más reciente
    <Route
        key="notifications-inbox"
        path="/notifications/inbox"
        element={
            <ProtectedRoute>
                <NotificationsInbox />
            </ProtectedRoute>
        }
    />,

    <Route
        key="notification-detail"
        path="/notifications/:id"
        element={
            <ProtectedRoute>
                <NotificationDetail />
            </ProtectedRoute>
        }
    />,

]
    ;

export default notificationsRoutes;
