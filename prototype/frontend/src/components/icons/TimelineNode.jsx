/**
 * TimelineNode - SVG component for timeline visualization
 * 
 * Shows circle node with connecting lines based on position
 * Supports different states (passed, current, upcoming, user)
 */

export function TimelineNode({ position = 'middle', state = 'upcoming', height = 48 }) {
    // Determine circle size and style based on state
    const getCircleStyle = () => {
        switch (state) {
            case 'passed':
                return { r: 4, fill: '#525252', stroke: 'none' };
            case 'current':
                return { r: 6, fill: '#f59e0b', stroke: 'none', animate: true };
            case 'upcoming':
                return { r: 5, fill: 'none', stroke: '#a3a3a3', strokeWidth: 2 };
            case 'user':
                return { type: 'star', fill: '#3b82f6', glow: true };
            default:
                return { r: 5, fill: 'none', stroke: '#a3a3a3', strokeWidth: 2 };
        }
    };

    const circleStyle = getCircleStyle();
    const lineColor = state === 'passed' ? '#525252' : '#a3a3a3';

    // SVG viewBox: 24px wide, dynamic height
    const centerX = 12;
    const centerY = height / 2;

    return (
        <svg
            width="24"
            height={height}
            viewBox={`0 0 24 ${height}`}
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className="timeline-node"
        >
            {/* Line from top (for middle and last positions) */}
            {(position === 'middle' || position === 'last') && (
                <line
                    x1={centerX}
                    y1={0}
                    x2={centerX}
                    y2={centerY - 8}
                    stroke={lineColor}
                    strokeWidth="2"
                />
            )}

            {/* Circle or Star */}
            {circleStyle.type === 'star' ? (
                <g>
                    {/* Glow effect for user's stop */}
                    {circleStyle.glow && (
                        <circle
                            cx={centerX}
                            cy={centerY}
                            r="10"
                            fill={circleStyle.fill}
                            opacity="0.2"
                        />
                    )}
                    {/* Star path */}
                    <path
                        d={`M ${centerX},${centerY - 7} 
                           L ${centerX + 2},${centerY - 2} 
                           L ${centerX + 7},${centerY - 2} 
                           L ${centerX + 3.5},${centerY + 1} 
                           L ${centerX + 5},${centerY + 6} 
                           L ${centerX},${centerY + 3} 
                           L ${centerX - 5},${centerY + 6} 
                           L ${centerX - 3.5},${centerY + 1} 
                           L ${centerX - 7},${centerY - 2} 
                           L ${centerX - 2},${centerY - 2} Z`}
                        fill={circleStyle.fill}
                    />
                </g>
            ) : (
                <circle
                    cx={centerX}
                    cy={centerY}
                    r={circleStyle.r}
                    fill={circleStyle.fill || 'none'}
                    stroke={circleStyle.stroke}
                    strokeWidth={circleStyle.strokeWidth}
                    className={circleStyle.animate ? 'timeline-node__pulse' : ''}
                />
            )}

            {/* Line to bottom (for first and middle positions) */}
            {(position === 'first' || position === 'middle') && (
                <line
                    x1={centerX}
                    y1={centerY + 8}
                    x2={centerX}
                    y2={height}
                    stroke={lineColor}
                    strokeWidth="2"
                />
            )}
        </svg>
    );
}
