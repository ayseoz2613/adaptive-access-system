import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  // ✅ Tek yerde localStorage yazma (her senaryo için)
  const saveRiskSnapshot = (obj) => {
    // obj: { risk_level, risk_score, adjusted_risk_score, trust_score, require_mfa, ui_state, alert_type }
    if (!obj) return;

    if (obj.risk_level != null) localStorage.setItem('risk_level', String(obj.risk_level).toLowerCase());
    if (obj.risk_score != null) localStorage.setItem('risk_score', String(obj.risk_score));
    if (obj.adjusted_risk_score != null) localStorage.setItem('adjusted_risk_score', String(obj.adjusted_risk_score));
    if (obj.trust_score != null) localStorage.setItem('trust_score', String(obj.trust_score));
    if (obj.require_mfa != null) localStorage.setItem('require_mfa', String(!!obj.require_mfa));
    if (obj.ui_state != null) localStorage.setItem('ui_state', String(obj.ui_state));
    if (obj.alert_type != null) localStorage.setItem('alert_type', String(obj.alert_type));
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      // İstersen burada device_info / location da gönderebilirsin (risk test için)
      const response = await api.post('/auth/login', { email, password });

      // ✅ Backend bazen { ok: true, data: {...} } döndürür
      const payload = response.data?.data ?? response.data;

      // 🔴 DECOY
      if (payload?.ui_state === 'decoy') {
        localStorage.removeItem('token');

        // ✅ risk/trust snapshot yaz
        saveRiskSnapshot({
          risk_level: payload.risk_level,
          risk_score: payload.risk_score,
          adjusted_risk_score: payload.adjusted_risk_score,
          trust_score: payload.trust_score,
          require_mfa: false,
          ui_state: 'decoy',
          alert_type: payload.alert_type || 'danger',
        });

        navigate('/decoy');
        return;
      }

      // 🟢 ALLOW (token ile)
      if (payload?.access_token) {
        localStorage.setItem('token', payload.access_token);

        // ✅ risk/trust snapshot yaz (hocaya frontend kanıtı)
        saveRiskSnapshot({
          risk_level: payload.risk_level,
          risk_score: payload.risk_score,
          adjusted_risk_score: payload.adjusted_risk_score,
          trust_score: payload.trust_score,
          require_mfa: payload.require_mfa,
          ui_state: payload.ui_state,
          alert_type: payload.alert_type,
        });

        navigate('/dashboard');
        return;
      }

      // 🟡 MFA gerekiyorsa (bazı backend'ler bunu 200 içinde de döndürebilir)
      if (payload?.error === 'MFA_REQUIRED' || payload?.require_mfa === true) {
        // Eğer backend 200 içinde details veriyorsa yakalayalım
        saveRiskSnapshot({
          risk_level: payload.risk_level || 'suspicious',
          risk_score: payload.risk_score,
          adjusted_risk_score: payload.adjusted_risk_score,
          trust_score: payload.trust_score,
          require_mfa: true,
          ui_state: 'mfa',
          alert_type: 'warning',
        });

        alert('MFA gerekiyor. (Şimdilik MFA ekranı yok) Dashboard’da SUSPICIOUS görünecek.');
        navigate('/dashboard');
        return;
      }

      console.error('Beklenmeyen login response:', response.data);
      alert('Login response beklenmeyen formatta geldi.');
    } catch (error) {
      // ✅ Backend cevap verdiyse (server çalışıyor)
      if (error.response) {
        const resp = error.response.data;

        // Bizim backend formatı: { ok:false, error:{ code, message, details } }
        const errObj = resp?.error ?? resp;

        // MFA (401)
        if (errObj?.code === 'MFA_REQUIRED' || errObj?.error === 'MFA_REQUIRED') {
          const d = errObj?.details || {};

          // ✅ MFA details içindeki risk/trust snapshot yaz
          saveRiskSnapshot({
            risk_level: d.risk_level || 'suspicious',
            risk_score: d.risk_score,
            adjusted_risk_score: d.adjusted_risk_score,
            trust_score: d.trust_score,
            require_mfa: true,
            ui_state: 'mfa',
            alert_type: 'warning',
          });

          alert('Şüpheli aktivite tespit edildi. MFA gerekli. Dashboard’da risk teması değişecek.');
          navigate('/dashboard');
          return;
        }

        // Yanlış şifre / kullanıcı yok
        if (errObj?.code === 'INVALID_CREDENTIALS' || errObj?.error === 'INVALID_CREDENTIALS') {
          alert('E-posta veya şifre hatalı.');
          return;
        }

        // Diğer hatalar
        alert(errObj?.message || 'Giriş başarısız.');
        return;
      }

      // ✅ Backend'e ulaşılamadıysa (network error)
      console.warn('Backend erişilemiyor, Test Modu devrede.');
      alert('⚠️ Backend kapalı. Test moduyla giriş yapılıyor...');

      localStorage.setItem('token', 'fake-test-token-12345');

      // ✅ Demo için safe snapshot
      saveRiskSnapshot({
        risk_level: 'safe',
        risk_score: 20,
        adjusted_risk_score: 20,
        trust_score: 80,
        require_mfa: false,
        ui_state: 'normal',
        alert_type: 'none',
      });

      navigate('/dashboard');
    }
  };

  return (
    <div className="login-container">
      <h2>Adaptive Access</h2>
      <p style={{ color: 'var(--text-secondary)' }}>Secure Login</p>

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
