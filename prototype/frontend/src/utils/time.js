/**
 * Time utilities for formatting and calculating relative times
 */

/**
 * Parse a time string (HH:MM:SS) into minutes since midnight
 * @param {string} timeStr - Time in HH:MM:SS format
 * @returns {number} Minutes since midnight
 */
export function parseTimeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

/**
 * Get current time as minutes since midnight (in UTC to match server)
 * Note: Backend runs in UTC, so we need to compare in UTC
 * @returns {number} Minutes since midnight UTC
 */
export function getCurrentTimeMinutes() {
    const now = new Date();
    // Use UTC hours/minutes to match backend server time
    return now.getUTCHours() * 60 + now.getUTCMinutes();
}

/**
 * Calculate minutes until a scheduled arrival time
 * @param {string} arrivalTime - Time in HH:MM:SS format
 * @returns {number} Minutes until arrival (can be negative if passed)
 */
export function getMinutesUntil(arrivalTime) {
    const arrivalMinutes = parseTimeToMinutes(arrivalTime);
    const currentMinutes = getCurrentTimeMinutes();
    return arrivalMinutes - currentMinutes;
}

/**
 * Format minutes into a human-readable relative time
 * @param {number} minutes - Number of minutes
 * @returns {string} Formatted string like "2 min", "Arriving", "15 min"
 */
export function formatRelativeTime(minutes) {
    if (minutes < 0) {
        const absMins = Math.abs(Math.round(minutes));
        return `${absMins} min ago`;
    }
    if (minutes === 0) {
        return 'Just Arriving';
    }
    if (minutes < 1) {
        return '< 1 min';
    }
    if (minutes < 60) {
        return `In ${Math.round(minutes)} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    if (mins === 0) {
        return `${hours} hr`;
    }
    return `${hours} hr ${mins} min`;
}

/**
 * Format a time string for display (e.g., "09:15" from "09:15:00")
 * @param {string} timeStr - Time in HH:MM:SS format
 * @returns {string} Time in HH:MM format
 */
export function formatTime(timeStr) {
    if (!timeStr) return '';
    return timeStr.slice(0, 5);
}
