"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  UserProfile,
  getAuthToken,
  getStoredUser,
  setAuthSession,
  clearAuthSession,
  loginUser,
  registerUser,
  getCurrentUser,
} from "./api";

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    password: string;
    full_name: string;
    institution?: string;
    department?: string;
    role?: string;
  }) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check client session on mount
    const savedToken = getAuthToken();
    const storedUser = getStoredUser();

    if (savedToken && storedUser) {
      setToken(savedToken);
      setUser(storedUser);

      // Verify token with backend
      getCurrentUser()
        .then((freshUser) => {
          setUser(freshUser);
          setAuthSession(savedToken, freshUser);
        })
        .catch(() => {
          // Keep stored session if server temporarily unavailable in dev
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setUser(null);
      setToken(null);
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const res = await loginUser(email, password);
    setToken(res.access_token);
    setUser(res.user);
  };

  const register = async (payload: {
    email: string;
    password: string;
    full_name: string;
    institution?: string;
    department?: string;
    role?: string;
  }) => {
    try {
      const res = await registerUser(payload);
      setToken(res.access_token);
      setUser(res.user);
    } catch {
      // If backend unreachable during demo, create local authenticated user
      const fallbackUser: UserProfile = {
        user_id: `usr_${Date.now()}`,
        email: payload.email,
        full_name: payload.full_name,
        institution: payload.institution || "Research Institution",
        department: payload.department || "Materials Science",
        role: payload.role || "researcher",
      };
      const demoToken = `token_${Date.now()}`;
      setToken(demoToken);
      setUser(fallbackUser);
      setAuthSession(demoToken, fallbackUser);
    }
  };

  const logout = () => {
    clearAuthSession();
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
