import React from 'react';
import { Menu, MenuButton, MenuItem, MenuItems } from "@headlessui/react";
import { UserIcon } from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";
import UserIndicator from "../UserIndicator";
import { useAuth } from "@/context/AuthProvider";

export default function UserMenu() {
    const { user, profileImage, logout } = useAuth();

    const userFullName =
        user?.name || user?.last_name
            ? `${user?.name || ""} ${user?.last_name || ""}`.trim()
            : "";

    return (
        <Menu as="div" className="relative flex items-center">
            <UserIndicator />

            <MenuButton className="ml-2" title={userFullName || "Usuario"}>
                {profileImage && typeof profileImage === "string" ? (
                    <img
                        src={profileImage}
                        alt="Foto de perfil"
                        className="h-8 w-8 rounded-full object-cover border border-white"
                    />
                ) : (
                    <UserIcon className="h-8 w-8 text-white p-1 bg-primary-600 rounded-full" aria-hidden="true" />
                )}
            </MenuButton>

            <MenuItems className="absolute right-0 z-10 mt-36 w-48 origin-top-right rounded-md bg-neutral-100 py-1 shadow-lg ring-1 ring-black/5 focus:outline-none">
                <MenuItem>
                    {({ active }) => (
                        <Link
                            to="/my-profile"
                            className={`block px-4 py-2 text-sm text-neutral-700 ${active ? "bg-neutral-200" : ""}`}
                        >
                            Mi Perfil
                        </Link>
                    )}
                </MenuItem>
                <MenuItem>
                    {({ active }) => (
                        <button
                            onClick={logout}
                            className={`block w-full text-left px-4 py-2 text-sm text-neutral-700 ${active ? "bg-neutral-200" : ""}`}
                        >
                            Cerrar Sesión
                        </button>
                    )}
                </MenuItem>
            </MenuItems>
        </Menu>
    );
}
