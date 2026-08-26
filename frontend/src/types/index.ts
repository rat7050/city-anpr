export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: string;
  username: string;
}

export interface Camera {
  id: string;
  name: string;
  road: string;
  zone: string;
  latitude: number;
  longitude: number;
  status: 'ONLINE' | 'OFFLINE' | 'MAINTENANCE';
  last_heartbeat: string;
  detection_count?: number;
}

export interface Vehicle {
  id: string;
  plate_number: string;
  vehicle_type: string;
  color: string;
  first_seen: string;
  last_seen: string;
  detection_count: number;
}

export interface Detection {
  id: string;
  camera_id: string;
  plate_number: string;
  timestamp: string;
  confidence: number;
  vehicle_type?: string;
  speed?: number;
  direction?: string;
  image_url?: string;
  camera?: Camera;
}

export interface TrajectoryPoint {
  camera_id: string;
  camera_name: string;
  latitude: number;
  longitude: number;
  timestamp: string;
  ocr_confidence: number;
}

export interface Trajectory {
  id: string;
  vehicle_id: string;
  plate_number: string;
  start_time: string;
  end_time: string;
  distance: number;
  average_speed: number;
  camera_count: number;
  points: TrajectoryPoint[];
  route_geojson: any;
}

export interface Alert {
  id: string;
  alert_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  plate_number: string;
  camera_id: string;
  message: string;
  timestamp: string;
  status: 'ACTIVE' | 'ACKNOWLEDGED' | 'RESOLVED' | 'DISMISSED';
  camera?: Camera;
}

export interface WatchlistEntry {
  id: string;
  plate_number: string;
  reason: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'ACTIVE' | 'INACTIVE';
  created_at: string;
}

export interface TrafficStats {
  total_vehicles: number;
  active_cameras: number;
  total_detections: number;
  average_speed: number;
  congestion_level: string;
  active_alerts: number;
}

export interface HeatmapPoint {
  latitude: number;
  longitude: number;
  intensity: number;
}
