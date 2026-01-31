import { Coordinates, VehicleCapacity } from '../types';

// ==========================================
// DISTANCE CALCULATIONS
// ==========================================

/**
 * Calculate distance between two coordinates using Haversine formula
 * Returns distance in kilometers
 */
export const calculateDistance = (point1: Coordinates, point2: Coordinates): number => {
    const R = 6371; // Earth's radius in km
    const dLat = toRadians(point2.lat - point1.lat);
    const dLng = toRadians(point2.lng - point1.lng);

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRadians(point1.lat)) *
        Math.cos(toRadians(point2.lat)) *
        Math.sin(dLng / 2) *
        Math.sin(dLng / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
};

const toRadians = (degrees: number): number => {
    return degrees * (Math.PI / 180);
};

/**
 * Calculate bearing between two coordinates
 * Returns bearing in degrees (0-360)
 */
export const calculateBearing = (point1: Coordinates, point2: Coordinates): number => {
    const dLng = toRadians(point2.lng - point1.lng);
    const lat1 = toRadians(point1.lat);
    const lat2 = toRadians(point2.lat);

    const y = Math.sin(dLng) * Math.cos(lat2);
    const x =
        Math.cos(lat1) * Math.sin(lat2) -
        Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);

    const bearing = Math.atan2(y, x);
    return (bearing * 180 / Math.PI + 360) % 360;
};

// ==========================================
// CAPACITY CALCULATIONS
// ==========================================

export const calculateLoadPercentage = (
    currentWeight: number,
    currentVolume: number,
    capacity: VehicleCapacity
): number => {
    const weightPercentage = (currentWeight / capacity.maxWeight) * 100;
    const volumePercentage = (currentVolume / capacity.maxVolume) * 100;

    // Return the higher of the two (limiting factor)
    return Math.max(weightPercentage, volumePercentage);
};

export const canFitLoad = (
    currentWeight: number,
    currentVolume: number,
    loadWeight: number,
    loadVolume: number,
    capacity: VehicleCapacity
): boolean => {
    return (
        currentWeight + loadWeight <= capacity.maxWeight &&
        currentVolume + loadVolume <= capacity.maxVolume
    );
};

// ==========================================
// ETA CALCULATIONS
// ==========================================

/**
 * Calculate estimated time of arrival
 * @param distanceKm - Distance in kilometers
 * @param averageSpeedKmh - Average speed in km/h (default: 40)
 * @param bufferMinutes - Buffer time in minutes (default: 15)
 * @returns ETA in minutes
 */
export const calculateETA = (
    distanceKm: number,
    averageSpeedKmh: number = 40,
    bufferMinutes: number = 15
): number => {
    const travelTimeMinutes = (distanceKm / averageSpeedKmh) * 60;
    return Math.ceil(travelTimeMinutes + bufferMinutes);
};

/**
 * Calculate estimated delivery time based on multiple waypoints
 */
export const calculateTotalRouteTime = (
    coordinates: Coordinates[],
    averageSpeedKmh: number = 40,
    stopTimeMinutes: number = 10
): number => {
    if (coordinates.length < 2) return 0;

    let totalDistance = 0;
    for (let i = 0; i < coordinates.length - 1; i++) {
        totalDistance += calculateDistance(coordinates[i], coordinates[i + 1]);
    }

    const travelTime = calculateETA(totalDistance, averageSpeedKmh, 0);
    const stopTime = (coordinates.length - 1) * stopTimeMinutes;

    return travelTime + stopTime;
};

// ==========================================
// FARE CALCULATIONS
// ==========================================

export const calculateBaseFare = (distanceKm: number, ratePerKm: number = 15): number => {
    return distanceKm * ratePerKm;
};

export const calculateSurgeFare = (baseFare: number, surgeFactor: number): number => {
    return baseFare * surgeFactor;
};

export const calculateTotalFare = (
    distanceKm: number,
    ratePerKm: number = 15,
    surgeFactor: number = 1.0,
    tollCharges: number = 0,
    fuelSurcharge: number = 0
): number => {
    const baseFare = calculateBaseFare(distanceKm, ratePerKm);
    const surgeAdjusted = calculateSurgeFare(baseFare, surgeFactor);
    return surgeAdjusted + tollCharges + fuelSurcharge;
};

// ==========================================
// UTILITY CALCULATIONS
// ==========================================

/**
 * Calculate center point of multiple coordinates
 */
export const calculateCenter = (coordinates: Coordinates[]): Coordinates => {
    if (coordinates.length === 0) {
        return { lat: 0, lng: 0 };
    }

    const sum = coordinates.reduce(
        (acc, coord) => ({
            lat: acc.lat + coord.lat,
            lng: acc.lng + coord.lng,
        }),
        { lat: 0, lng: 0 }
    );

    return {
        lat: sum.lat / coordinates.length,
        lng: sum.lng / coordinates.length,
    };
};

/**
 * Calculate bounding box for coordinates
 */
export const calculateBounds = (
    coordinates: Coordinates[]
): { min: Coordinates; max: Coordinates } => {
    if (coordinates.length === 0) {
        return {
            min: { lat: 0, lng: 0 },
            max: { lat: 0, lng: 0 },
        };
    }

    const lats = coordinates.map(c => c.lat);
    const lngs = coordinates.map(c => c.lng);

    return {
        min: { lat: Math.min(...lats), lng: Math.min(...lngs) },
        max: { lat: Math.max(...lats), lng: Math.max(...lngs) },
    };
};
