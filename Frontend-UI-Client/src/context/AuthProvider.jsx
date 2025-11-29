/* eslint-disable react-refresh/only-export-components */
import React from 'react';
import {
    createContext,
    useState,
    useEffect,
    useContext,
    useCallback,
} from "react";
import PropTypes from "prop-types";
import { useNavigate, useLocation } from "react-router-dom";
import { djangoApi } from "@/api/clients";
import { logoutHelper } from "./authHelpers";
import { shutdownAllSockets } from "@/lib/wsSingletons";
import { getAccessToken, clearTokens } from "@/utils/sessionUtils";
import { downloadProfileImage } from "@/features/user/services/downloadProfileImage";
// NotificationsBridge se monta globalmente en App.jsx

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [profileImage, setProfileImage] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const navigate = useNavigate();
    const location = useLocation();

    const loadProfileImage = async (userData) => {
        const rawUrl = userData?.image_signed_url || userData?.image_url;
        if (!rawUrl) {
            setProfileImage(null);
            return;
        }
        try {
            const imgUrl = await downloadProfileImage(rawUrl);
            setProfileImage(imgUrl || null);
        } catch (err) {
            console.warn("⚠️ No se pudo cargar la imagen de perfil:", err);
            setProfileImage(null);
        }
    };

    const logout = useCallback(async () => {
        try {
            await logoutHelper();
        } catch {
            // noop
        } finally {
            // 🔌 Cerrar websockets antes de limpiar tokens para evitar reconexiones con token vacío
            try { shutdownAllSockets(); } catch {}
            clearTokens();
            setUser(null);
            setIsAuthenticated(false);
            setProfileImage(null);
            setError(null);
            navigate("/", { replace: true });
        }
    }, [navigate]);

    // 🔐 Restaurar sesión al montar
    useEffect(() => {
        const validateToken = async () => {
            const accessToken = getAccessToken();

            if (!accessToken) {
                setIsAuthenticated(false);
                setLoading(false);
                return;
            }

            try {
                const { data } = await djangoApi.get("/users/profile/");
                setUser(data);
                setIsAuthenticated(true);
                await loadProfileImage(data);

                // 👉 Redirección automática si el usuario abre en "/" o "/login"
                if (location.pathname === "/" || location.pathname === "/login") {
                    navigate("/dashboard", { replace: true });
                }
            } catch {
                await logout(); // manejar expiración/401
            } finally {
                setLoading(false);
            }
        };

        validateToken();
        // Escucha expiración global del token (lanzada por axios interceptor)
        const onExpired = () => logout();
        window.addEventListener("sessionExpired", onExpired);
        return () => window.removeEventListener("sessionExpired", onExpired);
    }, [logout, navigate, location.pathname]);

    // 🚪 Login
    const login = async ({ username, password }) => {
        setError(null);
        setLoading(true);

        try {
            // 1) login y guardar tokens
            const res = await djangoApi.post("/users/login/", { username, password });
            const { access_token, refresh_token } = res.data;

            localStorage.setItem("accessToken", access_token);
            localStorage.setItem("refreshToken", refresh_token);

            // 2) perfil
            const { data: profile } = await djangoApi.get("/users/profile/");
            setUser(profile);
            setIsAuthenticated(true);
            await loadProfileImage(profile);
            // Guardar perfil completo en localStorage para acceso global
            localStorage.setItem("user", JSON.stringify(profile));

            // 3) ir al dashboard sin recargar la página
            navigate("/dashboard", { replace: true });
        } catch (err) {
            setError(err?.response?.data?.detail || "Credenciales inválidas");
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                isStaff: !!user?.is_staff,
                isAuthenticated,
                loading,
                error,
                profileImage,
                login,
                logout,
            }}
        >
            {/* WS de notificaciones se maneja en App.jsx mediante <NotificationsBridge /> */}

            {children}
        </AuthContext.Provider>
    );
};

AuthProvider.propTypes = {
    children: PropTypes.node.isRequired,
};

export default AuthProvider;
export const useAuth = () => useContext(AuthContext);
