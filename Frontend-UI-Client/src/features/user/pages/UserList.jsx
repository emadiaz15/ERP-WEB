// src/features/user/pages/UserList.jsx
import React, { useState, useCallback, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import Toolbar from "../../../components/common/Toolbar";
import SuccessMessage from "../../../components/common/SuccessMessage";
import ErrorMessage from "../../../components/common/ErrorMessage";
import Layout from "../../../pages/Layout";
import UserTable from "../components/UserTable";
import UserModals from "../components/UserModals";
import UserFilters from "../components/UserFilters";

import { registerUser } from "../services/registerUser";
import { updateUser } from "../services/updateUser";
import { resetUserPassword } from "../services/resetUserPassword";
import { deleteUser } from "../services/deleteUser";

// ✅ Hook genérico raíz (DRF PageNumberPagination)
import { useInfinitePageQuery } from "@/hooks/useInfinitePageQuery";

const UserList = () => {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState({
    full_name: "",
    dni: "",
    is_active: "true",
    is_staff: "",
  });

  const [showSuccess, setShowSuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [modalState, setModalState] = useState({ type: null, userData: null });
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionError, setActionError] = useState(null);

  // 🌀 Listado con infinite scroll
  const {
    items: users,            // array aplanado de todas las páginas
    isLoading,
    isError,
    error: fetchError,
    fetchNextPage,           // para el sentinel
    hasNextPage,
    isFetchingNextPage,
    invalidate,
  } = useInfinitePageQuery({
    key: ["users", filters],
    url: "/users/list/",          // tu axiosInstance ya tiene baseURL /api/v1
    params: filters,
    pageSize: 10,
    enabled: true,
  });

  // El overlay de Layout usará isLoading directamente

  const openCreateModal = useCallback(() => {
    setModalState({ type: "create", userData: null });
  }, []);

  const openEditModal = useCallback((user) => {
    setModalState({ type: "edit", userData: user });
  }, []);

  const openViewModal = useCallback((user) => {
    setModalState({ type: "view", userData: user });
  }, []);

  const openDeleteConfirmModal = useCallback((user) => {
    setModalState({ type: "deleteConfirm", userData: user });
  }, []);

  const closeModal = useCallback(() => {
    setModalState({ type: null, userData: null });
    setActionError(null);
  }, []);

  const handleActionSuccess = useCallback(
    (message, { immediateInvalidate = false } = {}) => {
      setSuccessMessage(message);
      setShowSuccess(true);
      closeModal();
      if (immediateInvalidate) invalidate();
      setTimeout(() => setShowSuccess(false), 3000);
    },
    [closeModal, invalidate]
  );

  // Helpers de patch local sobre listas infinitas bajo root 'users'
  const prependUserToLists = useCallback((user) => {
    if (!user) return;
    queryClient.setQueriesData({ queryKey: ["users"], exact: false, type: "active" }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      const pages = old.pages.slice();
      const first = pages[0] || {};
      const results = Array.isArray(first.results) ? first.results : [];
      pages[0] = {
        ...first,
        results: [user, ...results],
        count: typeof first.count === "number" ? first.count + 1 : first.count,
      };
      return { ...old, pages };
    });
  }, [queryClient]);

  const replaceUserInLists = useCallback((user) => {
    if (!user) return;
    queryClient.setQueriesData({ queryKey: ["users"], exact: false, type: "active" }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      let replaced = false;
      const pages = old.pages.map((p) => {
        const results = Array.isArray(p?.results)
          ? p.results.map((r) => {
              if (r?.id === user.id) {
                replaced = true;
                return { ...r, ...user };
              }
              return r;
            })
          : p?.results;
        return { ...p, results };
      });
      return replaced ? { ...old, pages } : old;
    });
  }, [queryClient]);

  const removeUserFromLists = useCallback((userId) => {
    if (userId == null) return;
    queryClient.setQueriesData({ queryKey: ["users"], exact: false, type: "active" }, (old) => {
      if (!old || !Array.isArray(old.pages)) return old;
      let changed = false;
      const pages = old.pages.map((p) => {
        const before = Array.isArray(p?.results) ? p.results.length : 0;
        const results = Array.isArray(p?.results) ? p.results.filter((u) => u?.id !== userId) : p?.results;
        if (Array.isArray(p?.results) && results.length !== before) changed = true;
        return {
          ...p,
          results,
          count: typeof p.count === "number" ? Math.max(0, p.count - (before - (results?.length ?? 0))) : p.count,
        };
      });
      return changed ? { ...old, pages } : old;
    });
  }, [queryClient]);

  const handleRegisterUser = useCallback(
    async (newUserData) => {
      setIsProcessing(true);
      setActionError(null);
      try {
        const created = await registerUser(newUserData);
        // Patch inmediato en listas
        prependUserToLists(created);
        handleActionSuccess("Usuario creado exitosamente.");
        // Refetch con pequeño retraso para evitar carreras con caché
        setTimeout(() => invalidate(), 150);
      } catch (err) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "Error al crear el usuario.";
        setActionError({ message: errorMsg });
        throw err;
      } finally {
        setIsProcessing(false);
      }
    },
    [handleActionSuccess, prependUserToLists, invalidate]
  );

  const handleUpdateUser = useCallback(
    async (userId, updatedData) => {
      setIsProcessing(true);
      setActionError(null);
      try {
        const updatedResponse = await updateUser(userId, updatedData);
        const username =
          updatedResponse?.username ||
          updatedResponse?.user?.username ||
          "desconocido";
        // Patch inmediato en listas
        replaceUserInLists(updatedResponse);
        handleActionSuccess(`Usuario "${username}" actualizado.`);
        // Refetch con pequeño retraso
        setTimeout(() => invalidate(), 150);
        return updatedResponse;
      } catch (err) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "Error al actualizar el usuario.";
        setActionError({ message: errorMsg });
        throw err;
      } finally {
        setIsProcessing(false);
      }
    },
    [handleActionSuccess, replaceUserInLists, invalidate]
  );

  const handlePasswordReset = useCallback(
    async (userId, passwordData) => {
      setIsProcessing(true);
      setActionError(null);
      try {
        await resetUserPassword(userId, passwordData);
        handleActionSuccess(
          `Contraseña actualizada para el usuario ID ${userId}.`
        );
      } catch (err) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "Error al cambiar contraseña.";
        setActionError({ message: errorMsg });
        throw err;
      } finally {
        setIsProcessing(false);
      }
    },
    [handleActionSuccess]
  );

  const handleDeleteUser = useCallback(
    async (userToDelete) => {
      if (!userToDelete) return;
      setIsProcessing(true);
      setActionError(null);
      try {
        await deleteUser(userToDelete.id);
        // Patch inmediato: remover de listas
        removeUserFromLists(userToDelete.id);
        handleActionSuccess(`Usuario "${userToDelete.username}" eliminado (soft).`);
        // Refetch con retraso
        setTimeout(() => invalidate(), 150);
      } catch (err) {
        const errorMsg =
          err?.response?.data?.detail ||
          err?.message ||
          "Error al desactivar el usuario.";
        setActionError({ message: errorMsg });
      } finally {
        setIsProcessing(false);
      }
    },
    [handleActionSuccess, removeUserFromLists, invalidate]
  );

  // Refrescar en eventos realtime (crear/actualizar/eliminar usuario) con dedupe
  useEffect(() => {
    const map = (typeof window !== 'undefined') ? (window.__rtDedupe ||= new Map()) : new Map();
    const shouldDedupe = (key, ttlMs = 700) => {
      const now = Date.now();
      const last = map.get(key) || 0;
      if (now - last < ttlMs) return true;
      map.set(key, now);
      return false;
    };
    function onRealtime(e) {
      const msg = e?.detail;
      if (!msg || msg.model !== 'User') return;
      const k = `User:${msg.event}:${msg.payload?.id ?? 'any'}`;
      if (shouldDedupe(k)) return;
      // Pequeño retraso para evitar carreras con invalidación del backend
      setTimeout(() => invalidate(), 150);
    }
    window.addEventListener('realtime-crud-event', onRealtime);
    return () => window.removeEventListener('realtime-crud-event', onRealtime);
  }, [invalidate]);

  return (
    <>
  <Layout isLoading={isLoading}>
        {showSuccess && (
          <div className="fixed top-20 right-5 z-[10000]">
            <SuccessMessage
              message={successMessage}
              onClose={() => setShowSuccess(false)}
            />
          </div>
        )}

        <div className="p-3 md:p-4 lg:p-6 mt-6">
          <Toolbar
            title="Lista de Usuarios"
            onButtonClick={openCreateModal}
            buttonText="Crear Usuario"
          />

          <UserFilters filters={filters} onChange={setFilters} />

          {isError && !isLoading && (
            <div className="my-4">
              <ErrorMessage
                message={fetchError?.message || "Error al cargar datos."}
                onClose={() => setActionError(null)}
              />
            </div>
          )}

          {!isLoading && users.length > 0 && (
            <UserTable
              users={users}
              openViewModal={openViewModal}
              openEditModal={openEditModal}
              openDeleteConfirmModal={openDeleteConfirmModal}
              // 👇 Props para infinite scroll dentro de la tabla
              onLoadMore={fetchNextPage}
              hasNextPage={!!hasNextPage}
              isFetchingNextPage={isFetchingNextPage}
            />
          )}

          {!isLoading && users.length === 0 && (
            <div className="text-center py-10 px-4 mt-4 bg-white rounded-lg shadow">
              <p className="text-gray-500">No se encontraron usuarios.</p>
            </div>
          )}
        </div>
      </Layout>

      <UserModals
        modalState={modalState}
        closeModal={closeModal}
        onRegisterUser={handleRegisterUser}
        onUpdateUser={handleUpdateUser}
        onDeleteUser={handleDeleteUser}
        onPasswordReset={handlePasswordReset}
        handleActionSuccess={handleActionSuccess}
        isProcessing={isProcessing}
        actionError={actionError}
      />
    </>
  );
};

export default UserList;
