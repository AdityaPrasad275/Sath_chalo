import React from 'react';
import { NavLink } from 'react-router-dom';

function NavBar() {
    return (
        <nav style={{ background: '#333', color: 'white', padding: '10px 20px', display: 'flex', gap: '20px' }}>
            <div style={{ fontWeight: 'bold', fontSize: '1.2em', marginRight: '20px' }}>TransiViz</div>
            <NavLink
                to="/"
                className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
                style={{ color: 'white', textDecoration: 'none' }}
            >
                Map
            </NavLink>
            <NavLink
                to="/all"
                className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}
                style={{ color: 'white', textDecoration: 'none' }}
            >
                Timetable
            </NavLink>
            <style>{`
        .nav-link.active { border-bottom: 2px solid white; }
        .nav-link:hover { opacity: 0.8; }
      `}</style>
        </nav>
    );
}

export default NavBar;
