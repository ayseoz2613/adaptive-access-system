import React from 'react';

const TrustBadge = ({ score }) => {
  // Puana göre renk değişimi
  const getColor = () => {
    if (score >= 80) return '#2ecc71'; // Yeşil (Güvenilir)
    if (score >= 50) return '#f1c40f'; // Sarı
    return '#e74c3c';                 // Kırmızı
  };

  return (
    <div style={{
      marginTop: '20px',
      padding: '10px',
      background: '#f8f9fa',
      borderRadius: '8px',
      textAlign: 'center',
      border: `1px solid ${getColor()}`
    }}>
      <small style={{color: '#7f8c8d', fontWeight: 'bold'}}>TRUST SCORE</small>
      <div style={{
        fontSize: '24px', 
        fontWeight: 'bold', 
        color: getColor(),
        marginTop: '5px'
      }}>
        {score}/100
      </div>
    </div>
  );
};

export default TrustBadge;