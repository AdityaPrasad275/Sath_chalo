import './BusInTransitCard.css';
import { BusIconFilled } from '../icons';

/**
 * BusInTransitCard - Shows bus traveling between stops
 * 
 * Props:
 * - routeName: string (e.g., "502")
 * - betweenStops: [string, string] | null
 * - position: 'before-start' | 'between' | 'after-end'
 */
export function BusInTransitCard({
    routeName,
    betweenStops = null,
    position = 'between'
}) {
    const getMessage = () => {
        if (position === 'before-start') {
            return `Bus ${routeName} hasn't started yet`;
        }
        if (position === 'after-end') {
            return `Bus ${routeName} has completed this route`;
        }
        if (betweenStops && betweenStops.length === 2) {
            return (
                <>
                    <div className="bus-transit__primary">
                        Bus {routeName} is here
                    </div>
                    <div className="bus-transit__secondary">
                        Between {betweenStops[0]} & {betweenStops[1]}
                    </div>
                </>
            );
        }
        return `Bus ${routeName} is traveling`;
    };

    return (
        <div className={`bus-transit-card bus-transit-card--${position}`}>
            {/* Bus icon */}
            <div className="bus-transit__graphic">
                <BusIconFilled size={24} />
            </div>

            {/* Content */}
            <div className="bus-transit__content">
                {getMessage()}
            </div>
        </div>
    );
}
