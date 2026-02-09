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
        <div className={`timeline-stop ${status === 'passed' ? 'timeline-stop--passed' : ''}`}>
            {/* Timeline graphic - absolutely positioned to left */}
            <div className="timeline-stop__graphic">
                <TimelineNode position={position} state={nodeState} height={64} />
            </div>

            {/* Content - has left padding to clear graphic */}
            <div className="timeline-stop__content">
                <div className="timeline-stop__name">{stopName}</div>

                {isUserStop && (
                    <span className="timeline-stop__label timeline-stop__label--user">
                        Your stop
                    </span>
                )}
            </div>

            <div className="timeline-stop__time">{scheduledTime}</div>
        </div>
    );
}
