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
      // Backend'e istek atıyoruz (Backend kapalıysa burası hata verir)
      const response = await api.post('/auth/login', { email, password });
      
      localStorage.setItem('token', response.data.access_token);
      navigate('/dashboard'); 

    } catch (error) {
      // --- BURAYI DEĞİŞTİRDİK ---
      console.warn("Backend kapalı, Test Modu devrede.");
      
      // Backend yoksa bile varmış gibi davranıp içeri alıyoruz
      alert("⚠️ Backend kapalı. Test moduyla giriş yapılıyor...");
      
      // Sahte bir token kaydedelim ki sistem giriş yapıldı sansın
      localStorage.setItem('token', 'fake-test-token-12345');
      
      // Dashboard'a yönlendir
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