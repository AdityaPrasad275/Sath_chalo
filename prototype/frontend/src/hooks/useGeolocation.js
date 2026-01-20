import { useState, useEffect, useCallback } from 'react';

// Dev location mock - set to GTFS generator center (Bangalore)
// Toggle via URL param: ?mock_location=true
const DEV_MOCK_LOCATION = {
    lat: 12.9716,
    lon: 77.5946,
};

function shouldMockLocation() {
    if (typeof window === 'undefined') return false;
    const params = new URLSearchParams(window.location.search);
    return params.get('mock_location') === 'true' || params.get('mock') === 'true';
}

/**
 * Hook for handling geolocation with permission detection
 * 
 * Returns:
 * - position: { lat, lon } or null
 * - error: string or null
 * - permissionState: 'granted' | 'denied' | 'prompt' | 'unknown'
 * - isLoading: boolean
 * - requestLocation: function to trigger location request
 * - isMocked: boolean - true if using mock location
 */
export function useGeolocation() {
    const [position, setPosition] = useState(null);
    const [error, setError] = useState(null);
    const [permissionState, setPermissionState] = useState('unknown');
    const [isLoading, setIsLoading] = useState(true);
    const [isMocked, setIsMocked] = useState(false);

    // Check current permission status on mount
    useEffect(() => {
        // Check for mock location mode
        if (shouldMockLocation()) {
            console.log('🧪 Using mock location:', DEV_MOCK_LOCATION);
            setPosition(DEV_MOCK_LOCATION);
            setPermissionState('granted');
            setIsMocked(true);
            setIsLoading(false);
            return;
        }

        async function checkPermission() {
            if (!navigator.permissions) {
                setPermissionState('unknown');
                setIsLoading(false);
                return;
            }

            try {
                const result = await navigator.permissions.query({ name: 'geolocation' });
                setPermissionState(result.state);

                // Listen for permission changes
                result.addEventListener('change', () => {
                    setPermissionState(result.state);
                });

                // If already granted, get position immediately
                if (result.state === 'granted') {
                    getCurrentPosition();
                } else {
                    setIsLoading(false);
                }
            } catch (err) {
                // Firefox doesn't support geolocation permission query
                setPermissionState('unknown');
                setIsLoading(false);
            }
        }

        checkPermission();
    }, []);

    const getCurrentPosition = useCallback(() => {
        // If mocked, just return mock position
        if (shouldMockLocation()) {
            setPosition(DEV_MOCK_LOCATION);
            setPermissionState('granted');
            setIsMocked(true);
            setIsLoading(false);
            return;
        }

        if (!navigator.geolocation) {
            setError('Geolocation not supported by your browser');
            setIsLoading(false);
            return;
        }

        setIsLoading(true);
        setError(null);

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                setPosition({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude,
                });
                setPermissionState('granted');
                setIsLoading(false);
            },
            (err) => {
                switch (err.code) {
                    case err.PERMISSION_DENIED:
                        setError('Location permission denied');
                        setPermissionState('denied');
                        break;
                    case err.POSITION_UNAVAILABLE:
                        setError('Location unavailable');
                        break;
                    case err.TIMEOUT:
                        setError('Location request timed out');
                        break;
                    default:
                        setError('Failed to get location');
                }
                setIsLoading(false);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000, // Cache position for 1 minute
            }
        );
    }, []);

    const requestLocation = useCallback(() => {
        getCurrentPosition();
    }, [getCurrentPosition]);

    return {
        position,
        error,
        permissionState,
        isLoading,
        requestLocation,
        isMocked,
    };
}
