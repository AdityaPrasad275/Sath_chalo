import { useState } from 'react';
import { useGeolocation } from '../hooks/useGeolocation';
import { useStops } from '../hooks/useStops';

// Sub-components
import { Header } from './home/components/Header';
import { SearchInput } from './home/components/SearchInput';
import { LocationPrompt } from './home/components/LocationPrompt';
import { StopsDisplay } from './home/components/StopsDisplay';

import './Home.css';

/**
 * Home page - Entry point for stops discovery
 */
export function Home() {
    const [searchQuery, setSearchQuery] = useState('');

    // Custom hooks for logic
    const {
        position,
        error: geoError,
        permissionState,
        isLoading: geoLoading,
        requestLocation,
        isMocked
    } = useGeolocation();

    const {
        stops,
        isSearching,
        isLoadingStops,
        fetchError
    } = useStops(position, searchQuery);

    const handleStopClick = (stop) => {
        console.log('Navigate to stop:', stop);
    };

    const showLocationPrompt = permissionState !== 'granted' && !geoLoading;
    const isLoading = geoLoading || isLoadingStops;

    return (
        <div className="home">
            <Header isMocked={isMocked} />

            <main className="home__main">
                <SearchInput
                    value={searchQuery}
                    onChange={setSearchQuery}
                    isSearching={isSearching}
                />

                {showLocationPrompt && (
                    <LocationPrompt
                        onPermissionRequest={requestLocation}
                        isLoading={geoLoading}
                    />
                )}

                {(geoError || fetchError) && (
                    <div className="home__message home__message--error">
                        {geoError || fetchError}
                    </div>
                )}

                <StopsDisplay
                    stops={stops}
                    isLoading={isLoading}
                    searchQuery={searchQuery}
                    onStopClick={handleStopClick}
                />
            </main>
        </div>
    );
}
