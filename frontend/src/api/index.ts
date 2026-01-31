import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, STORAGE_KEYS } from '../utils/constants';
import type {
    ApiResponse,
    PaginatedResponse,
    LoginCredentials,
    LoginResponse,
    Vehicle,
    Load,
    Route,
    FleetMetrics,
    RevenueMetrics,
} from '../types';

// ==========================================
// AXIOS INSTANCE
// ==========================================

const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// ==========================================
// REQUEST INTERCEPTOR
// ==========================================

api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// ==========================================
// RESPONSE INTERCEPTOR
// ==========================================

api.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => {
        if (error.response?.status === 401) {
            // Unauthorized - clear token and redirect to login
            localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
            localStorage.removeItem(STORAGE_KEYS.USER);
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ==========================================
// AUTH API
// ==========================================

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
        const response = await api.post<ApiResponse<LoginResponse>>('/api/auth/login', credentials);
        return response.data.data!;
    },

    logout: async (): Promise<void> => {
        await api.post('/api/auth/logout');
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
    },

    getMe: async (): Promise<any> => {
        const response = await api.get<ApiResponse<any>>('/api/auth/me');
        return response.data.data;
    },
};

// ==========================================
// VEHICLE API
// ==========================================

export const vehicleApi = {
    getAll: async (): Promise<Vehicle[]> => {
        const response = await api.get<ApiResponse<Vehicle[]>>('/api/vehicles');
        return response.data.data || [];
    },

    getById: async (id: string): Promise<Vehicle> => {
        const response = await api.get<ApiResponse<Vehicle>>(`/api/vehicles/${id}`);
        return response.data.data!;
    },

    updateLocation: async (id: string, location: { lat: number; lng: number }): Promise<void> => {
        await api.patch(`/api/vehicles/${id}/location`, location);
    },

    updateStatus: async (id: string, status: string): Promise<void> => {
        await api.patch(`/api/vehicles/${id}/status`, { status });
    },
};

// ==========================================
// LOAD API
// ==========================================

export const loadApi = {
    getAll: async (params?: {
        status?: string;
        page?: number;
        pageSize?: number;
    }): Promise<PaginatedResponse<Load>> => {
        const response = await api.get<ApiResponse<PaginatedResponse<Load>>>('/api/loads', { params });
        return response.data.data!;
    },

    getById: async (id: string): Promise<Load> => {
        const response = await api.get<ApiResponse<Load>>(`/api/loads/${id}`);
        return response.data.data!;
    },

    create: async (load: Partial<Load>): Promise<Load> => {
        const response = await api.post<ApiResponse<Load>>('/api/loads', load);
        return response.data.data!;
    },

    assign: async (id: string, vehicleId: string): Promise<Load> => {
        const response = await api.post<ApiResponse<Load>>(`/api/loads/${id}/assign`, { vehicleId });
        return response.data.data!;
    },
};

// ==========================================
// ROUTE API
// ==========================================

export const routeApi = {
    getAll: async (): Promise<Route[]> => {
        const response = await api.get<ApiResponse<Route[]>>('/api/routes');
        return response.data.data || [];
    },

    getById: async (id: string): Promise<Route> => {
        const response = await api.get<ApiResponse<Route>>(`/api/routes/${id}`);
        return response.data.data!;
    },

    optimize: async (vehicleId: string, loadIds: string[]): Promise<Route> => {
        const response = await api.post<ApiResponse<Route>>('/api/routes/optimize', {
            vehicleId,
            loadIds,
        });
        return response.data.data!;
    },
};

// ==========================================
// ANALYTICS API
// ==========================================

export const analyticsApi = {
    getFleetMetrics: async (): Promise<FleetMetrics> => {
        const response = await api.get<ApiResponse<FleetMetrics>>('/api/analytics/fleet-metrics');
        return response.data.data!;
    },

    getRevenue: async (): Promise<RevenueMetrics> => {
        const response = await api.get<ApiResponse<RevenueMetrics>>('/api/analytics/revenue');
        return response.data.data!;
    },
};

// ==========================================
// EXPORT DEFAULT
// ==========================================

export default api;
