import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard'; // Artık gerçek dosyayı çekiyor
import DecoyDashboard from './pages/DecoyDashboard'; // Yeni sayfa

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/decoy" element={<DecoyDashboard />} /> {/* Rota eklendi */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;