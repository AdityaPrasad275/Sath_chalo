import { useState, useEffect } from 'react';
import { getUpcomingTrips } from '../utils/api';
import { convertUtcToIst } from '../utils/time';

/**
 * Hook to fetch upcoming trips/buses for a specific stop
 * @param {string} stopId - The stop ID to fetch trips for
 */
export function useUpcomingTrips(stopId) {
    const [trips, setTrips] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!stopId) {
            setIsLoading(false);
            return;
        }

        let cancelled = false;
        setIsLoading(true);
        setError(null);

        async function fetchTrips() {
            try {
                const data = await getUpcomingTrips(stopId);
                // Extract results from paginated response
                const results = data.results || data;

                // WORKAROUND: Convert UTC times from backend to IST
                const tripsInIst = results.map(trip => ({
                    ...trip,
                    arrival_time: convertUtcToIst(trip.arrival_time),
                    departure_time: convertUtcToIst(trip.departure_time)
                }));

                if (!cancelled) {
                    setTrips(tripsInIst);
                    setIsLoading(false);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err.message || 'Failed to fetch upcoming trips');
                    setIsLoading(false);
                }
            }
        }

        fetchTrips();

        return () => {
            cancelled = true;
        };
    }, [stopId]);

    // Function to manually refetch
    const refetch = async () => {
        if (!stopId) return;
        setIsLoading(true);
        setError(null);
        try {
            const data = await getUpcomingTrips(stopId);
            const results = data.results || data;

            // WORKAROUND: Convert UTC times from backend to IST
            const tripsInIst = results.map(trip => ({
                ...trip,
                arrival_time: convertUtcToIst(trip.arrival_time),
                departure_time: convertUtcToIst(trip.departure_time)
            }));

            setTrips(tripsInIst);
        } catch (err) {
            setError(err.message || 'Failed to fetch upcoming trips');
        } finally {
            setIsLoading(false);
        }
    };

    return { trips, isLoading, error, refetch };
}
