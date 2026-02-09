import { Link } from 'react-router-dom';
import { formatRoundedDistance } from '../../utils/geo';
import './StopCard.css';

/**
 * StopCard - Clean, simplified stop display
 * Shows stop name, distance, and routes as "towards" information
 */
export function StopCard({ stop, distance }) {
    const stopId = stop.stop_id || stop.id;

    return (
        <Link to={`/stop/${stopId}`} className="stop-card">
            {/* Stop name - 2/3 width, 2/3 height, top-left */}
            <div className="stop-card__name-container">
                <h3 className="stop-card__name">{stop.stop_name || stop.name}</h3>
            </div>

            {/* Distance - 1/3 width, full height, right side */}
            {distance != null && (
                <div className="stop-card__distance-container">
                    <p className="stop-card__distance">{formatRoundedDistance(distance)}</p>
                </div>
            )}

            {/* Towards - 2/3 width, 1/3 height, bottom-left */}
            <div className="stop-card__towards-container">
                <span className="stop-card__towards-label">towards</span>
                <span className="stop-card__towards-text">Downtown, Airport, Mall</span>
            </div>
        </Link>
    );
}

