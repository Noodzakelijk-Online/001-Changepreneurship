import React, { createContext, useContext, useState, useEffect } from "react";
import apiService from "../services/api";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

// Development bypass mode - set to false to use real authentication
const BYPASS_AUTH = false;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(
    BYPASS_AUTH
      ? {
          id: "demo-user",
          username: "demo",
          email: "demo@changepreneurship.com",
        }
      : null
  );
  const [isAuthenticated, setIsAuthenticated] = useState(BYPASS_AUTH);
  const [isLoading, setIsLoading] = useState(!BYPASS_AUTH);

  // Initialize authentication state
  useEffect(() => {
    if (BYPASS_AUTH) {
      setIsLoading(false);
      return;
    }

    const initAuth = async () => {
      try {
        if (apiService.isAuthenticated()) {
          const result = await apiService.verifySession();
          if (result.success && result.data?.user) {
            setUser(result.data.user);
            setIsAuthenticated(true);
          } else {
            apiService.clearSession();
          }
        }
      } catch (error) {
        console.warn("Session verification failed:", error.message);
        apiService.clearSession();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);
  const register = async (userData) => {
    if (BYPASS_AUTH) {
      return { success: true, data: { user } };
    }

    try {
      const result = await apiService.register(userData);
      if (result.success && result.data?.user) {
        setUser(result.data.user);
        setIsAuthenticated(true);
      }
      return result;
    } catch (error) {
      console.error("Registration error:", error.message);
      return { success: false, error: error.message };
    }
  };

  const login = async (credentials) => {
    if (BYPASS_AUTH) {
      return { success: true, data: { user } };
    }

    try {
      const result = await apiService.login(credentials);
      if (result.success && result.data?.user) {
        setUser(result.data.user);
        setIsAuthenticated(true);
      }
      return result;
    } catch (error) {
      console.error("Login error:", error.message);
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    if (BYPASS_AUTH) {
      return;
    }

    try {
      await apiService.logout();
    } catch (error) {
      console.error("Logout error:", error.message);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const getProfile = async () => {
    if (BYPASS_AUTH) {
      return { success: true, data: { user } };
    }

    if (!apiService.isAuthenticated()) {
      return { success: false, error: "Not authenticated" };
    }

    try {
      const result = await apiService.getProfile();
      if (result.success && result.data?.user) {
        setUser(result.data.user);
      }
      return result;
    } catch (error) {
      console.error("Profile fetch error:", error.message);
      return { success: false, error: error.message };
    }
  };

  const apiCall = async (endpoint, options = {}) => {
    if (BYPASS_AUTH) {
      // In bypass mode, return mock successful responses
      return new Response(JSON.stringify({ success: true, data: {} }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }

    if (!apiService.isAuthenticated()) {
      throw new Error("Not authenticated");
    }

    const config = {
      headers: apiService.getHeaders(),
      ...options,
    };

    const response = await fetch(
      `${apiService.getApiBaseUrl()}${endpoint}`,
      config
    );

    if (response.status === 401) {
      // Token expired or invalid
      await logout();
      throw new Error("Session expired");
    }

    return apiService.handleResponse(response);
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    sessionToken: apiService.getSessionToken(),
    register,
    login,
    logout,
    getProfile,
    apiCall,
    apiService, // Expose apiService for direct access
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
