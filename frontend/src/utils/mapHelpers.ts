import { LatLngBounds, LatLngExpression } from 'leaflet';
import { Coordinates } from '../types';

// ==========================================
// COORDINATE CONVERSION
// ==========================================

export const coordsToLatLng = (coords: Coordinates): LatLngExpression => {
    return [coords.lat, coords.lng];
};

export const latLngToCoords = (lat: number, lng: number): Coordinates => {
    return { lat, lng };
};

// ==========================================
// BOUNDS HELPERS
// ==========================================

export const createBoundsFromCoordinates = (coordinates: Coordinates[]): LatLngBounds | null => {
    if (coordinates.length === 0) return null;

    const latLngs = coordinates.map(coordsToLatLng);
    return new LatLngBounds(latLngs as any); // Cast because LatLngExpression array check might be strict
};

export const padBounds = (bounds: LatLngBounds, paddingPercent: number = 10): LatLngBounds => {
    const sw = bounds.getSouthWest();
    const ne = bounds.getNorthEast();

    const latDiff = ne.lat - sw.lat;
    const lngDiff = ne.lng - sw.lng;

    const latPadding = (latDiff * paddingPercent) / 100;
    const lngPadding = (lngDiff * paddingPercent) / 100;

    return new LatLngBounds(
        [sw.lat - latPadding, sw.lng - lngPadding],
        [ne.lat + latPadding, ne.lng + lngPadding]
    );
};

// ==========================================
// POLYLINE HELPERS
// ==========================================

/**
 * Decode an encoded polyline string into coordinates
 * (Google Polyline encoding algorithm)
 */
export const decodePolyline = (encoded: string): Coordinates[] => {
    const coordinates: Coordinates[] = [];
    let index = 0;
    let lat = 0;
    let lng = 0;

    while (index < encoded.length) {
        let b;
        let shift = 0;
        let result = 0;

        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);

        const dlat = result & 1 ? ~(result >> 1) : result >> 1;
        lat += dlat;

        shift = 0;
        result = 0;

        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);

        const dlng = result & 1 ? ~(result >> 1) : result >> 1;
        lng += dlng;

        coordinates.push({
            lat: lat / 1e5,
            lng: lng / 1e5,
        });
    }

    return coordinates;
};

/**
 * Encode coordinates into a polyline string
 */
export const encodePolyline = (coordinates: Coordinates[]): string => {
    let encoded = '';
    let prevLat = 0;
    let prevLng = 0;

    for (const coord of coordinates) {
        const lat = Math.round(coord.lat * 1e5);
        const lng = Math.round(coord.lng * 1e5);

        encoded += encodeValue(lat - prevLat);
        encoded += encodeValue(lng - prevLng);

        prevLat = lat;
        prevLng = lng;
    }

    return encoded;
};

const encodeValue = (value: number): string => {
    let encoded = '';
    let num = value < 0 ? ~(value << 1) : value << 1;

    while (num >= 0x20) {
        encoded += String.fromCharCode((0x20 | (num & 0x1f)) + 63);
        num >>= 5;
    }

    encoded += String.fromCharCode(num + 63);
    return encoded;
};

// ==========================================
// MAP UTILITIES
// ==========================================

export const getZoomLevelForDistance = (distanceKm: number): number => {
    if (distanceKm < 1) return 15;
    if (distanceKm < 5) return 13;
    if (distanceKm < 10) return 12;
    if (distanceKm < 50) return 10;
    if (distanceKm < 100) return 9;
    if (distanceKm < 500) return 7;
    return 5;
};

export const shouldClusterMarkers = (markerCount: number): boolean => {
    return markerCount > 20;
};
