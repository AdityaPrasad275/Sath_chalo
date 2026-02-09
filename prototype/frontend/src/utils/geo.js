/**
 * Haversine distance calculation
 * Returns distance in meters between two lat/lon points
 */
export function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371000; // Earth's radius in meters
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

function toRad(deg) {
    return deg * (Math.PI / 180);
}

/**
 * Format distance for display
 * @param {number} meters - distance in meters
 * @returns {string} - formatted string like "50m" or "1.2km"
 */
export function formatDistance(meters) {
    if (meters < 1000) {
        return `${Math.round(meters)}m`;
    }
    return `${(meters / 1000).toFixed(1)}km`;
}

/**
 * Format distance with smart rounding for better UX
 * Since we're using Haversine (as-the-crow-flies) distance, 
 * exact values don't make sense. Round to sensible increments.
 * @param {number} meters - distance in meters
 * @returns {string} - formatted string like "50m" or "1.2km"
 */
export function formatRoundedDistance(meters) {
    if (meters < 50) {
        // Under 50m: round to nearest 10m
        return `${Math.round(meters / 10) * 10}m`;
    } else if (meters < 100) {
        // 50-100m: round to nearest 25m
        return `${Math.round(meters / 25) * 25}m`;
    } else if (meters < 500) {
        // 100-500m: round to nearest 50m
        return `${Math.round(meters / 50) * 50}m`;
    } else if (meters < 1000) {
        // 500m-1km: round to nearest 100m
        return `${Math.round(meters / 100) * 100}m`;
    } else {
        // Over 1km: show with 1 decimal place
        return `${(meters / 1000).toFixed(1)}km`;
    }
}
