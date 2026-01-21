import './Timeline.css';
import { Pulse } from './Pulse';

/**
 * Timeline - Horizontal 1D visualization of bus approaching stop
 * 
 * Props:
 * - minutesUntil: number of minutes until arrival
 * - maxMinutes: maximum minutes to show (for scaling)
 */
export function Timeline({ minutesUntil, maxMinutes = 15 }) {
    // Calculate position: 0% = far left (furthest), 100% = right (arrived)
    // Clamp between 0 and 100
    const progress = Math.max(0, Math.min(100, (1 - minutesUntil / maxMinutes) * 100));

    // If bus has departed, hide the dot
    const hasDeparted = minutesUntil < 0;
    const hasArrived = minutesUntil <= 0;

    return (
        <div className="timeline">
            <div className="timeline__track">
                <div
                    className="timeline__progress"
                    style={{ width: `${progress}%` }}
                />
                {!hasDeparted && (
                    <div
                        className="timeline__bus"
                        style={{ left: `${progress}%` }}
                    >
                        <Pulse isScheduled={true} />
                    </div>
                )}
            </div>
            <div className={`timeline__stop ${hasArrived ? 'timeline__stop--active' : ''}`}>
                <div className="timeline__stop-marker" />
            </div>
        </div>
    );
}
