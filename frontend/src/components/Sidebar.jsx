import React from 'react';
import { useNavigate } from 'react-router-dom';
import TrustBadge from './TrustBadge'; // Yeni bileşeni ekle

const Sidebar = ({ trustScore = 0 }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <div className="sidebar">
      <h3>🛡️ Adaptive Access</h3>
      
      {/* Trust Score Göstergesi */}
      <TrustBadge score={trustScore} />
      
      <ul style={{marginTop: '20px'}}>
        <li style={{fontWeight: 'bold', color: '#2c3e50'}}>📊 Dashboard</li>
        <li>⚙️ Settings</li>
        <li>👤 Profile</li>
        <li onClick={handleLogout} style={{color: '#e74c3c', marginTop: 'auto'}}>
          🚪 Logout
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;