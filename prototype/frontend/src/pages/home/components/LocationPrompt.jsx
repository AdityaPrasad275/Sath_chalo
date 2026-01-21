import { MapPinIcon } from '../../../components/icons';

export function LocationPrompt({ onPermissionRequest, isLoading }) {
    return (
        <button
            className="home__location-btn"
            onClick={onPermissionRequest}
            disabled={isLoading}
        >
            <MapPinIcon className="home__location-icon" />
            <span>Use my location</span>
        </button>
    );
}
