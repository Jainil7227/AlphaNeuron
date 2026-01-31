import { format, formatDistanceToNow } from 'date-fns';
import { TIME_FORMATS } from './constants';

// ==========================================
// DATE/TIME FORMATTERS
// ==========================================

export const formatDate = (date: string | Date): string => {
    return format(new Date(date), TIME_FORMATS.DISPLAY_DATE);
};

export const formatTime = (date: string | Date): string => {
    return format(new Date(date), TIME_FORMATS.DISPLAY_TIME);
};

export const formatDateTime = (date: string | Date): string => {
    return format(new Date(date), TIME_FORMATS.DISPLAY_DATETIME);
};

export const formatRelativeTime = (date: string | Date): string => {
    return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;

    if (hours === 0) return `${mins}m`;
    if (mins === 0) return `${hours}h`;
    return `${hours}h ${mins}m`;
};

// ==========================================
// NUMBER FORMATTERS
// ==========================================

export const formatCurrency = (amount: number, currency: string = 'INR'): string => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
};

export const formatWeight = (kg: number): string => {
    if (kg >= 1000) {
        return `${(kg / 1000).toFixed(1)} tons`;
    }
    return `${kg.toFixed(0)} kg`;
};

export const formatDistance = (km: number): string => {
    if (km < 1) {
        return `${(km * 1000).toFixed(0)} m`;
    }
    return `${km.toFixed(1)} km`;
};

export const formatPercentage = (value: number, decimals: number = 0): string => {
    return `${value.toFixed(decimals)}%`;
};

export const formatSpeed = (kmph: number): string => {
    return `${kmph.toFixed(0)} km/h`;
};

// ==========================================
// TEXT FORMATTERS
// ==========================================

export const truncateText = (text: string, maxLength: number): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

export const capitalizeFirstLetter = (text: string): string => {
    return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

export const formatEnumValue = (value: string): string => {
    return value
        .split('_')
        .map(word => capitalizeFirstLetter(word))
        .join(' ');
};

// ==========================================
// VEHICLE/REGISTRATION FORMATTERS
// ==========================================

export const formatRegistrationNumber = (regNo: string): string => {
    // Format: MH12AB1234 -> MH 12 AB 1234
    const clean = regNo.replace(/[^A-Z0-9]/gi, '').toUpperCase();

    if (clean.length >= 10) {
        return `${clean.slice(0, 2)} ${clean.slice(2, 4)} ${clean.slice(4, -4)} ${clean.slice(-4)}`;
    }
    return clean;
};

export const formatPhoneNumber = (phone: string): string => {
    // Format: +91XXXXXXXXXX -> +91 XXXXX XXXXX
    const clean = phone.replace(/\D/g, '');

    if (clean.startsWith('91') && clean.length === 12) {
        return `+91 ${clean.slice(2, 7)} ${clean.slice(7)}`;
    }
    if (clean.length === 10) {
        return `+91 ${clean.slice(0, 5)} ${clean.slice(5)}`;
    }
    return phone;
};

// ==========================================
// COORDINATE FORMATTERS
// ==========================================

export const formatCoordinates = (lat: number, lng: number): string => {
    return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
};
