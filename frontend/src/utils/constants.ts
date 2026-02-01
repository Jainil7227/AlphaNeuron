import { VehicleStatus } from '../types';

// ==========================================
// API CONFIGURATION
// ==========================================

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export const API_ENDPOINTS = {
    AUTH: {
        LOGIN: '/api/auth/login',
        LOGOUT: '/api/auth/logout',
        REGISTER: '/api/auth/register',
        REFRESH: '/api/auth/refresh',
        ME: '/api/auth/me',
    },
    VEHICLES: {
        LIST: '/api/vehicles',
        DETAIL: (id: string) => `/api/vehicles/${id}`,
        LOCATION: (id: string) => `/api/vehicles/${id}/location`,
        STATUS: (id: string) => `/api/vehicles/${id}/status`,
    },
    LOADS: {
        LIST: '/api/loads',
        DETAIL: (id: string) => `/api/loads/${id}`,
        CREATE: '/api/loads',
        ASSIGN: (id: string) => `/api/loads/${id}/assign`,
    },
    ROUTES: {
        LIST: '/api/routes',
        DETAIL: (id: string) => `/api/routes/${id}`,
        OPTIMIZE: '/api/routes/optimize',
    },
    ANALYTICS: {
        FLEET_METRICS: '/api/analytics/fleet-metrics',
        REVENUE: '/api/analytics/revenue',
    },
};

// ==========================================
// WEBSOCKET EVENTS
// ==========================================

export const WS_EVENTS = {
    CONNECT: 'connect',
    DISCONNECT: 'disconnect',
    VEHICLE_LOCATION_UPDATE: 'vehicle:location:update',
    ROUTE_DEVIATION: 'route:deviation',
    LOAD_STATUS_CHANGE: 'load:status:change',
    NOTIFICATION: 'notification',
};

// ==========================================
// STATUS COLORS
// ==========================================

export const STATUS_COLORS = {
    VEHICLE: {
        IDLE: '#10b981',       // green-500
        EN_ROUTE: '#3b82f6',   // blue-500
        LOADING: '#f59e0b',    // amber-500
        UNLOADING: '#8b5cf6',  // violet-500
        MAINTENANCE: '#ef4444', // red-500
        OFFLINE: '#6b7280',    // gray-500
    } as Record<VehicleStatus, string>,
    LOAD: {
        PENDING: '#f59e0b',    // amber-500
        ASSIGNED: '#3b82f6',   // blue-500
        IN_TRANSIT: '#8b5cf6', // violet-500
        DELIVERED: '#10b981',  // green-500
        CANCELLED: '#ef4444',  // red-500
    },
    TRAFFIC: {
        CLEAR: '#10b981',      // green-500
        MODERATE: '#f59e0b',   // amber-500
        HEAVY: '#ef4444',      // red-500
        BLOCKED: '#991b1b',    // red-900
    },
};

// ==========================================
// MAP CONFIGURATION
// ==========================================

export const MAP_CONFIG = {
    DEFAULT_CENTER: { lat: 19.076, lng: 72.8777 }, // Mumbai
    DEFAULT_ZOOM: 12,
    TILE_LAYER_URL: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    TILE_LAYER_ATTRIBUTION: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
};

// ==========================================
// VEHICLE TYPES
// ==========================================

export const VEHICLE_TYPE_CONFIG = {
    TRUCK: {
        label: 'Truck',
        icon: '🚚',
        baseCapacity: { maxWeight: 5000, maxVolume: 30 },
    },
    MINI_TRUCK: {
        label: 'Mini Truck',
        icon: '🚐',
        baseCapacity: { maxWeight: 2000, maxVolume: 12 },
    },
    TEMPO: {
        label: 'Tempo',
        icon: '🚙',
        baseCapacity: { maxWeight: 1000, maxVolume: 8 },
    },
    CONTAINER: {
        label: 'Container',
        icon: '🚛',
        baseCapacity: { maxWeight: 20000, maxVolume: 60 },
    },
};

// ==========================================
// LOCAL STORAGE KEYS
// ==========================================

export const STORAGE_KEYS = {
    AUTH_TOKEN: 'neuro_logistics_token',
    USER: 'neuro_logistics_user',
    THEME: 'neuro_logistics_theme',
};

// ==========================================
// PAGINATION
// ==========================================

export const PAGINATION = {
    DEFAULT_PAGE: 1,
    DEFAULT_PAGE_SIZE: 20,
    PAGE_SIZE_OPTIONS: [10, 20, 50, 100],
};

// ==========================================
// TIME FORMATS
// ==========================================

export const TIME_FORMATS = {
    DISPLAY_DATE: 'MMM dd, yyyy',
    DISPLAY_TIME: 'hh:mm a',
    DISPLAY_DATETIME: 'MMM dd, yyyy hh:mm a',
    API_DATETIME: "yyyy-MM-dd'T'HH:mm:ss",
};
