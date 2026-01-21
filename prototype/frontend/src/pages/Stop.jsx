import { useParams, useNavigate, Link } from 'react-router-dom';
import { useUpcomingTrips } from '../hooks/useUpcomingTrips';
import { BusCard } from '../components/bus/BusCard';
import { ArrowLeftIcon, MapPinIcon } from '../components/icons';
import './Stop.css';

/**
 * Stop Detail Page - Shows buses coming to this stop
 */
export function Stop() {
    const { stopId } = useParams();
    const navigate = useNavigate();
    const { trips, isLoading, error, refetch } = useUpcomingTrips(stopId);

    // For now, use stopId as the display name
    // TODO: Fetch stop details to get actual name
    const stopName = stopId;

    const handleBusClick = (trip) => {
        // Navigate to trip detail page (Flow 3 - future)
        console.log('Navigate to trip:', trip);
    };

    return (
        <div className="stop">
            <header className="stop__header">
                <button
                    className="stop__back"
                    onClick={() => navigate(-1)}
                    aria-label="Go back"
                >
                    <ArrowLeftIcon className="stop__back-icon" />
                </button>
                <div className="stop__title">
                    <MapPinIcon className="stop__title-icon" />
                    <h1 className="stop__name">{stopName}</h1>
                </div>
            </header>

            <main className="stop__main">
                {isLoading && (
                    <div className="stop__loading">
                        <div className="stop__loading-spinner" />
                        <span>Loading buses...</span>
                    </div>
                )}

                {error && (
                    <div className="stop__error">
                        <p>{error}</p>
                        <button
                            className="stop__retry"
                            onClick={refetch}
                        >
                            Try again
                        </button>
                    </div>
                )}

                {!isLoading && !error && trips.length === 0 && (
                    <div className="stop__empty">
                        <p>No upcoming buses at this stop.</p>
                        <p className="stop__empty-hint">
                            Check back later for scheduled arrivals.
                        </p>
                    </div>
                )}

                {!isLoading && !error && trips.length > 0 && (
                    <div className="stop__buses">
                        <h2 className="stop__section-title">Upcoming Buses</h2>
                        <div className="stop__buses-list">
                            {trips.map((trip, index) => (
                                <BusCard
                                    key={`${trip.trip?.trip_id || index}-${trip.arrival_time}`}
                                    trip={trip}
                                    onClick={() => handleBusClick(trip)}
                                />
                            ))}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
