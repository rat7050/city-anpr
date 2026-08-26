import { useEffect, useState } from 'react';
import { apiService } from '../lib/api';
import TrafficChart from '../components/TrafficChart';
import MapView from '../components/MapView';
import { HeatmapPoint } from '../types';

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<'flow' | 'heatmap'>('flow');
  const [vehiclesByHour, setVehiclesByHour] = useState<any>(null);
  const [vehiclesByZone, setVehiclesByZone] = useState<any>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapPoint[]>([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [vbhRes, vbzRes, heatRes] = await Promise.all([
        apiService.getVehiclesByHour(),
        apiService.getVehiclesByZone(),
        apiService.getHeatmap()
      ]);
      
      const vbh = Array.isArray(vbhRes.data) ? vbhRes.data : [];
      setVehiclesByHour({
        labels: vbh.map((d: any) => `${d.hour}:00`),
        datasets: [{ label: 'Vehicles', data: vbh.map((d: any) => d.count), color: '#3b82f6' }]
      });

      const vbz = Array.isArray(vbzRes.data) ? vbzRes.data : [];
      setVehiclesByZone(vbz.map((d: any) => ({ name: d.zone, value: d.count })));

      setHeatmapData(heatRes.data.points || []);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6 h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Traffic Analytics</h1>
        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
          <button onClick={() => setActiveTab('flow')} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'flow' ? 'bg-surface text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>Flow & Volumes</button>
          <button onClick={() => setActiveTab('heatmap')} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${activeTab === 'heatmap' ? 'bg-surface text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}>Density Heatmap</button>
        </div>
      </div>

      <div className="flex-1">
        {activeTab === 'flow' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Volume by Hour</h2>
              {vehiclesByHour && <TrafficChart type="line" data={vehiclesByHour} height="350px" />}
            </div>
            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Volume by Zone</h2>
              {vehiclesByZone && <TrafficChart type="pie" data={vehiclesByZone} height="350px" />}
            </div>
          </div>
        )}

        {activeTab === 'heatmap' && (
          <div className="bg-surface rounded-xl border border-slate-700/50 p-4 h-[calc(100vh-140px)]">
            <MapView heatmapData={heatmapData} height="100%" />
          </div>
        )}
      </div>
    </div>
  );
}
