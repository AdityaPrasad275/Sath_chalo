import { useState, useEffect } from 'react';
import { useGeolocation } from '../hooks/useGeolocation';
import { getNearbyStops, searchStops } from '../utils/api';
import { getDistance } from '../utils/geo';
import { StopCard } from '../components/stops/StopCard';
import './Home.css';

export function Home() {
    const { position, error: geoError, permissionState, isLoading: geoLoading, requestLocation, isMocked } = useGeolocation();

    const [stops, setStops] = useState([]);
    const [searchQuery, setSearchQuery] = useState('');
    const [isSearching, setIsSearching] = useState(false);
    const [fetchError, setFetchError] = useState(null);
    const [isLoadingStops, setIsLoadingStops] = useState(false);

    // Fetch nearby stops when position is available
    useEffect(() => {
        if (!position) return;

        async function fetchNearbyStops() {
            setIsLoadingStops(true);
            setFetchError(null);
            try {
                const data = await getNearbyStops(position.lon, position.lat, 1000);
                // Handle GeoJSON FeatureCollection format: data.results.features
                const features = data.results?.features || data.features || data.results || data || [];
                // Add distance to each stop
                const stopsWithDistance = features.map(stop => {
                    // GeoJSON Feature has geometry.coordinates and properties
                    const stopLat = stop.geometry?.coordinates?.[1] || stop.properties?.lat || stop.lat;
                    const stopLon = stop.geometry?.coordinates?.[0] || stop.properties?.lon || stop.lon;
                    const distance = getDistance(position.lat, position.lon, stopLat, stopLon);
                    return { ...stop, ...stop.properties, distance };
                });
                // Sort by distance
                stopsWithDistance.sort((a, b) => a.distance - b.distance);
                setStops(stopsWithDistance);
            } catch (err) {
                setFetchError(err.message);
            } finally {
                setIsLoadingStops(false);
            }
        }

        fetchNearbyStops();
    }, [position]);

    // Handle search
    useEffect(() => {
        if (!searchQuery.trim()) {
            // If search cleared and we have position, refetch nearby stops
            if (position) {
                // Re-trigger nearby fetch by calling the API
                async function refetchNearby() {
                    setIsLoadingStops(true);
                    setFetchError(null);
                    try {
                        const data = await getNearbyStops(position.lon, position.lat, 1000);
                        const features = data.results?.features || data.features || data.results || data || [];
                        const stopsWithDistance = features.map(stop => {
                            const stopLat = stop.geometry?.coordinates?.[1] || stop.properties?.lat || stop.lat;
                            const stopLon = stop.geometry?.coordinates?.[0] || stop.properties?.lon || stop.lon;
                            const distance = getDistance(position.lat, position.lon, stopLat, stopLon);
                            return { ...stop, ...stop.properties, distance };
                        });
                        stopsWithDistance.sort((a, b) => a.distance - b.distance);
                        setStops(stopsWithDistance);
                    } catch (err) {
                        setFetchError(err.message);
                    } finally {
                        setIsLoadingStops(false);
                    }
                }
                refetchNearby();
            }
            return;
        }

        const debounce = setTimeout(async () => {
            setIsSearching(true);
            setFetchError(null);
            try {
                const data = await searchStops(searchQuery);
                // Handle GeoJSON FeatureCollection format
                const features = data.results?.features || data.features || data.results || data || [];
                // If we have position, add distance
                if (position) {
                    const stopsWithDistance = features.map(stop => {
                        const stopLat = stop.geometry?.coordinates?.[1] || stop.properties?.lat || stop.lat;
                        const stopLon = stop.geometry?.coordinates?.[0] || stop.properties?.lon || stop.lon;
                        const distance = getDistance(position.lat, position.lon, stopLat, stopLon);
                        return { ...stop, ...stop.properties, distance };
                    });
                    stopsWithDistance.sort((a, b) => a.distance - b.distance);
                    setStops(stopsWithDistance);
                } else {
                    setStops(features.map(stop => ({ ...stop, ...stop.properties })));
                }
            } catch (err) {
                setFetchError(err.message);
            } finally {
                setIsSearching(false);
            }
        }, 300);

        return () => clearTimeout(debounce);
    }, [searchQuery, position]);

    const handleStopClick = (stop) => {
        // TODO: Navigate to stop detail page
        console.log('Navigate to stop:', stop);
    };

    const showLocationPrompt = permissionState !== 'granted' && !geoLoading;
    const showLoading = geoLoading || isLoadingStops;
    const showStops = stops.length > 0 && !showLoading;
    const showEmpty = !showLoading && !showLocationPrompt && stops.length === 0 && !searchQuery;

    return (
        <div className="home">
            <header className="home__header">
                <h1 className="home__title">🚌 Bus Radar</h1>
                {isMocked && (
                    <span className="home__mock-badge">🧪 Mock Location</span>
                )}
            </header>

            <main className="home__main">
                {/* Search Input */}
                <div className="home__search">
                    <input
                        type="text"
                        className="home__search-input"
                        placeholder="Search for a stop..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    {isSearching && <span className="home__search-spinner" />}
                </div>

                {/* Location Button - Only show if not granted */}
                {showLocationPrompt && (
                    <button
                        className="home__location-btn"
                        onClick={requestLocation}
                        disabled={geoLoading}
                    >
                        <span className="home__location-icon">📍</span>
                        <span>Use my location</span>
                    </button>
                )}

                {/* Error Messages */}
                {geoError && (
                    <div className="home__message home__message--error">
                        {geoError}
                    </div>
                )}
                {fetchError && (
                    <div className="home__message home__message--error">
                        {fetchError}
                    </div>
                )}

                {/* Loading State */}
                {showLoading && (
                    <div className="home__loading">
                        <div className="home__loading-spinner" />
                        <span>Finding stops...</span>
                    </div>
                )}

                {/* Stops List */}
                {showStops && (
                    <div className="home__stops">
                        <h2 className="home__section-title">
                            {searchQuery ? 'Search Results' : '📍 Stops Near You'}
                        </h2>
                        <div className="home__stops-list">
                            {stops.map((stop) => (
                                <StopCard
                                    key={stop.stop_id || stop.id}
                                    stop={stop}
                                    distance={stop.distance}
                                    onClick={() => handleStopClick(stop)}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Empty State */}
                {showEmpty && (
                    <div className="home__empty">
                        <p>No stops found nearby.</p>
                        <p className="home__empty-hint">Try searching for a stop name</p>
                    </div>
                )}
            </main>
        </div>
    );
}
