import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message;

    console.error('API Error:', { status, message, error });
    
    // Could add user-friendly error handling here
    // e.g., show toast notifications
    
    return Promise.reject(error);
  }
);

export default apiClient;
