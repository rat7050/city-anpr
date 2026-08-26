import { useEffect, useState } from 'react';
import { apiService } from '../lib/api';
import { wsManager } from '../lib/websocket';
import { TrafficStats, Camera, Detection, Alert } from '../types';
import StatsCard from '../components/StatsCard';
import MapView from '../components/MapView';
import TrafficChart from '../components/TrafficChart';
import DetectionCard from '../components/DetectionCard';
import AlertBanner from '../components/AlertBanner';
import { Car, Camera as CameraIcon, Activity, AlertTriangle, Gauge } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState<TrafficStats | null>(null);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [recentDetections, setRecentDetections] = useState<Detection[]>([]);
  const [vehiclesByHour, setVehiclesByHour] = useState<any>(null);
  const [liveAlert, setLiveAlert] = useState<Alert | null>(null);

  const fetchData = async () => {
    try {
      const [statsRes, camRes, detRes, vbhRes] = await Promise.all([
        apiService.getTrafficStats(),
        apiService.getCameras(),
        apiService.getRecentDetections(),
        apiService.getVehiclesByHour()
      ]);
      setStats(statsRes.data);
      setCameras(camRes.data.cameras || camRes.data); // Adjust depending on response format
      setRecentDetections(detRes.data);
      
      const vbh = Array.isArray(vbhRes.data) ? vbhRes.data : [];
      setVehiclesByHour({
        labels: vbh.map((d: any) => `${d.hour}:00`),
        datasets: [{ label: 'Vehicles', data: vbh.map((d: any) => d.count), color: '#3b82f6' }]
      });
    } catch (err) {
      console.error('Error fetching dashboard data', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);

    const unsubDet = wsManager.onMessage('NEW_DETECTION', (det: Detection) => {
      setRecentDetections(prev => [det, ...prev].slice(0, 20));
      setStats(prev => prev ? { ...prev, total_detections: prev.total_detections + 1 } : null);
    });

    const unsubAlert = wsManager.onMessage('NEW_ALERT', (alert: Alert) => {
      setLiveAlert(alert);
      setStats(prev => prev ? { ...prev, active_alerts: prev.active_alerts + 1 } : null);
    });

    return () => {
      clearInterval(interval);
      unsubDet();
      unsubAlert();
    };
  }, []);

  return (
    <div className="p-6 space-y-6">
      {liveAlert && <AlertBanner alert={liveAlert} onDismiss={() => setLiveAlert(null)} />}
      
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-100">Live Dashboard</h1>
        <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-400/10 px-3 py-1.5 rounded-full">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          System Online
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatsCard title="Total Vehicles Today" value={stats.total_vehicles.toLocaleString()} icon={Car} color="primary" />
          <StatsCard title="Active Cameras" value={`${stats.active_cameras} / ${cameras.length}`} icon={CameraIcon} color="emerald" />
          <StatsCard title="Total Detections" value={stats.total_detections.toLocaleString()} icon={Activity} color="blue" />
          <StatsCard title="Average Speed" value={`${Math.round(stats.average_speed)} km/h`} icon={Gauge} color="amber" />
          <StatsCard title="Active Alerts" value={stats.active_alerts} icon={AlertTriangle} color="red" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-surface rounded-xl border border-slate-700/50 p-4">
            <h2 className="text-lg font-semibold mb-4 text-slate-200">Network Map</h2>
            <MapView cameras={cameras} height="400px" />
          </div>
          <div className="bg-surface rounded-xl border border-slate-700/50 p-4">
            <h2 className="text-lg font-semibold mb-4 text-slate-200">Traffic Volume (24h)</h2>
            {vehiclesByHour && <TrafficChart type="line" data={vehiclesByHour} height="250px" />}
          </div>
        </div>

        <div className="bg-surface rounded-xl border border-slate-700/50 p-4 flex flex-col h-full">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-slate-200">Live Detections</h2>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar" style={{ maxHeight: '720px' }}>
            {recentDetections.map(det => (
              <DetectionCard key={det.id} detection={det} />
            ))}
            {recentDetections.length === 0 && (
              <div className="text-center text-slate-500 py-10">No recent detections</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
