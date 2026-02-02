import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Landing } from './pages/Landing';
import { DriverDashboard } from './pages/DriverDashboard';
import { FleetDashboard } from './pages/FleetDashboard';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/driver" element={<DriverDashboard />} />
        <Route path="/fleet" element={<FleetDashboard />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
