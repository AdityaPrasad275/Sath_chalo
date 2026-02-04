/**
 * Time utilities for formatting and calculating relative times
 */

// ============================================================================
// WORKAROUND: Backend returns times in UTC, but we need IST (UTC+5:30)
// TODO: Remove these functions once backend is fixed to use Indian timezone
// ============================================================================

const IST_OFFSET_HOURS = 5;
const IST_OFFSET_MINUTES = 30;
const IST_OFFSET_TOTAL_MINUTES = IST_OFFSET_HOURS * 60 + IST_OFFSET_MINUTES;

/**
 * Convert UTC time string to IST time string
 * @param {string} utcTimeStr - Time in HH:MM:SS format (UTC)
 * @returns {string} Time in HH:MM:SS format (IST)
 */
export function convertUtcToIst(utcTimeStr) {
    if (!utcTimeStr) return utcTimeStr;

    const [hours, minutes, seconds] = utcTimeStr.split(':').map(Number);

    // Convert to minutes since midnight
    let totalMinutes = hours * 60 + minutes + IST_OFFSET_TOTAL_MINUTES;

    // Handle day overflow (if time goes past midnight)
    if (totalMinutes >= 24 * 60) {
        totalMinutes -= 24 * 60;
    }

    // Convert back to HH:MM:SS
    const istHours = Math.floor(totalMinutes / 60);
    const istMinutes = totalMinutes % 60;

    return `${String(istHours).padStart(2, '0')}:${String(istMinutes).padStart(2, '0')}:${String(seconds || 0).padStart(2, '0')}`;
}

/**
 * Get current time in IST as HH:MM:SS
 * @returns {string} Current time in IST
 */
export function getCurrentIstTime() {
    const now = new Date();

    // Get UTC time
    const utcHours = now.getUTCHours();
    const utcMinutes = now.getUTCMinutes();
    const utcSeconds = now.getUTCSeconds();

    // Add IST offset
    let totalMinutes = utcHours * 60 + utcMinutes + IST_OFFSET_TOTAL_MINUTES;

    if (totalMinutes >= 24 * 60) {
        totalMinutes -= 24 * 60;
    }

    const istHours = Math.floor(totalMinutes / 60);
    const istMinutes = totalMinutes % 60;

    return `${String(istHours).padStart(2, '0')}:${String(istMinutes).padStart(2, '0')}:${String(utcSeconds).padStart(2, '0')}`;
}

// ============================================================================
// End of workaround
// ============================================================================

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
 * Get current time as minutes since midnight (in IST)
 * @returns {number} Minutes since midnight IST
 */
export function getCurrentTimeMinutes() {
    const currentIstTime = getCurrentIstTime();
    return parseTimeToMinutes(currentIstTime);
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
        return `in ${Math.round(minutes)} min`;
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
