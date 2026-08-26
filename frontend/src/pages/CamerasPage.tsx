import { useEffect, useState } from 'react';
import { apiService } from '../lib/api';
import { Camera } from '../types';
import { formatDate } from '../lib/utils';
import { Map, Video, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import MapView from '../components/MapView';

export default function CamerasPage() {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState<'table' | 'map'>('table');

  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      const res = await apiService.getCameras();
      setCameras(res.data.cameras || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    if (status === 'ONLINE') return <CheckCircle2 size={16} className="text-emerald-500" />;
    if (status === 'OFFLINE') return <XCircle size={16} className="text-red-500" />;
    return <AlertCircle size={16} className="text-amber-500" />;
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Camera Management</h1>
        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700">
          <button 
            onClick={() => setView('table')} 
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${view === 'table' ? 'bg-surface text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            List View
          </button>
          <button 
            onClick={() => setView('map')} 
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${view === 'map' ? 'bg-surface text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Map size={16} /> Map View
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-400">Loading cameras...</div>
      ) : view === 'map' ? (
        <div className="bg-surface rounded-xl border border-slate-700/50 p-4 h-[700px]">
          <MapView cameras={cameras} height="100%" />
        </div>
      ) : (
        <div className="bg-surface rounded-xl border border-slate-700/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-400">
              <thead className="text-xs text-slate-400 uppercase bg-slate-900/50 border-b border-slate-700/50">
                <tr>
                  <th className="px-6 py-4">Camera Name</th>
                  <th className="px-6 py-4">Location</th>
                  <th className="px-6 py-4">Zone</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Last Heartbeat</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {cameras.map(camera => (
                  <tr key={camera.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-200 flex items-center gap-3">
                      <div className="p-2 bg-slate-900 rounded border border-slate-700"><Video size={16} /></div>
                      {camera.name}
                    </td>
                    <td className="px-6 py-4">{camera.road}</td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700 text-xs">
                        {camera.zone}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(camera.status)}
                        <span className={camera.status === 'ONLINE' ? 'text-emerald-400' : camera.status === 'OFFLINE' ? 'text-red-400' : 'text-amber-400'}>
                          {camera.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{formatDate(camera.last_heartbeat)}</td>
                    <td className="px-6 py-4 text-right">
                      <button className="text-primary-400 hover:text-primary-300 font-medium text-xs uppercase tracking-wider">
                        View Details
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
