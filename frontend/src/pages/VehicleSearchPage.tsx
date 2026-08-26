import { useState, useEffect } from 'react';
import { apiService } from '../lib/api';
import { Trajectory, Detection } from '../types';
import { Search, Route, Clock, Navigation, Zap } from 'lucide-react';
import MapView from '../components/MapView';
import DetectionCard from '../components/DetectionCard';
import { formatDistance, formatDate, formatSpeed } from '../lib/utils';

const SUGGESTED_PLATES = ['UP14BN4001', 'CG04AB1234', 'MH02AB1234', 'DL01CD5678', 'KA03EF9012'];

export default function VehicleSearchPage() {
  const [plate, setPlate] = useState('UP14BN4001');
  const [loading, setLoading] = useState(false);
  const [trajectory, setTrajectory] = useState<Trajectory | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [error, setError] = useState('');

  const executeSearch = async (targetPlate: string) => {
    const query = targetPlate.toUpperCase().trim();
    if (!query) return;

    setLoading(true);
    setError('');
    setTrajectory(null);
    setDetections([]);

    try {
      const [trajRes, detRes] = await Promise.all([
        apiService.getVehicleTrajectory(query).catch(() => ({ data: null })),
        apiService.getVehicleDetections(query).catch(() => ({ data: [] }))
      ]);

      if (!trajRes.data && (!detRes.data || detRes.data.length === 0)) {
        setError(`No historical detections found for plate ${query}.`);
      } else {
        setTrajectory(trajRes.data);
        setDetections(detRes.data || []);
      }
    } catch {
      setError('An error occurred while fetching trajectory records.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Auto-search default plate on mount
    executeSearch('UP14BN4001');
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch(plate);
  };

  const handleChipClick = (p: string) => {
    setPlate(p);
    executeSearch(p);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-slate-100">Vehicle Search & Trajectory Tracking</h1>
        <p className="text-slate-400">Search for any vehicle by license plate number to reconstruct its multi-camera trajectory and timeline.</p>
      </div>

      <div className="space-y-3">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="relative flex-1 max-w-xl">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
            <input
              type="text"
              value={plate}
              onChange={(e) => setPlate(e.target.value.toUpperCase())}
              placeholder="ENTER PLATE NUMBER (e.g. UP14BN4001)"
              className="w-full bg-surface border border-slate-700 rounded-xl py-3 pl-12 pr-4 text-slate-100 font-mono text-lg focus:outline-none focus:border-primary-500 transition-colors uppercase placeholder:normal-case placeholder:font-sans placeholder:text-base"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !plate.trim()}
            className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-xl font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            <Search size={18} />
            {loading ? 'Tracking...' : 'Search'}
          </button>
        </form>

        {/* Quick Suggestion Chips */}
        <div className="flex items-center gap-2 flex-wrap text-xs text-slate-400">
          <span className="flex items-center gap-1"><Zap size={14} className="text-amber-400" /> Quick Samples:</span>
          {SUGGESTED_PLATES.map(p => (
            <button
              key={p}
              type="button"
              onClick={() => handleChipClick(p)}
              className={`px-2.5 py-1 rounded-lg border font-mono transition-colors ${
                plate === p 
                  ? 'bg-primary-600/20 border-primary-500 text-primary-400' 
                  : 'bg-slate-800 border-slate-700 hover:border-slate-600 text-slate-300'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl">
          {error}
        </div>
      )}

      {trajectory && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-surface rounded-xl border border-slate-700/50 p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-slate-200 flex items-center gap-2">
                <Route size={20} className="text-primary-400" /> Multi-Camera Trajectory Map
              </h2>
              <span className="text-xs px-2.5 py-1 rounded bg-primary-500/10 text-primary-400 border border-primary-500/20 font-mono">
                {trajectory.plate_number}
              </span>
            </div>
            <MapView 
              trajectory={trajectory} 
              height="500px" 
              center={trajectory.points.length > 0 ? [trajectory.points[0].latitude, trajectory.points[0].longitude] : [21.2514, 81.6296]} 
              zoom={13} 
            />
          </div>

          <div className="space-y-6">
            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Trip Summary</h2>
              <div className="space-y-4 text-sm">
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Clock size={16}/> Active Window</span>
                  <span className="font-medium text-slate-200">
                    {formatDate(trajectory.start_time, 'HH:mm')} - {formatDate(trajectory.end_time, 'HH:mm')}
                  </span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Navigation size={16}/> Total Distance</span>
                  <span className="font-medium text-slate-200">{formatDistance(trajectory.distance)}</span>
                </div>
                <div className="flex justify-between items-center pb-3 border-b border-slate-800">
                  <span className="text-slate-400 flex items-center gap-2"><Search size={16}/> Cameras Passed</span>
                  <span className="font-medium text-slate-200">{trajectory.camera_count} Nodes</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 flex items-center gap-2"><Clock size={16}/> Average Speed</span>
                  <span className="font-medium text-slate-200">{formatSpeed(trajectory.average_speed)}</span>
                </div>
              </div>
            </div>

            <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
              <h2 className="text-lg font-semibold mb-4 text-slate-200">Camera Observation Timeline</h2>
              <div className="relative border-l-2 border-slate-700 ml-3 space-y-6">
                {trajectory.points.map((pt, idx) => (
                  <div key={idx} className="relative pl-6">
                    <div className="absolute w-3 h-3 bg-primary-500 rounded-full -left-[7px] top-1.5 ring-4 ring-surface" />
                    <div className="flex justify-between items-start">
                      <p className="font-medium text-slate-200 text-sm">{pt.camera_name}</p>
                      <span className="text-xs text-emerald-400 font-mono">{(pt.ocr_confidence * 100).toFixed(0)}% OCR</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{formatDate(pt.timestamp)}</p>
                    <p className="text-xs text-slate-500 mt-1">Speed: {pt.speed} km/h • Direction: {pt.direction}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {detections.length > 0 && (
        <div className="bg-surface rounded-xl border border-slate-700/50 p-5">
          <h2 className="text-lg font-semibold mb-4 text-slate-200">Camera Detection Log ({detections.length})</h2>
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
