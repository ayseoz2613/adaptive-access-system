import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import RiskIndicator from '../components/RiskIndicator';
import Toast from '../components/Alert/Toast';
import api from '../services/api';

const Dashboard = () => {
  const [riskData, setRiskData] = useState({ score: 0, level: 'LOADING' });
  const [alerts, setAlerts] = useState([]);

  const navigate = useNavigate();

  // ✅ Trust score'u burada al (return'ün üstünde!)
  const trustScore = Number(localStorage.getItem('trust_score') || 0);

  // alert functions
  const addAlert = (message, type) => {
    const id = Date.now();
    setAlerts(prev => [...prev, { id, message, type }]);
  };

  const removeAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  // risk data fetch
  useEffect(() => {
    const fetchRiskStatus = async () => {
      try {
        const response = await api.get('/risk/status');
        updateRiskState(response.data);
      } catch (error) {
        // Backend is unreachable, set default safe state
        updateRiskState({ score: 20, level: 'SAFE' });
      }
    };
    fetchRiskStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // adaptive UI based on risk state
  const updateRiskState = (data) => {
    setRiskData(data);

    if (data.level === 'SUSPICIOUS') {
      addAlert("Unusual activity detected! Please verify your identity.", "warning");
    } else if (data.level === 'CRITICAL') {
      navigate('/decoy');
    }
  };

  // test function to simulate risk level changes
  const simulateRisk = (newScore, newLevel) => {
    updateRiskState({ score: newScore, level: newLevel });
  };

  return (
    <div className={`dashboard-layout border-${riskData.level.toLowerCase()}`}>
      
      {/* ✅ Sidebar artık doğru şekilde render ediliyor */}
      <Sidebar trustScore={trustScore} />

      {/* alert container */}
      <div className="toast-container">
        {alerts.map(alert => (
          <Toast key={alert.id} {...alert} onClose={() => removeAlert(alert.id)} />
        ))}
      </div>

      {/* emergency lock overlay */}
      {riskData.level === 'CRITICAL' && (
        <div className="critical-overlay">
          <h1>🚫 SYSTEM LOCKED</h1>
          <p>Security breach detected. Access suspended.</p>
          <div style={{ fontSize: '50px', marginTop: '20px' }}>🔒</div>

          {/* unlock button for testing */}
          <button className="unlock-btn" onClick={() => simulateRisk(20, 'SAFE')}>
            Admin Unlock (Test)
          </button>
        </div>
      )}

      <div className="main-content">
        <h1>Adaptive Security Dashboard</h1>

        {/* test buttons */}
        <div style={{ background: '#eee', padding: '10px', borderRadius: '8px', marginBottom: '20px' }}>
          <small>🛠️ <strong>Developer Tools (Test Risk Levels):</strong></small><br />
          <button onClick={() => simulateRisk(20, 'SAFE')} style={{ width: 'auto', marginRight: '5px', background: 'green' }}>
            Safe
          </button>
          <button onClick={() => simulateRisk(55, 'SUSPICIOUS')} style={{ width: 'auto', marginRight: '5px', background: 'orange' }}>
            Suspicious
          </button>
          <button onClick={() => simulateRisk(95, 'CRITICAL')} style={{ width: 'auto', background: 'red' }}>
            Critical
          </button>
        </div>

        <RiskIndicator score={riskData.score} level={riskData.level} />

        <div style={{ marginTop: '30px', padding: '20px', background: 'white', borderRadius: '8px' }}>
          <h3>System Status</h3>
          <p>The UI adapts automatically based on the risk score above.</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
