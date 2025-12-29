import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
  const response = await api.post('/auth/login', { email, password });

  // ✅ Backend bazen { ok: true, data: {...} } döndürür
  const payload = response.data?.data ?? response.data;

  // 🔴 DECOY
  if (payload?.ui_state === 'decoy') {
    localStorage.removeItem('token');
    localStorage.setItem('trust_score', String(payload.trust_score ?? 0));
    navigate('/decoy');
    return;
  }

  // 🟢 ALLOW (token ile)
  if (payload?.access_token) {
    localStorage.setItem('token', payload.access_token);
    localStorage.setItem('trust_score', String(payload.trust_score ?? 0));
    navigate('/dashboard');
    return;
  }

  // 🟡 MFA gerekiyorsa (bazı backend'ler bunu 200 içinde de döndürebilir)
  if (payload?.error === 'MFA_REQUIRED' || payload?.require_mfa === true) {
    alert('MFA gerekiyor. (Şimdilik MFA ekranı yok)');
    return;
  }

  console.error('Beklenmeyen login response:', response.data);
  alert('Login response beklenmeyen formatta geldi.');
} catch (error) {
  // ✅ Backend cevap verdiyse (server çalışıyor)
  if (error.response) {
    const resp = error.response.data;
    const errObj = resp?.error ?? resp; // bazen {error:{...}} bazen direkt gelir

    // MFA
    if (errObj?.code === 'MFA_REQUIRED' || errObj?.error === 'MFA_REQUIRED') {
      alert('MFA gerekiyor. (Şimdilik MFA ekranı yok)');
      return;
    }

    // Yanlış şifre / kullanıcı yok
    if (errObj?.code === 'INVALID_CREDENTIALS' || errObj?.error === 'INVALID_CREDENTIALS') {
      alert('E-posta veya şifre hatalı.');
      return;
    }

    // Validasyon vs.
    alert(errObj?.message || 'Giriş başarısız.');
    return;
  }

  // ✅ Backend'e ulaşılamadıysa (network error)
  console.warn('Backend erişilemiyor, Test Modu devrede.');
  alert('⚠️ Backend kapalı. Test moduyla giriş yapılıyor...');

  localStorage.setItem('token', 'fake-test-token-12345');
  localStorage.setItem('trust_score', '80');
  navigate('/dashboard');
}


  };

  return (
    <div className="login-container">
      <h2>Adaptive Access</h2>
      <p style={{color: 'var(--text-secondary)'}}>Secure Login</p>
      <form onSubmit={handleLogin}>
        <input 
          type="email" 
          placeholder="Email Address" 
          onChange={(e) => setEmail(e.target.value)} 
          required
        />
        <input 
          type="password" 
          placeholder="Password" 
          onChange={(e) => setPassword(e.target.value)} 
          required
        />
        <button type="submit">Sign In</button>
      </form>
    </div>
  );
};

export default Login;