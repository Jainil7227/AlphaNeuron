// ==========================================
// EMAIL & PASSWORD VALIDATORS
// ==========================================

export const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    return passwordRegex.test(password);
};

export const getPasswordStrength = (password: string): 'weak' | 'medium' | 'strong' => {
    if (password.length < 6) return 'weak';

    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;

    if (strength <= 2) return 'weak';
    if (strength <= 3) return 'medium';
    return 'strong';
};

// ==========================================
// PHONE NUMBER VALIDATORS
// ==========================================

export const isValidIndianPhone = (phone: string): boolean => {
    // Accepts: 10 digits, or +91 followed by 10 digits
    const phoneRegex = /^(\+91)?[6-9]\d{9}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
};

// ==========================================
// VEHICLE VALIDATORS
// ==========================================

export const isValidRegistrationNumber = (regNo: string): boolean => {
    // Indian vehicle registration format: XX00XX0000
    // Example: MH12AB1234
    const regNoRegex = /^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$/;
    return regNoRegex.test(regNo.replace(/\s/g, ''));
};

// ==========================================
// COORDINATE VALIDATORS
// ==========================================

export const isValidLatitude = (lat: number): boolean => {
    return lat >= -90 && lat <= 90;
};

export const isValidLongitude = (lng: number): boolean => {
    return lng >= -180 && lng <= 180;
};

export const isValidCoordinates = (lat: number, lng: number): boolean => {
    return isValidLatitude(lat) && isValidLongitude(lng);
};

// ==========================================
// FORM VALIDATORS
// ==========================================

export const isNotEmpty = (value: string): boolean => {
    return value.trim().length > 0;
};

export const isMinLength = (value: string, minLength: number): boolean => {
    return value.length >= minLength;
};

export const isMaxLength = (value: string, maxLength: number): boolean => {
    return value.length <= maxLength;
};

export const isNumeric = (value: string): boolean => {
    return /^\d+$/.test(value);
};

export const isPositiveNumber = (value: number): boolean => {
    return !isNaN(value) && value > 0;
};

// ==========================================
// DATE VALIDATORS
// ==========================================

export const isValidDate = (dateString: string): boolean => {
    const date = new Date(dateString);
    return !isNaN(date.getTime());
};

export const isFutureDate = (dateString: string): boolean => {
    const date = new Date(dateString);
    return date.getTime() > Date.now();
};

export const isPastDate = (dateString: string): boolean => {
    const date = new Date(dateString);
    return date.getTime() < Date.now();
};

// ==========================================
// FILE VALIDATORS
// ==========================================

export const isValidFileSize = (file: File, maxSizeMB: number): boolean => {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
};

export const isValidFileType = (file: File, allowedTypes: string[]): boolean => {
    return allowedTypes.includes(file.type);
};

// ==========================================
// PINCODE VALIDATOR
// ==========================================

export const isValidIndianPincode = (pincode: string): boolean => {
    const pincodeRegex = /^[1-9][0-9]{5}$/;
    return pincodeRegex.test(pincode);
};
