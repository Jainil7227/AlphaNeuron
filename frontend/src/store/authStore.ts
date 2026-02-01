import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../types';
import { STORAGE_KEYS } from '../utils/constants';
import { authApi } from '../api';
import websocketService from '../api/websocket';

// ==========================================
// AUTH STORE STATE
// ==========================================

interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
}

interface AuthActions {
    login: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    setUser: (user: User) => void;
    setToken: (token: string) => void;
    clearError: () => void;
    checkAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

// ==========================================
// ZUSTAND STORE
// ==========================================

export const useAuthStore = create<AuthStore>()(
    persist(
        (set, get) => ({
            // Initial State
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            // Actions
            login: async (email: string, password: string) => {
                set({ isLoading: true, error: null });

                try {
                    const response = await authApi.login({ email, password });

                    // Store token in localStorage
                    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, response.token);

                    set({
                        user: response.user,
                        token: response.token,
                        isAuthenticated: true,
                        isLoading: false,
                        error: null,
                    });

                    // Connect WebSocket after successful login
                    websocketService.connect();
                } catch (error: any) {
                    set({
                        error: error.response?.data?.message || 'Login failed',
                        isLoading: false,
                        isAuthenticated: false,
                    });
                    throw error;
                }
            },

            logout: async () => {
                try {
                    await authApi.logout();
                } catch (error) {
                    console.error('Logout error:', error);
                } finally {
                    // Disconnect WebSocket
                    websocketService.disconnect();

                    // Clear state
                    set({
                        user: null,
                        token: null,
                        isAuthenticated: false,
                        error: null,
                    });

                    // Clear localStorage
                    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
                    localStorage.removeItem(STORAGE_KEYS.USER);
                }
            },

            setUser: (user: User) => {
                set({ user, isAuthenticated: true });
            },

            setToken: (token: string) => {
                localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
                set({ token, isAuthenticated: true });
            },

            clearError: () => {
                set({ error: null });
            },

            checkAuth: async () => {
                const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);

                if (!token) {
                    set({ isAuthenticated: false, user: null, token: null });
                    return;
                }


                try {
                    const user = await authApi.getMe();
                    set({
                        user,
                        token,
                        isAuthenticated: true,
                    });

                    // Connect WebSocket if authenticated
                    websocketService.connect();
                } catch (error) {
                    console.error('Auth check failed:', error);
                    set({
                        user: null,
                        token: null,
                        isAuthenticated: false,
                    });
                    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
