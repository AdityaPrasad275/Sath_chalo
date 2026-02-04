import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useTrip } from '../hooks/useTrip';
import { ArrowLeftIcon } from '../components/icons';
import { StopCard } from '../components/bus/StopCard';
import { BusInTransitCard } from '../components/bus/BusInTransitCard';
import './Trip.css';

/**
 * Trip Page - Bus Timeline/Rail View
 * Shows full route with all stops, bus position, and user's stop
 */
export function Trip() {
    const { tripId } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const userStopId = searchParams.get('userStop');

    const { trip, stopTimes, currentStopIndex, isLoading, error, refetch } = useTrip(tripId);
    const [isScrolled, setIsScrolled] = useState(false);
    const busCardRef = useRef(null);

    // Auto-scroll to bus position on mount
    useEffect(() => {
        if (busCardRef.current && !isLoading) {
            setTimeout(() => {
                busCardRef.current?.scrollIntoView({
                    behavior: 'smooth',
                    block: 'center'
                });
            }, 300);
        }
    }, [currentStopIndex, isLoading]);

    // Detect scroll for header shadow
    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    // Calculate ETA to user's stop
    const calculateEta = () => {
        if (!userStopId || currentStopIndex === null || !stopTimes.length) {
            return null;
        }

        const userStopIndex = stopTimes.findIndex(st => st.stop === userStopId);
        if (userStopIndex === -1 || userStopIndex <= currentStopIndex) {
            return null;
        }

        const stopsAway = userStopIndex - currentStopIndex;

        // Estimate time based on stop times
        const currentTime = stopTimes[currentStopIndex]?.arrival_time;
        const userStopTime = stopTimes[userStopIndex]?.arrival_time;

        if (currentTime && userStopTime) {
            const [ch, cm] = currentTime.split(':').map(Number);
            const [uh, um] = userStopTime.split(':').map(Number);
            const currentMinutes = ch * 60 + cm;
            const userMinutes = uh * 60 + um;
            const minutesAway = userMinutes - currentMinutes;

            return { stopsAway, minutesAway };
        }

        return { stopsAway, minutesAway: null };
    };

    const eta = calculateEta();

    // Determine bus position based on current time comparison
    const busPosition = (() => {
        if (!stopTimes || stopTimes.length === 0) {
            return { type: 'before-start' };
        }

        // currentStopIndex is the last stop where arrival_time <= current time

        if (currentStopIndex === null) {
            // Current time is before first stop
            return { type: 'before-start' };
        }

        if (currentStopIndex >= stopTimes.length - 1) {
            // Bus has reached or passed the last stop
            return { type: 'after-end' };
        }

        // Bus is between currentStopIndex and the next stop
        // We want to insert the bus card BEFORE the next upcoming stop
        return {
            type: 'between',
            beforeStopIndex: currentStopIndex,
            afterStopIndex: currentStopIndex + 1,  // Insert BEFORE this stop
            beforeStopName: stopTimes[currentStopIndex]?.stop_name,
            afterStopName: stopTimes[currentStopIndex + 1]?.stop_name
        };
    })();

    if (isLoading) {
        return (
            <div className="trip">
                <div className="trip__loading">
                    <div className="trip__loading-spinner" />
                    <span>Loading trip details...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="trip">
                <div className="trip__error">
                    <p>{error}</p>
                    <button className="trip__retry" onClick={refetch}>
                        Try again
                    </button>
                </div>
            </div>
        );
    }

    if (!trip) {
        return (
            <div className="trip">
                <div className="trip__error">
                    <p>Trip not found</p>
                    <button className="trip__retry" onClick={() => navigate(-1)}>
                        Go back
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="trip">
            <header className={`trip__header ${isScrolled ? 'trip__header--scrolled' : ''}`}>
                <button
                    className="trip__back"
                    onClick={() => navigate(-1)}
                    aria-label="Go back"
                >
                    <ArrowLeftIcon className="trip__back-icon" />
                </button>

                <div className="trip__info">
                    <div className="trip__route">
                        Route {trip.route_name || trip.route}
                    </div>
                    <div className="trip__destination">
                        {trip.headed_to || 'Final Stop'}
                    </div>
                    {eta && (
                        <div className="trip__eta">
                            <span className="trip__eta-highlight">{eta.stopsAway} stops away</span>
                            {eta.minutesAway && (
                                <> · ~<span className="trip__eta-highlight">{eta.minutesAway} min</span></>
                            )}
                        </div>
                    )}
                </div>
            </header>

            <main className="trip__rail">
                {/* Bus before first stop */}
                {busPosition.type === 'before-start' && (
                    <div ref={busCardRef}>
                        <BusInTransitCard
                            routeName={trip.route_name || trip.route}
                            position="before-start"
                        />
                    </div>
                )}

                {/* Stops and bus in-transit */}
                {stopTimes.map((stopTime, index) => {
                    const isUserStop = stopTime.stop === userStopId;
                    // Include current stop in "passed" to mark it as dimmed
                    const isPassed = currentStopIndex !== null && index <= currentStopIndex;

                    // Determine position
                    let position = 'middle';
                    if (index === 0) position = 'first';
                    if (index === stopTimes.length - 1) position = 'last';

                    // Determine status (only passed/upcoming, no 'current')
                    let status = 'upcoming';
                    if (isPassed) status = 'passed';

                    // Show bus card BEFORE this stop if this is the afterStopIndex
                    const showBusBefore =
                        busPosition.type === 'between' &&
                        busPosition.afterStopIndex === index;

                    return (
                        <div key={`${stopTime.stop}-${index}`} className="stop-wrapper">
                            {/* Insert bus card BEFORE this stop if needed */}
                            {showBusBefore && (
                                <div ref={busCardRef}>
                                    <BusInTransitCard
                                        routeName={trip.route_name || trip.route}
                                        betweenStops={[
                                            busPosition.beforeStopName,
                                            busPosition.afterStopName
                                        ]}
                                        position="between"
                                    />
                                </div>
                            )}

                            <StopCard
                                stopName={stopTime.stop_name}
                                scheduledTime={stopTime.arrival_time?.substring(0, 5)}
                                position={position}
                                status={status}
                                isUserStop={isUserStop}
                            />
                        </div>
                    );
                })}
            </main>
        </div>
    );
}
