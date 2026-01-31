// ==========================================
// USER & AUTHENTICATION
// ==========================================

export type UserRole = 'ADMIN' | 'FLEET_MANAGER' | 'DRIVER';

export interface User {
    id: string;
    name: string;
    email: string;
    phone: string;
    role: UserRole;
    avatar?: string;
    createdAt: string;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
}

export interface LoginCredentials {
    email: string;
    password: string;
}

export interface LoginResponse {
    user: User;
    token: string;
}

// ==========================================
// COORDINATES & LOCATION
// ==========================================

export interface Coordinates {
    lat: number;
    lng: number;
}

export interface Location extends Coordinates {
    address?: string;
    city?: string;
    state?: string;
    pincode?: string;
}

// ==========================================
// VEHICLE
// ==========================================

export type VehicleStatus = 'IDLE' | 'EN_ROUTE' | 'LOADING' | 'UNLOADING' | 'MAINTENANCE' | 'OFFLINE';
export type VehicleType = 'TRUCK' | 'MINI_TRUCK' | 'TEMPO' | 'CONTAINER';

export interface VehicleCapacity {
    maxWeight: number; // in kg
    maxVolume: number; // in cubic meters
}

export interface Vehicle {
    id: string;
    registrationNumber: string;
    type: VehicleType;
    capacity: VehicleCapacity;
    currentLocation: Coordinates;
    status: VehicleStatus;
    currentLoadPercentage: number; // 0-100
    driverId?: string;
    driverName?: string;
    lastUpdated: string;
}

// ==========================================
// LOAD & SHIPMENT
// ==========================================

export type LoadStatus = 'PENDING' | 'ASSIGNED' | 'IN_TRANSIT' | 'DELIVERED' | 'CANCELLED';
export type LoadPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface Load {
    id: string;
    customerId: string;
    customerName: string;
    weight: number; // kg
    volume: number; // cubic meters
    origin: Location;
    destination: Location;
    status: LoadStatus;
    priority: LoadPriority;
    pickupTimeWindow: TimeWindow;
    deliveryTimeWindow: TimeWindow;
    assignedVehicleId?: string;
    createdAt: string;
    estimatedDelivery?: string;
}

export interface TimeWindow {
    start: string; // ISO datetime
    end: string;   // ISO datetime
}

// ==========================================
// ROUTE & WAYPOINT
// ==========================================

export type WaypointType = 'PICKUP' | 'DROPOFF' | 'CHECKPOINT' | 'FUEL_STOP' | 'REST_STOP';

export interface Waypoint {
    id: string;
    type: WaypointType;
    location: Coordinates;
    address?: string;
    scheduledTime?: string;
    actualTime?: string;
    completed: boolean;
    loadId?: string;
}

export interface Route {
    id: string;
    vehicleId: string;
    waypoints: Waypoint[];
    totalDistance: number; // km
    estimatedDuration: number; // minutes
    status: 'PLANNED' | 'ACTIVE' | 'COMPLETED' | 'CANCELLED';
    createdAt: string;
    polyline?: string; // Encoded polyline
}

// ==========================================
// ANALYTICS & METRICS
// ==========================================

export interface FleetMetrics {
    totalVehicles: number;
    activeVehicles: number;
    idleVehicles: number;
    maintenanceVehicles: number;
    averageUtilization: number; // percentage
    totalDistanceCovered: number; // km today
}

export interface RevenueMetrics {
    todayRevenue: number;
    weekRevenue: number;
    monthRevenue: number;
    currency: string;
}

// ==========================================
// NOTIFICATIONS
// ==========================================

export type NotificationType = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';

export interface Notification {
    id: string;
    type: NotificationType;
    title: string;
    message: string;
    timestamp: string;
    read: boolean;
    actionUrl?: string;
}

// ==========================================
// WEBSOCKET EVENTS
// ==========================================

export interface VehicleLocationUpdate {
    vehicleId: string;
    location: Coordinates;
    speed: number; // km/h
    heading: number; // degrees
    timestamp: string;
}

export interface RouteDeviationAlert {
    vehicleId: string;
    routeId: string;
    deviationDistance: number; // meters
    currentLocation: Coordinates;
    timestamp: string;
}

// ==========================================
// API RESPONSE
// ==========================================

export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
}

export interface PaginatedResponse<T> {
    data: T[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
}

// ==========================================
//FARE & PRICING
// ==========================================

export interface FareBreakdown {
    baseFare: number;
    distanceCharge: number;
    surgeFactor: number;
    tollCharges: number;
    fuelSurcharge: number;
    totalFare: number;
    currency: string;
}

// ==========================================
// RISK & OPTIMIZATION
// ==========================================

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RiskAssessment {
    level: RiskLevel;
    factors: string[];
    score: number; // 0-100
}
