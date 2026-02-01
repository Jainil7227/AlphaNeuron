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
        // Backend expects { phone, password } - send email in phone field
        const response = await api.post('/api/v1/auth/login', {
            phone: credentials.email,  // Backend accepts email in phone field
            password: credentials.password,
        });

        // Backend returns { access_token, refresh_token, token_type, expires_in }
        const tokenData = response.data;

        // Create a mock user for demo mode (real user data would come from /me endpoint)
        const demoUser: any = {
            id: 'demo-user',
            name: credentials.email.includes('admin') ? 'Admin User' :
                credentials.email.includes('driver') ? 'Demo Driver' : 'Fleet Operator',
            email: credentials.email,
            phone: '+919999999999',
            role: credentials.email.includes('admin') ? 'ADMIN' :
                credentials.email.includes('driver') ? 'DRIVER' : 'FLEET_MANAGER',
            createdAt: new Date().toISOString(),
        };

        return {
            user: demoUser,
            token: tokenData.access_token,
        };
    },

    logout: async (): Promise<void> => {
        try {
            await api.post('/api/v1/auth/logout');
        } catch (error) {
            // Ignore logout errors
        }
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
    },

    getMe: async (): Promise<any> => {
        const response = await api.get<ApiResponse<any>>('/api/v1/auth/me');
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
        // Use demo endpoint for testing
        try {
            const response = await api.get('/api/v1/demo/fleet-stats');
            const data = response.data.data;
            return {
                totalVehicles: data.total_vehicles,
                activeVehicles: data.on_mission_vehicles,
                idleVehicles: data.available_vehicles,
                maintenanceVehicles: data.maintenance_vehicles,
                averageUtilization: data.utilization_percent,
                totalDistanceCovered: data.total_distance_today_km,
            };
        } catch (error) {
            return {
                totalVehicles: 5,
                activeVehicles: 3,
                idleVehicles: 1,
                maintenanceVehicles: 1,
                averageUtilization: 37.3,
                totalDistanceCovered: 2450,
            };
        }
    },

    getRevenue: async (): Promise<RevenueMetrics> => {
        try {
            const response = await api.get('/api/v1/demo/fleet-stats');
            const data = response.data.data;
            return {
                todayRevenue: data.revenue_today,
                weekRevenue: data.revenue_week,
                monthRevenue: data.revenue_month,
                currency: 'INR',
            };
        } catch (error) {
            return {
                todayRevenue: 175000,
                weekRevenue: 1250000,
                monthRevenue: 4800000,
                currency: 'INR',
            };
        }
    },
};

// ==========================================
// DEMO API (for testing without database)
// ==========================================

export const demoApi = {
    getDashboard: async (): Promise<any> => {
        const response = await api.get('/api/v1/demo/dashboard');
        return response.data;
    },

    getVehicles: async (): Promise<any[]> => {
        const response = await api.get('/api/v1/demo/vehicles');
        return response.data.data;
    },

    getMissions: async (): Promise<any[]> => {
        const response = await api.get('/api/v1/demo/missions');
        return response.data.data;
    },

    getLoads: async (): Promise<any[]> => {
        const response = await api.get('/api/v1/demo/loads');
        return response.data.data;
    },

    getAiInsights: async (): Promise<any[]> => {
        const response = await api.get('/api/v1/demo/insights');
        return response.data.data;
    },

    getFleetStats: async (): Promise<any> => {
        const response = await api.get('/api/v1/demo/fleet-stats');
        return response.data.data;
    },

    // Demo Scenarios for video
    getBackhaulScenario: async (): Promise<any> => {
        const response = await api.get('/api/v1/demo/scenario/backhaul');
        return response.data;
    },

    getLtlPoolingScenario: async (): Promise<any> => {
        const response = await api.get('/api/v1/demo/scenario/ltl-pooling');
        return response.data;
    },

    getRouteOptimizationScenario: async (): Promise<any> => {
        const response = await api.get('/api/v1/demo/scenario/route-optimization');
        return response.data;
    },
};

// ==========================================
// EXPORT DEFAULT
// ==========================================

export default api;
