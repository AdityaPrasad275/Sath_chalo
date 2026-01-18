import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getStops, getRoutes, getTrips, getTripStops } from './api';
import './App.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapPage() {
    const [stops, setStops] = useState([]);
    const [routes, setRoutes] = useState([]);
    const [activeRoute, setActiveRoute] = useState(null);
    const [routeTrips, setRouteTrips] = useState([]);
    const [routePath, setRoutePath] = useState([]);

    useEffect(() => {
        getStops().then(setStops).catch(console.error);
        getRoutes().then(setRoutes).catch(console.error);
    }, []);

    const handleRouteSelect = async (routeId) => {
        setActiveRoute(routeId);
        setRoutePath([]);
        try {
            const trips = await getTrips(routeId);
            setRouteTrips(trips);

            if (trips.length > 0) {
                const firstTripId = trips[0].trip_id;
                const tripStops = await getTripStops(firstTripId);
                const path = tripStops.map(s => [s.stop_lat, s.stop_lon]);
                setRoutePath(path);
            }
        } catch (e) {
            console.error(e);
        }
    };

    return (
        <div className="container">
            <div className="sidebar">
                <h2>Explorer</h2>
                <h3>Routes</h3>
                <ul>
                    {routes.map(r => (
                        <li
                            key={r.route_id}
                            onClick={() => handleRouteSelect(r.route_id)}
                            className={activeRoute === r.route_id ? 'active' : ''}
                        >
                            {r.route_short_name} - {r.route_long_name}
                        </li>
                    ))}
                </ul>
                <div className="stats">
                    <p>Stops: {stops.length}</p>
                    {activeRoute && <p>Trips on Route: {routeTrips.length}</p>}
                </div>
            </div>
            <div className="map-container">
                <MapContainer center={[12.9716, 77.5946]} zoom={13} style={{ height: '100%', width: '100%' }}>
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    />
                    {routePath.length > 0 && (
                        <Polyline positions={routePath} color="blue" weight={5} opacity={0.7} />
                    )}
                    {stops.map(stop => (
                        <Marker key={stop.stop_id} position={[stop.stop_lat, stop.stop_lon]}>
                            <Popup>
                                {stop.stop_name} ({stop.stop_id})
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>
        </div>
    );
}

export default MapPage;
