import './Pulse.css';

/**
 * Pulse - Animated bus dot for timeline
 * 
 * Props:
 * - isScheduled: if true, uses subtle pulse animation (vs verified = solid)
 * - isVerified: if true, shows as verified (brighter, no pulse)
 */
export function Pulse({ isScheduled = true, isVerified = false }) {
    const className = [
        'pulse',
        isScheduled && !isVerified ? 'pulse--scheduled' : '',
        isVerified ? 'pulse--verified' : ''
    ].filter(Boolean).join(' ');

    return (
        <div className={className}>
            <div className="pulse__dot" />
        </div>
    );
}
