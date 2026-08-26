import { Camera, Trajectory, Detection, TrafficStats, WatchlistEntry, Alert } from '../types';

export const INITIAL_CAMERAS: Camera[] = [
  {
    id: 'cam-01',
    name: 'C01 - VIP Road',
    road: 'VIP Road',
    zone: 'Raipur North',
    latitude: 21.2514,
    longitude: 81.6296,
    status: 'ONLINE',
    last_heartbeat: new Date().toISOString(),
    detection_count: 342,
  },
  {
    id: 'cam-08',
    name: 'C08 - Ring Road',
    road: 'Ring Road',
    zone: 'Raipur West',
    latitude: 21.2350,
    longitude: 81.6100,
    status: 'ONLINE',
    last_heartbeat: new Date().toISOString(),
    detection_count: 289,
  },
  {
    id: 'cam-15',
    name: 'C15 - GE Road',
    road: 'GE Road',
    zone: 'Raipur South',
    latitude: 21.2200,
    longitude: 81.5950,
    status: 'ONLINE',
    last_heartbeat: new Date().toISOString(),
    detection_count: 412,
  },
  {
    id: 'cam-22',
    name: 'C22 - Pandri Main Road',
    road: 'Pandri',
    zone: 'Raipur Central',
    latitude: 21.2100,
    longitude: 81.6350,
    status: 'ONLINE',
    last_heartbeat: new Date().toISOString(),
    detection_count: 198,
  },
  {
    id: 'cam-29',
    name: 'C29 - Airport Expressway',
    road: 'Expressway',
    zone: 'Raipur East',
    latitude: 21.2380,
    longitude: 81.6700,
    status: 'ONLINE',
    last_heartbeat: new Date().toISOString(),
    detection_count: 245,
  }
];

export const INITIAL_WATCHLIST: WatchlistEntry[] = [
  {
    id: 'w-1',
    plate_number: 'CG04AB1234',
    reason: 'Stolen vehicle reported under FIR-294/2026',
    priority: 'HIGH',
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 3600000 * 24).toISOString(),
  },
  {
    id: 'w-2',
    plate_number: 'UP14BN4001',
    reason: 'Speed violation & unpaid toll corridor alert',
    priority: 'CRITICAL',
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 3600000 * 12).toISOString(),
  },
  {
    id: 'w-3',
    plate_number: 'MH02AB1234',
    reason: 'Commercial permit expired - check at checkpoint',
    priority: 'MEDIUM',
    status: 'ACTIVE',
    created_at: new Date(Date.now() - 3600000 * 48).toISOString(),
  }
];

export const INITIAL_ALERTS: Alert[] = [
  {
    id: 'alt-1',
    alert_type: 'WATCHLIST_MATCH',
    severity: 'HIGH',
    plate_number: 'CG04AB1234',
    camera_id: 'cam-01',
    message: 'Watchlist vehicle CG04AB1234 detected on VIP Road (Confidence: 98%)',
    timestamp: new Date(Date.now() - 15 * 60000).toISOString(),
    status: 'ACTIVE',
  },
  {
    id: 'alt-2',
    alert_type: 'SPEED_ANOMALY',
    severity: 'CRITICAL',
    plate_number: 'UP14BN4001',
    camera_id: 'cam-08',
    message: 'Vehicle UP14BN4001 exceeded speed limit (88.4 km/h in 50 km/h zone)',
    timestamp: new Date(Date.now() - 32 * 60000).toISOString(),
    status: 'ACTIVE',
  },
  {
    id: 'alt-3',
    alert_type: 'ROUTE_ANOMALY',
    severity: 'MEDIUM',
    plate_number: 'MH02AB1234',
    camera_id: 'cam-15',
    message: 'Unusual corridor transition sequence detected for MH02AB1234',
    timestamp: new Date(Date.now() - 75 * 60000).toISOString(),
    status: 'ACKNOWLEDGED',
  }
];

// Helper to generate realistic multi-camera trajectory for any plate
export function generateTrajectoryForPlate(plateNumber: string): { trajectory: Trajectory; detections: Detection[] } {
  const normPlate = plateNumber.toUpperCase().trim();
  const now = Date.now();
  
  // Pick sequence of cameras based on plate hash
  const numCams = 4;
  const cams = INITIAL_CAMERAS.slice(0, numCams);
  
  const points = cams.map((cam, idx) => {
    const timeOffset = (numCams - 1 - idx) * 18 * 60000; // 18 mins apart
    return {
      camera_id: cam.id,
      camera_name: cam.name,
      latitude: cam.latitude,
      longitude: cam.longitude,
      timestamp: new Date(now - timeOffset).toISOString(),
      ocr_confidence: Math.round((0.92 + Math.random() * 0.07) * 100) / 100,
      direction: idx % 2 === 0 ? 'NORTH' : 'EAST',
      speed: Math.round((42 + Math.random() * 20) * 10) / 10
    };
  });

  const startTime = points[0].timestamp;
  const endTime = points[points.length - 1].timestamp;
  const distance = 11.8;
  const averageSpeed = 52.4;

  const trajectory: Trajectory = {
    id: `traj-${normPlate}`,
    vehicle_id: `veh-${normPlate}`,
    plate_number: normPlate,
    start_time: startTime,
    end_time: endTime,
    distance,
    average_speed: averageSpeed,
    camera_count: points.length,
    points,
    route_geojson: {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: points.map(p => [p.longitude, p.latitude])
      }
    }
  };

  const detections: Detection[] = points.map((p, idx) => ({
    id: `det-${normPlate}-${idx}`,
    camera_id: p.camera_id,
    plate_number: normPlate,
    timestamp: p.timestamp,
    confidence: p.ocr_confidence,
    vehicle_type: normPlate.startsWith('CG') ? 'CAR' : normPlate.startsWith('UP') ? 'SUV' : 'SEDAN',
    speed: p.speed,
    direction: p.direction,
    camera: cams.find(c => c.id === p.camera_id)
  }));

  return { trajectory, detections };
}

export const INITIAL_STATS: TrafficStats = {
  total_vehicles: 1840,
  active_cameras: 5,
  total_detections: 4290,
  average_speed: 48.6,
  congestion_level: 'MODERATE',
  active_alerts: 3
};
