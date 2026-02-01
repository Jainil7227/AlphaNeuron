import axios, { AxiosInstance } from 'axios';
import { API_BASE_URL, STORAGE_KEYS } from '../utils/constants';
import type {
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
// MOCK DATA GENERATORS
// ==========================================

const mockVehicles: Vehicle[] = [
    { id: 'v1', registrationNumber: 'MH02AB1234', type: 'TRUCK', capacity: { maxWeight: 5000, maxVolume: 30 }, currentLocation: { lat: 19.076, lng: 72.8777 }, status: 'IDLE', currentLoadPercentage: 0, lastUpdated: new Date().toISOString() },
    { id: 'v2', registrationNumber: 'MH04XY5678', type: 'MINI_TRUCK', capacity: { maxWeight: 2000, maxVolume: 12 }, currentLocation: { lat: 19.218, lng: 72.978 }, status: 'EN_ROUTE', currentLoadPercentage: 50, lastUpdated: new Date().toISOString() },
];

const mockLoads: Load[] = [
    {
        id: 'l1', customerId: 'c1', customerName: 'ABC Logistics', weight: 1500, volume: 10,
        origin: { lat: 19.076, lng: 72.8777, address: 'Mumbai Port' },
        destination: { lat: 18.5204, lng: 73.8567, address: 'Pune Warehouse' },
        status: 'PENDING', priority: 'HIGH', createdAt: new Date().toISOString(),
        pickupTimeWindow: { start: new Date().toISOString(), end: new Date(Date.now() + 86400000).toISOString() },
        deliveryTimeWindow: { start: new Date().toISOString(), end: new Date(Date.now() + 172800000).toISOString() }
    },
];

// ==========================================
// AXIOS INSTANCE (Mocked)
// ==========================================

const api: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 1000,
});

// ==========================================
// MOCK AGENT API
// ==========================================

export const agentApi = {
    calculateCost: async (data: any): Promise<any> => {
        // Return mock data for cost calculator
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    data: {
                        success: true,
                        agent_used: false,
                        calculation: {
                            origin: data.origin || 'Mumbai',
                            destination: data.destination || 'Delhi',
                            cargo: { type: data.cargo_type || 'General', weight_tons: data.weight_tons || 10 },
                            vehicle_type: data.vehicle_type || 'HCV',
                            route: {
                                distance_km: 1450,
                                duration_hours: 24,
                                highways: ['NH48', 'NH19'],
                                toll_plazas: 15,
                                border_crossings: 4
                            },
                            cost_breakdown: {
                                fuel: { liters_needed: 450, price_per_liter: 95, total: 42750 },
                                tolls: 8500,
                                driver: 3000,
                                misc: 1500,
                                total_operating_cost: 55750
                            },
                            fare_calculation: {
                                base_fare: 65000,
                                effort_multiplier: 1.2,
                                adjusted_fare: 78000,
                                fuel_surcharge: 4000,
                                toll_pass_through: 8500,
                                total_fare: 90500,
                                rate_per_km: 62.4
                            },
                            profit_analysis: {
                                gross_profit: 34750,
                                profit_margin_percent: 38.4
                            },
                            eta_range: {
                                optimistic: { hours: 22, arrival: 'Tomorrow 10:00 AM' },
                                expected: { hours: 24, arrival: 'Tomorrow 12:00 PM' },
                                pessimistic: { hours: 28, arrival: 'Tomorrow 04:00 PM' }
                            },
                            return_journey: data.include_return ? {
                                distance_km: 1450,
                                empty_return_cost: { total: 40000 },
                                potential_backhaul_earnings: 85000
                            } : null
                        },
                        ai_insights: [
                            "Route optimized for fuel efficiency using NH48.",
                            "High demand for return load from destination.",
                            "Weather conditions favorable for on-time delivery."
                        ],
                        ai_raw_analysis: {}
                    }
                });
            }, 800);
        });
    }
};



// ==========================================
// MOCK AUTH API
// ==========================================

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
        // MOCK LOGIN CHECK
        if (credentials.email === 'admin@neurologistics.com' && credentials.password === 'admin123') {
            return {
                user: {
                    id: 'mock-admin',
                    name: 'Admin User',
                    email: credentials.email,
                    phone: '+919999999999',
                    role: 'ADMIN',
                    createdAt: new Date().toISOString(),
                },
                token: 'mock-jwt-token-12345',
            };
        }
        throw new Error("Invalid credentials");
    },

    logout: async (): Promise<void> => {
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
        localStorage.removeItem(STORAGE_KEYS.USER);
    },

    getMe: async (): Promise<any> => {
        return {
            id: 'mock-admin',
            name: 'Admin User',
            email: 'admin@neurologistics.com',
            role: 'ADMIN',
        };
    },
};

// ==========================================
// MOCK APIs
// ==========================================

export const vehicleApi = {
    getAll: async (): Promise<Vehicle[]> => mockVehicles,
    getById: async (id: string): Promise<Vehicle> => mockVehicles.find(v => v.id === id) || mockVehicles[0],
    updateLocation: async () => { },
    updateStatus: async () => { },
};

export const loadApi = {
    getAll: async (): Promise<PaginatedResponse<Load>> => ({ data: mockLoads, total: mockLoads.length, page: 1, pageSize: 20, totalPages: 1 }),
    getById: async (id: string): Promise<Load> => mockLoads.find(l => l.id === id)!,
    create: async (load: Partial<Load>): Promise<Load> => ({ ...load, id: 'new-load' } as Load),
    assign: async () => mockLoads[0],
};

export const routeApi = {
    getAll: async (): Promise<Route[]> => [],
    getById: async (id: string): Promise<Route> => ({} as Route),
    optimize: async (): Promise<Route> => ({} as Route),
};

export const analyticsApi = {
    getFleetMetrics: async (): Promise<FleetMetrics> => ({
        totalVehicles: 5, activeVehicles: 2, idleVehicles: 2, maintenanceVehicles: 1, averageUtilization: 65, totalDistanceCovered: 1200
    }),
    getRevenue: async (): Promise<RevenueMetrics> => ({
        todayRevenue: 25000, weekRevenue: 150000, monthRevenue: 600000, currency: 'INR'
    }),
};

export const demoApi = {
    getDashboard: async (): Promise<any> => ({ stats: {}, recentActivity: [] }),
    getVehicles: async (): Promise<any[]> => mockVehicles,
    getMissions: async (): Promise<any[]> => [],
    getLoads: async (): Promise<any[]> => mockLoads,
    getAiInsights: async (): Promise<any[]> => [],
    getFleetStats: async (): Promise<any> => ({}),
    getBackhaulScenario: async (): Promise<any> => ({}),
    getLtlPoolingScenario: async (): Promise<any> => ({}),
    getRouteOptimizationScenario: async (): Promise<any> => ({}),
};

export default api;

