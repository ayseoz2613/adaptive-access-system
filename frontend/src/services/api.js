import axios from 'axios';

// Backend adresi. Backend çalışmıyorsa bile burası böyle kalsın.
const api = axios.create({
  baseURL: 'http://localhost:5000/api', 
  headers: {
    'Content-Type': 'application/json',
  }
});

// Her istekte Token var mı diye bakıp ekleyen yapı (Interceptor)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;