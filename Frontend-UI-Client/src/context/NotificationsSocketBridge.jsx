// src/context/NotificationsSocketBridge.jsx
import { useCallback } from "react";
import PropTypes from "prop-types";
import { useNotificationsSocket } from "@/features/notifications/hooks/useNotificationsSocket";
import { useNotificationsStore } from "@/features/notifications/stores/useNotificationsStore";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

export default function NotificationsSocketBridge({ onNewNotification }) {
    const pushFromWS = useNotificationsStore((s) => s.pushFromWS);
    const navigate = useNavigate();

    const handleNewNotification = useCallback(
        (notif) => {
            // 1) Mando al store
            pushFromWS(notif);

            // 2) Opcional: callback superior (si querés enganchar otra cosa desde AuthProvider)
            onNewNotification?.(notif);

            // 3) Toast (eliminado: solo NotificationsToaster muestra popups visuales)
        },
        [onNewNotification, pushFromWS]
    );

    useNotificationsSocket(handleNewNotification);
    return null;
}

NotificationsSocketBridge.propTypes = {
    onNewNotification: PropTypes.func,
};
