// Use env var for API base URL, fallback to localhost for dev
const API_BASE = import.meta.env.VITE_API_URL
    ? `${import.meta.env.VITE_API_URL}/api`
    : 'http://localhost:8000/api';

/**
 * Fetch nearby stops based on coordinates
 * @param {number} lon - longitude
 * @param {number} lat - latitude  
 * @param {number} dist - search radius in meters (default 500)
 */
export async function getNearbyStops(lon, lat, dist = 500) {
    const url = `${API_BASE}/gtfs/stops/?point=${lon},${lat}&dist=${dist}`;
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Failed to fetch stops: ${res.status}`);
    }
    return res.json();
}

/**
 * Search stops by name or ID
 * @param {string} query - search query
 */
export async function searchStops(query) {
    const url = `${API_BASE}/gtfs/stops/?search=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Failed to search stops: ${res.status}`);
    }
    return res.json();
}

/**
 * Get upcoming trips at a stop
 * @param {string} stopId - stop ID
 * @param {string} time - optional time in HH:MM:SS format
 */
export async function getUpcomingTrips(stopId, time) {
    let url = `${API_BASE}/gtfs/stops/${stopId}/upcoming/`;
    if (time) {
        url += `?time=${time}`;
    }
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Failed to fetch upcoming trips: ${res.status}`);
    }
    return res.json();
}

/**
 * Get trip details including all stop times
 * @param {string} tripId - trip ID
 */
export async function getTripDetails(tripId) {
    const url = `${API_BASE}/gtfs/trips/${tripId}/`;
    const res = await fetch(url);
    if (!res.ok) {
        throw new Error(`Failed to fetch trip details: ${res.status}`);
    }
    return res.json();
}
