import React from 'react';

const RiskIndicator = ({ score, level }) => {
  const getColor = () => {
    if (level === 'SAFE') return 'var(--color-safe)';
    if (level === 'SUSPICIOUS') return 'var(--color-suspicious)';
    if (level === 'CRITICAL') return 'var(--color-critical)';
    return '#ccc';
  };

  const color = getColor();

  return (
    <div className="risk-card" style={{ borderTop: `5px solid ${color}` }}>
      <h3 style={{ margin: 0 }}>Risk Analysis</h3>
      <p style={{ fontSize: '12px', color: '#777' }}>Current Session Status</p>

      <div className="score-circle" style={{ backgroundColor: color }}>
        {score}
      </div>

      <p style={{ fontSize: '18px', fontWeight: 'bold', color }}>
        {level}
      </p>
    </div>
  );
};

export default RiskIndicator;
