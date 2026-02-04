/**
 * BusIcon - Simple bus icon for in-transit card
 */

export function BusIcon({ size = 24, className = '' }) {
    return (
        <svg
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            className={`bus-icon ${className}`}
        >
            {/* Bus body */}
            <rect
                x="4"
                y="6"
                width="16"
                height="11"
                rx="2"
                fill="#f59e0b"
                stroke="#f59e0b"
                strokeWidth="1.5"
            />

            {/* Windshield */}
            <rect
                x="6"
                y="8"
                width="5"
                height="4"
                rx="0.5"
                fill="#0a0a0a"
                opacity="0.3"
            />
            <rect
                x="13"
                y="8"
                width="5"
                height="4"
                rx="0.5"
                fill="#0a0a0a"
                opacity="0.3"
            />

            {/* Wheels */}
            <circle cx="8" cy="18" r="2" fill="#525252" />
            <circle cx="16" cy="18" r="2" fill="#525252" />

            {/* Wheel inner */}
            <circle cx="8" cy="18" r="0.8" fill="#a3a3a3" />
            <circle cx="16" cy="18" r="0.8" fill="#a3a3a3" />
        </svg>
    );
}
