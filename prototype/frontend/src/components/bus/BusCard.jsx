import './BusCard.css';
import { getMinutesUntil, formatRelativeTime } from '../../utils/time';
import { Timeline } from '../common/Timeline';
import { ChevronRightIcon } from '../icons';

/**
 * BusCard - Shows a single bus arrival with pulse timeline
 * 
 * Props:
 * - trip: { trip, arrival_time, departure_time, stop_sequence }
 * - onClick: function to handle card click
 */
export function BusCard({ trip, onClick }) {
    const arrivalTime = trip.arrival_time;
    const minutesUntil = getMinutesUntil(arrivalTime);
    const relativeTime = formatRelativeTime(minutesUntil);

    // Extract route info from API response
    // API returns: { trip: { route: "R02", route_name: "200" }, arrival_time: "..." }
    const tripData = trip.trip || {};
    const routeName = tripData.route_name || tripData.route || 'Route';
    // const headsign = tripData.trip_headsign || '';
    const headed_to = tripData.headed_to || '';
    // Determine if bus has departed
    const hasDeparted = minutesUntil < 0;

    return (
        <button
            className={`bus-card ${hasDeparted ? 'bus-card--departed' : ''}`}
            onClick={onClick}
            type="button"
        >
            <div className="bus-card__header">
                <div className="bus-card__info">
                    <div className="bus-card__route">
                        <span className="bus-card__route-name">{routeName}</span>
                    </div>
                    {headed_to && (
                        <div className="bus-card__destination">
                            <span className="bus-card__headsign">{headed_to}</span>
                        </div>
                    )}
                </div>

                <div className="bus-card__time">
                    <span className={`bus-card__time-value ${hasDeparted ? 'bus-card__time-value--late' : ''}`}>
                        {relativeTime}
                    </span>
                </div>
            </div>

            <div className="bus-card__timeline">
                <Timeline minutesUntil={minutesUntil} maxMinutes={60} />
            </div>
        </button>
    );
}
