import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { Stop } from './pages/Stop';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/stop/:stopId" element={<Stop />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
