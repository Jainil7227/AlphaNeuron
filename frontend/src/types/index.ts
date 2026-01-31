/**
 * @file index.ts
 * @description Core TypeScript type definitions for the Neuro-Logistics application.
 * This file acts as the central source of truth for types shared across modules.
 */

// ==========================================
// GEOLOCATION & COORDINATES
// ==========================================

/**
 * Basic coordinate pair (latitude, longitude)
 */
export interface Coordinates {
    lat: number;
    lng: number;
}

/**
 * Enhanced geographic point with optional metadata
 */
export interface GeoPoint extends Coordinates {
    /** Altitude in meters */
    altitude?: number;
    /** Timestamp of the reading (ISO 8601 string) */
    timestamp?: string;
    /** Heading in degrees (0-360) */
    heading?: number;
    /** Speed in meters/second */
    speed?: number;
    /** Accuracy radius in meters */
    accuracy?: number;
}

// ==========================================
// VEHICLE / TRUCK TYPES
// ==========================================

export type VehicleStatus = 'IDLE' | 'IN_TRANSIT' | 'LOADING' | 'UNLOADING' | 'MAINTENANCE' | 'OFFLINE';

export interface VehicleCapacity {
    /** Maximum weight capacity in kg */
    maxWeight: number;
    /** Maximum volume capacity in cubic meters */
    maxVolume: number;
}

export interface DriverInfo {
    id: string;
    name: string;
    phone: string;
    rating?: number;
    licenseNumber?: string;
}

export interface Vehicle {
    id: string;
    /** License plate or registration number */
    registrationNumber: string;
    /** Current geographical position */
    currentLocation: GeoPoint;
    /** Current operational status */
    status: VehicleStatus;
    /** Vehicle capacity constraints */
    capacity: VehicleCapacity;
    /** Assigned driver details */
    driver?: DriverInfo;
    /** Current load utilization percentage (0-100) */
    currentLoadPercentage: number;
    /** Fuel level percentage (0-100) */
    fuelLevel?: number;
    /** Last update timestamp */
    lastUpdated: string;
}

// ==========================================
// ROUTE TYPES
// ==========================================

export type WaypointType = 'PICKUP' | 'DROPOFF' | 'CHECKPOINT' | 'FUEL_STOP' | 'REST_STOP';

export interface Waypoint {
    id: string;
    location: Coordinates;
    type: WaypointType;
    /** Address or descriptive name */
    name?: string;
    /** Scheduled arrival time (ISO 8601) */
    scheduledTime?: string;
    /** Actual arrival time (ISO 8601) */
    actualTime?: string;
    /** Estimated time of arrival (ISO 8601) */
    eta?: string;
    /** Order in the route sequence */
    sequenceOrder: number;
}

export interface RouteConstraint {
    /** Time ranges where entry is prohibited (e.g., ["22:00-06:00"]) */
    noEntryTimings?: string[];
    /** Restricted vehicle types */
    vehicleRestrictions?: string[];
    /** Estimated toll cost */
    tollCost?: number;
    /** Maximum height/weight allowed */
    maxHeight?: number;
    maxWeight?: number;
}

export interface Route {
    id: string;
    origin: Waypoint;
    destination: Waypoint;
    /** List of intermediate stops */
    waypoints: Waypoint[];
    /** Total distance in kilometers */
    totalDistance: number;
    /** Estimated duration in minutes */
    estimatedDuration: number;
    /** Encoded polyline string for map rendering */
    polyline: string;
    /** Route specific constraints */
    constraints?: RouteConstraint;
    /** Traffic status summary */
    trafficStatus?: 'CLEAR' | 'MODERATE' | 'HEAVY' | 'BLOCKED';
}

// ==========================================
// LOAD / SHIPMENT TYPES
// ==========================================

export type LoadStatus = 'PENDING' | 'ASSIGNED' | 'PICKED_UP' | 'DELIVERED' | 'CANCELLED';
export type LoadPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface TimeWindow {
    start: string; // ISO 8601
    end: string;   // ISO 8601
}

export interface Load {
    id: string;
    /** Weight in kg */
    weight: number;
    /** Volume in cubic meters */
    volume: number;
    /** Description of the cargo */
    description?: string;
    pickupLocation: Waypoint;
    dropoffLocation: Waypoint;
    pickupWindow?: TimeWindow;
    deliveryWindow?: TimeWindow;
    status: LoadStatus;
    priority: LoadPriority;
    /** Value of the goods */
    value?: number;
    /** Required equipment or handling (e.g., "REFRIGERATED") */
    requirements?: string[];
    /** Associated vehicle ID if assigned */
    assignedVehicleId?: string;
}

/**
 * Represents a partial capacity match for LTL (Less Than Truckload) pooling
 */
export interface LoadMatch {
    loadId: string;
    /** Match quality score (0-100) */
    score: number;
    /** Detour distance required to accommodate this load (km) */
    detourDistance: number;
    /** Additional time required (minutes) */
    detourTime: number;
    /** Projected revenue increase */
    estimatedRevenue: number;
}

// ==========================================
// DECISION ENGINE TYPES
// ==========================================

export type DeviationType = 'TRAFFIC' | 'WEATHER' | 'OPPORTUNITY' | 'EMERGENCY' | 'FUEL' | 'REST';

export interface Deviation {
    id: string;
    type: DeviationType;
    description: string;
    /** Generated timestamp */
    detectedAt: string;
    /** Impact score (0-100), higher is more severe/important */
    impactScore: number;
    /** Location where deviation is relevant */
    location?: Coordinates;
    /** Recommended action key */
    recommendedAction?: string;
}

export interface RerouteRecommendation {
    id: string;
    deviationId: string;
    /** The original route before modification */
    originalRouteId: string;
    /** The proposed new route */
    newRoute: Route;
    /** Difference in cost (negative means savings) */
    costDelta: number;
    /** Difference in time in minutes (negative means faster) */
    timeDelta: number;
    /** Difference in distance in km */
    distanceDelta: number;
    /** Human-readable reason for the recommendation */
    reason: string;
    /** Confidence score of the AI agent (0-1) */
    confidenceScore: number;
    /** Expiry time for this recommendation */
    expiresAt?: string;
}

// ==========================================
// FARE & PRICING TYPES
// ==========================================

export interface FareBreakdown {
    baseFare: number;
    distanceCharge: number;
    /** Multiplier factor (e.g., 1.0 = standard, 1.5 = high demand) */
    surgeFactor: number;
    tollCharges: number;
    fuelSurcharge: number;
    totalFare: number;
    currency: string;
}

// ==========================================
// RISK ASSESSMENT TYPES
// ==========================================

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface RiskAssessment {
    overallRisk: RiskLevel;
    factors: {
        weather: RiskLevel;
        traffic: RiskLevel;
        route: RiskLevel;
        timing: RiskLevel;
    };
    etaRange: {
        /** Optimistic ETA duration in minutes */
        optimistic: number;
        /** Expected ETA duration in minutes */
        expected: number;
        /** Pessimistic ETA duration in minutes */
        pessimistic: number;
    };
    warnings: string[];
}

// ==========================================
// WEBSOCKET EVENT TYPES
// ==========================================

export type WSEventType = 'POSITION_UPDATE' | 'LOAD_OPPORTUNITY' | 'REROUTE_ALERT' | 'STATUS_CHANGE' | 'DEVIATION_DETECTED';

export interface WSMessage<T> {
    type: WSEventType;
    payload: T;
    vehicleId?: string;
    timestamp: string;
}

// ==========================================
// API RESPONSE WRAPPER
// ==========================================

/**
 * Generic API Response wrapper
 */
export interface ApiResponse<T> {
    /** Success status */
    success: boolean;
    /** Response data payload */
    data: T;
    /** Error message if success is false */
    message?: string;
    /** Error code if applicable */
    errorCode?: string;
    /** Request timestamp */
    timestamp: string;
    /** Pagination metadata if applicable */
    meta?: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
    };
}
