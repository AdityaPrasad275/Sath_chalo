import { formatDistance } from '../../utils/geo';
import { StopDotIcon, ChevronRightIcon } from '../icons';
import './StopCard.css';

/**
 * StopCard - displays a single stop with distance and routes
 */
export function StopCard({ stop, distance, onClick }) {
    // Extract routes from stop data if available
    const routes = stop.routes || [];

    return (
        <button className="stop-card" onClick={onClick}>
            <StopDotIcon className="stop-card__icon" filled />
            <div className="stop-card__content">
                <div className="stop-card__header">
                    <span className="stop-card__name">{stop.stop_name || stop.name}</span>
                    {distance != null && (
                        <span className="stop-card__distance">{formatDistance(distance)}</span>
                    )}
                </div>
                {routes.length > 0 && (
                    <div className="stop-card__routes">
                        {routes.slice(0, 4).map((route, i) => (
                            <span key={i} className="stop-card__route">
                                {route.route_short_name || route}
                            </span>
                        ))}
                        {routes.length > 4 && (
                            <span className="stop-card__more">+{routes.length - 4}</span>
                        )}
                    </div>
                )}
            </div>
            <ChevronRightIcon className="stop-card__arrow" />
        </button>
    );
}
