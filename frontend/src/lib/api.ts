import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  login: (data: URLSearchParams) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
  getCameras: (params?: any) => api.get('/api/cameras', { params }),
  getCamera: (id: string) => api.get(`/api/cameras/${id}`),
  getVehicles: (params?: any) => api.get('/api/vehicles', { params }),
  getVehicleTrajectory: (plate: string) => api.get(`/api/vehicles/${plate}/trajectory`),
  getVehicleDetections: (plate: string) => api.get(`/api/vehicles/${plate}/detections`),
  getDetections: (params?: any) => api.get('/api/detections', { params }),
  getRecentDetections: () => api.get('/api/detections/recent'),
  getTrafficStats: () => api.get('/api/analytics/stats'),
  getVehiclesByCamera: () => api.get('/api/analytics/vehicles-by-camera'),
  getVehiclesByHour: () => api.get('/api/analytics/vehicles-by-hour'),
  getVehiclesByZone: () => api.get('/api/analytics/vehicles-by-zone'),
  getCongestion: () => api.get('/api/analytics/congestion'),
  getHeatmap: (metric: string = 'density') => api.get(`/api/analytics/heatmap?metric=${metric}`),
  getODMatrix: () => api.get('/api/analytics/od-matrix'),
  getAlerts: (params?: any) => api.get('/api/alerts', { params }),
  updateAlertStatus: (id: string, status: string) => api.put(`/api/alerts/${id}/status`, { status }),
  getWatchlist: () => api.get('/api/watchlist'),
  addToWatchlist: (data: any) => api.post('/api/watchlist', data),
  removeFromWatchlist: (id: string) => api.delete(`/api/watchlist/${id}`),
};
