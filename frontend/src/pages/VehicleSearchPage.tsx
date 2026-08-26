import { useState } from 'react';
import { apiService } from '../lib/api';
import { Trajectory, Detection } from '../types';
import { Search, Route, Clock, Navigation } from 'lucide-react';
import MapView from '../components/MapView';
import DetectionCard from '../components/DetectionCard';
import { formatDistance, formatDate, formatSpeed } from '../lib/utils';

export default function VehicleSearchPage() {
  const [plate, setPlate] = useState('');
  const [loading, setLoading] = useState(false);
  const [trajectory, setTrajectory] = useState<Trajectory | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plate.trim()) return;
    
    setLoading(true);
    setError('');
    setTrajectory(null);
    setDetections([]);

    try {
      const [trajRes, detRes] = await Promise.all([
        apiService.getVehicleTrajectory(plate).catch(() => ({ data: null })),
        apiService.getVehicleDetections(plate).catch(() => ({ data: [] }))
      ]);

      if (!trajRes.data && detRes.data.length === 0) {
        setError('No records found for this plate number.');
      } else {
        setTrajectory(trajRes.data);
        setDetections(detRes.data);
      }
    } catch (err) {
      setError('An error occurred while searching.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-slate-100">Vehicle Search</h1>
        <p className="text-slate-400">Search for vehicles by plate number to view their history and trajectory.</p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-4">
        <div className="relative flex-1 max-w-xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
          <input
            type="text"
            value={plate}
            onChange={(e) => setPlate(e.target.value.toUpperCase())}
            placeholder="ENTER PLATE NUMBER (e.g. MH12AB1234)"
            className="w-full bg-surface border border-slate-700 rounded-xl py-3 pl-12 pr-4 text-slate-100 font-mono text-lg focus:outline-none focus:border-primary-500 transition-colors uppercase placeholder:normal-case placeholder:font-sans placeholder:text-base"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !plate.trim()}
          className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-xl font-medium transition-colors disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl">
          {error}
        </div>
      )}

      {trajectory && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-surface rounded-xl border border-slate-700/50 p-4">
            <h2 className="text-lg font-semibold mb-4 text-slate-200 flex items-center gap-2"><Route size={20}/> Trajectory Map</h2>
            <MapView trajectory={trajectory} height="500px" center={trajectory.points.length > 0 ? [trajectory.points[0].latitude, trajectory.points[0].longitude] : undefined} zoom={13} />
          </div>

          <div className="space-y-6">
            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Trip Summary</h2>
              <div className="space-y-4 text-sm">
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Clock size={16}/> Duration</span>
                  <span className="font-medium text-slate-200">
                    {formatDate(trajectory.start_time, 'HH:mm')} - {formatDate(trajectory.end_time, 'HH:mm')}
                  </span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Navigation size={16}/> Distance</span>
                  <span className="font-medium text-slate-200">{formatDistance(trajectory.distance)}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Search size={16}/> Cameras Passed</span>
                  <span className="font-medium text-slate-200">{trajectory.camera_count}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 flex items-center gap-2"><Clock size={16}/> Avg Speed</span>
                  <span className="font-medium text-slate-200">{formatSpeed(trajectory.average_speed)}</span>
                </div>
              </div>
            </div>

            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Camera Timeline</h2>
              <div className="relative border-l-2 border-slate-700 ml-3 space-y-6">
                {trajectory.points.map((pt, idx) => (
                  <div key={idx} className="relative pl-6">
                    <div className="absolute w-3 h-3 bg-primary-500 rounded-full -left-[7px] top-1.5 ring-4 ring-surface" />
                    <p className="font-medium text-slate-200 text-sm">{pt.camera_name}</p>
                    <p className="text-xs text-slate-400 mt-1">{formatDate(pt.timestamp)}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {detections.length > 0 && (
        <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
          <h2 className="text-lg font-semibold mb-4 text-slate-200">All Detections</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {detections.map(det => (
              <DetectionCard key={det.id} detection={det} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
