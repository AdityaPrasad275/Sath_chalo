import './StopCard.css';
import { TimelineNode } from '../icons/TimelineNode';

/**
 * StopCard - Individual stop in the timeline
 * Uses absolute positioning for seamless graphic connection
 */
export function StopCard({
    stopName,
    scheduledTime,
    position = 'middle',
    status = 'upcoming',
    isUserStop = false
}) {
    const nodeState = isUserStop ? 'user' : status;

    return (
        <div className={`stop-card ${status === 'passed' ? 'stop-card--passed' : ''}`}>
            {/* Timeline graphic - absolutely positioned to left */}
            <div className="stop-card__graphic">
                <TimelineNode position={position} state={nodeState} height={64} />
            </div>

            {/* Content - has left padding to clear graphic */}
            <div className="stop-card__content">
                <div className="stop-card__name">{stopName}</div>

                {isUserStop && (
                    <span className="stop-card__label stop-card__label--user">
                        Your stop
                    </span>
                )}
            </div>

            <div className="stop-card__time">{scheduledTime}</div>
        </div>
    );
}
