import React from 'react';
import Sidebar from '../components/Sidebar';

const DecoyDashboard = () => {
  return (
    <div className="dashboard-layout" style={{border: '5px solid transparent'}}> 
      {/* Sahte Sidebar: Düşük Trust Score gösterir */}
      <Sidebar trustScore={15} />

      <div className="main-content">
        <h1 style={{color: '#2c3e50'}}>System Overview</h1>
        
        {/* Sahte Uyarı */}
        <div style={{
          background: '#dff9fb', 
          padding: '15px', 
          borderRadius: '8px',
          marginBottom: '20px',
          borderLeft: '5px solid #22a6b3'
        }}>
          <strong>System Status:</strong> All systems operational. 
          <span style={{float: 'right', color: '#777'}}>Last updated: Just now</span>
        </div>

        {/* Sahte Grafikler (Resim veya CSS ile) */}
        <div style={{display: 'flex', gap: '20px'}}>
          <div style={{flex: 1, background: 'white', padding: '20px', borderRadius: '8px', height: '200px'}}>
            <h3>Network Traffic</h3>
            <div style={{marginTop: '50px', display: 'flex', alignItems: 'flex-end', height: '100px', gap: '10px'}}>
               {/* Rastgele çubuklar */}
               {[40, 70, 30, 80, 50, 90, 20].map((h, i) => (
                 <div key={i} style={{width: '100%', height: `${h}%`, background: '#3498db'}}></div>
               ))}
            </div>
          </div>
          
          <div style={{flex: 1, background: 'white', padding: '20px', borderRadius: '8px', height: '200px'}}>
             <h3>Active Sessions</h3>
             <p style={{fontSize: '40px', color: '#2ecc71', marginTop: '30px'}}>1</p>
             <small>Secure Connection Established</small>
          </div>
        </div>

        <p style={{marginTop: '50px', color: '#ccc', textAlign: 'center'}}>
           ⚠️ Decoy Environment Active - Logging all actions...
        </p>
      </div>
    </div>
  );
};

export default DecoyDashboard;