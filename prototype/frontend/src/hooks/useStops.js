import { useState, useEffect } from 'react';
import { getNearbyStops, searchStops } from '../utils/api';
import { getDistance } from '../utils/geo';

/**
 * Hook to manage stops data, searching, and proximity fetching
 * 
 * @param {Object} position - User position { lat, lon }
 * @param {string} searchQuery - Current search string
 */
export function useStops(position, searchQuery) {
    const [stops, setStops] = useState([]);
    const [isSearching, setIsSearching] = useState(false);
    const [isLoadingStops, setIsLoadingStops] = useState(false);
    const [fetchError, setFetchError] = useState(null);

    // Helper to process API response (GeoJSON FeatureCollection)
    const processStops = (data, pos) => {
        const features = data.results?.features || data.features || data.results || data || [];
        const results = features.map(stop => {
            const properties = stop.properties || stop;
            const stopLat = stop.geometry?.coordinates?.[1] || properties.lat || properties.latitude;
            const stopLon = stop.geometry?.coordinates?.[0] || properties.lon || properties.longitude;

            let distance = null;
            if (pos) {
                distance = getDistance(pos.lat, pos.lon, stopLat, stopLon);
            }

            return {
                ...properties,
                id: properties.stop_id || properties.id,
                lat: stopLat,
                lon: stopLon,
                distance
            };
        });

        if (pos) {
            results.sort((a, b) => a.distance - b.distance);
        }
        return results;
    };

    // 1. Fetch nearby stops when position is available (initial load)
    useEffect(() => {
        if (!position || searchQuery.trim()) return;

        async function fetchNearby() {
            setIsLoadingStops(true);
            setFetchError(null);
            try {
                const data = await getNearbyStops(position.lon, position.lat, 1000);
                setStops(processStops(data, position));
            } catch (err) {
                setFetchError(err.message);
            } finally {
                setIsLoadingStops(false);
            }
        }

        fetchNearby();
    }, [position, searchQuery]);

    // 2. Handle search with debouncing
    useEffect(() => {
        if (!searchQuery.trim()) {
            // If search cleared, the effect above will handle nearby stops
            // But we might need to trigger it if position exists
            return;
        }

        const debounce = setTimeout(async () => {
            setIsSearching(true);
            setFetchError(null);
            try {
                const data = await searchStops(searchQuery);
                setStops(processStops(data, position));
            } catch (err) {
                setFetchError(err.message);
            } finally {
                setIsSearching(false);
            }
        }, 300);

        return () => clearTimeout(debounce);
    }, [searchQuery, position]);

    return {
        stops,
        isSearching,
        isLoadingStops,
        fetchError
    };
}
