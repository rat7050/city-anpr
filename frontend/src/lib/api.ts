import axios from 'axios';
import { WatchlistEntry } from '../types';
import { 
  INITIAL_CAMERAS, 
  INITIAL_WATCHLIST, 
  INITIAL_ALERTS, 
  INITIAL_STATS, 
  generateTrajectoryForPlate 
} from './mockData';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL,
  timeout: 3000,
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
    return Promise.reject(error);
  }
);

// In-memory dynamic state for demo/standalone mode
let localWatchlist = [...INITIAL_WATCHLIST];
let localAlerts = [...INITIAL_ALERTS];

export const apiService = {
  login: async (data: URLSearchParams) => {
    try {
      return await api.post('/api/auth/login', data);
    } catch {
      // Fallback auth for standalone demo
      const username = data.get('username') || 'admin';
      return {
        data: {
          access_token: 'demo-token-jwt-2026',
          token_type: 'bearer',
          role: 'ADMIN',
          username: username,
        }
      };
    }
  },

  getMe: async () => {
    try {
      return await api.get('/api/auth/me');
    } catch {
      return { data: { id: 'usr-admin', username: 'admin', email: 'admin@city-anpr.local', role: 'ADMIN' } };
    }
  },

  getCameras: async (params?: any) => {
    try {
      const res = await api.get('/api/cameras/', { params });
      return res;
    } catch {
      return { data: { cameras: INITIAL_CAMERAS, total: INITIAL_CAMERAS.length } };
    }
  },

  getCamera: async (id: string) => {
    try {
      return await api.get(`/api/cameras/${id}`);
    } catch {
      const cam = INITIAL_CAMERAS.find(c => c.id === id) || INITIAL_CAMERAS[0];
      return { data: cam };
    }
  },

  getVehicles: async (params?: any) => {
    try {
      return await api.get('/api/vehicles/', { params });
    } catch {
      const samplePlates = ['CG04AB1234', 'UP14BN4001', 'MH02AB1234', 'DL01CD5678', 'KA03EF9012'];
      const vehicles = samplePlates.map((plate, idx) => ({
        id: `veh-${idx}`,
        plate_number: plate,
        vehicle_type: 'CAR',
        color: 'BLACK',
        first_seen: new Date(Date.now() - 3600000 * 24).toISOString(),
        last_seen: new Date().toISOString(),
        detection_count: 8 + idx * 3,
      }));
      return { data: { vehicles, total: vehicles.length } };
    }
  },

  getVehicleTrajectory: async (plate: string) => {
    try {
      const res = await api.get(`/api/vehicles/${plate}/trajectory`);
      return res;
    } catch {
      const { trajectory } = generateTrajectoryForPlate(plate);
      return { data: trajectory };
    }
  },

  getVehicleDetections: async (plate: string) => {
    try {
      const res = await api.get(`/api/vehicles/${plate}/detections`);
      return res;
    } catch {
      const { detections } = generateTrajectoryForPlate(plate);
      return { data: detections };
    }
  },

  getDetections: async (params?: any) => {
    try {
      return await api.get('/api/detections/', { params });
    } catch {
      const { detections } = generateTrajectoryForPlate(params?.plate_number || 'CG04AB1234');
      return { data: { detections, total: detections.length } };
    }
  },

  getRecentDetections: async () => {
    try {
      return await api.get('/api/detections/recent');
    } catch {
      const { detections } = generateTrajectoryForPlate('CG04AB1234');
      const { detections: det2 } = generateTrajectoryForPlate('UP14BN4001');
      return { data: [...detections, ...det2].slice(0, 8) };
    }
  },

  getTrafficStats: async () => {
    try {
      return await api.get('/api/analytics/stats');
    } catch {
      return { data: INITIAL_STATS };
    }
  },

  getVehiclesByCamera: async () => {
    try {
      return await api.get('/api/analytics/vehicles-by-camera');
    } catch {
      return {
        data: INITIAL_CAMERAS.map(c => ({
          camera_id: c.id,
          camera_name: c.name,
          count: c.detection_count || 150
        }))
      };
    }
  },

  getVehiclesByHour: async () => {
    try {
      return await api.get('/api/analytics/vehicles-by-hour');
    } catch {
      const hours = Array.from({ length: 24 }, (_, i) => ({
        hour: i,
        count: Math.round(50 + Math.sin(i / 3) * 40 + Math.random() * 20)
      }));
      return { data: hours };
    }
  },

  getVehiclesByZone: async () => {
    try {
      return await api.get('/api/analytics/vehicles-by-zone');
    } catch {
      return {
        data: [
          { zone: 'Raipur North', count: 1240 },
          { zone: 'Raipur West', count: 980 },
          { zone: 'Raipur South', count: 1450 },
          { zone: 'Raipur Central', count: 620 },
        ]
      };
    }
  },

  getCongestion: async () => {
    try {
      return await api.get('/api/analytics/congestion');
    } catch {
      return {
        data: [
          { road_name: 'VIP Road', zone: 'Raipur North', congestion_index: 0.85, level: 'NORMAL', vehicle_count: 140, average_speed: 55.4 },
          { road_name: 'Ring Road', zone: 'Raipur West', congestion_index: 1.45, level: 'MODERATE', vehicle_count: 280, average_speed: 38.2 },
          { road_name: 'GE Road', zone: 'Raipur South', congestion_index: 2.10, level: 'SEVERE', vehicle_count: 490, average_speed: 18.5 },
          { road_name: 'Pandri Road', zone: 'Raipur Central', congestion_index: 1.65, level: 'HEAVY', vehicle_count: 310, average_speed: 26.0 },
        ]
      };
    }
  },

  getHeatmap: async (metric: string = 'density') => {
    try {
      return await api.get(`/api/analytics/heatmap?metric=${metric}`);
    } catch {
      const points = INITIAL_CAMERAS.map(c => ({
        latitude: c.latitude + (Math.random() - 0.5) * 0.005,
        longitude: c.longitude + (Math.random() - 0.5) * 0.005,
        intensity: Math.round(Math.random() * 80 + 20)
      }));
      return { data: { points, metric } };
    }
  },

  getODMatrix: async () => {
    try {
      return await api.get('/api/analytics/od-matrix');
    } catch {
      return {
        data: {
          zones: ['Raipur North', 'Raipur West', 'Raipur South', 'Raipur Central'],
          entries: [
            { origin_zone: 'Raipur North', destination_zone: 'Raipur West', vehicle_count: 120 },
            { origin_zone: 'Raipur West', destination_zone: 'Raipur South', vehicle_count: 95 },
            { origin_zone: 'Raipur South', destination_zone: 'Raipur Central', vehicle_count: 140 },
            { origin_zone: 'Raipur Central', destination_zone: 'Raipur North', vehicle_count: 85 },
          ],
          matrix: [
            [0, 120, 45, 80],
            [60, 0, 95, 40],
            [30, 70, 0, 140],
            [85, 50, 65, 0]
          ]
        }
      };
    }
  },

  getAlerts: async (params?: any) => {
    try {
      return await api.get('/api/alerts/', { params });
    } catch {
      return { data: { alerts: localAlerts, total: localAlerts.length } };
    }
  },

  updateAlertStatus: async (id: string, status: string) => {
    try {
      return await api.put(`/api/alerts/${id}/status`, { status });
    } catch {
      localAlerts = localAlerts.map(a => a.id === id ? { ...a, status: status as any } : a);
      return { data: { message: 'Alert updated' } };
    }
  },

  getWatchlist: async () => {
    try {
      return await api.get('/api/watchlist/');
    } catch {
      return { data: { entries: localWatchlist, total: localWatchlist.length } };
    }
  },

  addToWatchlist: async (data: any) => {
    try {
      return await api.post('/api/watchlist/', data);
    } catch {
      const newEntry: WatchlistEntry = {
        id: `w-${Date.now()}`,
        plate_number: data.plate_number.toUpperCase(),
        reason: data.reason,
        priority: data.priority || 'MEDIUM',
        status: 'ACTIVE',
        created_at: new Date().toISOString(),
      };
      localWatchlist = [newEntry, ...localWatchlist];
      return { data: newEntry };
    }
  },

  removeFromWatchlist: async (id: string) => {
    try {
      return await api.delete(`/api/watchlist/${id}`);
    } catch {
      localWatchlist = localWatchlist.filter(w => w.id !== id);
      return { data: { message: 'Removed' } };
    }
  },
};
