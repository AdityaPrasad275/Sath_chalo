import React, { useEffect, useState } from 'react';
import { getRoutes, getTimetable } from './api';

function TimetablePage() {
    const [routes, setRoutes] = useState([]);
    const [activeRouteId, setActiveRouteId] = useState(null);
    const [timetable, setTimetable] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        getRoutes().then(data => {
            setRoutes(data);
            if (data.length > 0) {
                setActiveRouteId(data[0].route_id);
            }
        });
    }, []);

    useEffect(() => {
        if (activeRouteId) {
            setLoading(true);
            getTimetable(activeRouteId)
                .then(setTimetable)
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    }, [activeRouteId]);

    return (
        <div className="container">
            <div className="sidebar">
                <h2>Timetable View</h2>
                <h3>Routes</h3>
                <ul>
                    {routes.map(r => (
                        <li
                            key={r.route_id}
                            onClick={() => setActiveRouteId(r.route_id)}
                            className={activeRouteId === r.route_id ? 'active' : ''}
                        >
                            {r.route_short_name} - {r.route_long_name}
                        </li>
                    ))}
                </ul>
            </div>
            <div className="main-content" style={{ flexGrow: 1, padding: '20px', overflow: 'auto' }}>
                {loading && <p>Loading timetable...</p>}
                {!loading && timetable && (
                    <div className="timetable-wrapper">
                        <h3>Timetable for Route {activeRouteId}</h3>
                        <table border="1" cellPadding="5" style={{ borderCollapse: 'collapse', width: '100%', fontSize: '14px' }}>
                            <thead>
                                <tr>
                                    <th style={{ position: 'sticky', left: 0, background: 'white', zIndex: 1 }}>Trip ID</th>
                                    {timetable.stops.map(stop => (
                                        <th key={stop.stop_id}>{stop.stop_name}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {timetable.trips.map(trip => (
                                    <tr key={trip.trip_id}>
                                        <td style={{ position: 'sticky', left: 0, background: 'white', fontWeight: 'bold' }}>{trip.trip_id}</td>
                                        {timetable.stops.map(stop => (
                                            <td key={stop.stop_id} style={{ textAlign: 'center' }}>
                                                {trip.times[stop.stop_id] || '-'}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

export default TimetablePage;
