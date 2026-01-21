import { StopCard } from '../../../components/stops/StopCard';
import { SearchIcon, MapPinIcon } from '../../../components/icons';

export function StopsDisplay({
    stops,
    isLoading,
    searchQuery,
    onStopClick
}) {
    if (isLoading) {
        return (
            <div className="home__loading">
                <div className="home__loading-spinner" />
                <span>Finding stops...</span>
            </div>
        );
    }

    if (stops.length === 0 && !searchQuery) {
        return (
            <div className="home__empty">
                <p>No stops found nearby.</p>
                <p className="home__empty-hint">Try searching for a stop name</p>
            </div>
        );
    }

    if (stops.length === 0 && searchQuery) {
        return (
            <div className="home__empty">
                <p>No stops found matching "{searchQuery}"</p>
            </div>
        );
    }

    return (
        <div className="home__stops">
            <h2 className="home__section-title">
                {searchQuery ? (
                    <><SearchIcon className="home__section-icon" /> Search Results</>
                ) : (
                    <><MapPinIcon className="home__section-icon" /> Stops Near You</>
                )}
            </h2>
            <div className="home__stops-list">
                {stops.map((stop) => (
                    <StopCard
                        key={stop.id}
                        stop={stop}
                        distance={stop.distance}
                        onClick={() => onStopClick(stop)}
                    />
                ))}
            </div>
        </div>
    );
}
