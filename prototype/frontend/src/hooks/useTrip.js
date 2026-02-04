import { useState, useEffect } from 'react';
import { getTripDetails } from '../utils/api';
import { convertUtcToIst, getCurrentIstTime } from '../utils/time';

/**
 * Hook to fetch trip details including all stop times
 * @param {string} tripId - Trip ID to fetch
 * @returns {Object} { trip, stopTimes, currentStopIndex, isLoading, error, refetch }
 */
export function useTrip(tripId) {
    const [trip, setTrip] = useState(null);
    const [stopTimes, setStopTimes] = useState([]);
    const [currentStopIndex, setCurrentStopIndex] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchTrip = async () => {
        if (!tripId) {
            setError('No trip ID provided');
            setIsLoading(false);
            return;
        }

        try {
            setIsLoading(true);
            setError(null);

            const data = await getTripDetails(tripId);
            setTrip(data);

            // WORKAROUND: Convert UTC times from backend to IST
            const stopTimesInIst = (data.stop_times || []).map(st => ({
                ...st,
                arrival_time: convertUtcToIst(st.arrival_time),
                departure_time: convertUtcToIst(st.departure_time)
            }));

            setStopTimes(stopTimesInIst);

            // Calculate current bus position based on schedule (in IST)
            const currentTime = getCurrentIstTime();

            // Find the current stop: last stop with arrival_time <= now
            let currentIndex = null;
            for (let i = 0; i < stopTimesInIst.length; i++) {
                if (stopTimesInIst[i].arrival_time <= currentTime) {
                    currentIndex = i;
                } else {
                    break;
                }
            }

            setCurrentStopIndex(currentIndex);
        } catch (err) {
            setError(err.message || 'Failed to load trip details');
            console.error('Error fetching trip:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTrip();
    }, [tripId]);

    return {
        trip,
        stopTimes,
        currentStopIndex,
        isLoading,
        error,
        refetch: fetchTrip,
    };
}
