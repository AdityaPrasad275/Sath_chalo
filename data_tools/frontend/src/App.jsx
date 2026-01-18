import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './NavBar';
import MapPage from './MapPage';
import TimetablePage from './TimetablePage';
import './App.css';

function App() {
  return (
    <Router>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <NavBar />
        <div style={{ flexGrow: 1, position: 'relative' }}>
          <Routes>
            <Route path="/" element={<MapPage />} />
            <Route path="/all" element={<TimetablePage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
