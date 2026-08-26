import { Detection } from '../types';
import { formatDate } from '../lib/utils';
import { Camera, Clock, Activity, Gauge } from 'lucide-react';

export default function DetectionCard({ detection }: { detection: Detection }) {
  const confColor = detection.confidence > 90 ? 'text-emerald-400' : detection.confidence > 70 ? 'text-amber-400' : 'text-red-400';

  return (
    <div className="bg-surface border border-slate-700/50 p-4 rounded-xl hover:border-primary-500/50 transition-colors cursor-pointer">
      <div className="flex justify-between items-start mb-3">
        <div className="px-3 py-1 bg-slate-900 border border-slate-700 rounded text-lg font-mono font-bold tracking-widest text-slate-100">
          {detection.plate_number}
        </div>
        <span className={`text-sm font-semibold ${confColor}`}>{detection.confidence}%</span>
      </div>
      
      <div className="space-y-2 text-sm text-slate-400">
        <div className="flex items-center gap-2">
          <Camera size={14} />
          <span className="truncate">{detection.camera?.name || detection.camera_id}</span>
        </div>
        <div className="flex items-center gap-2">
          <Clock size={14} />
          <span>{formatDate(detection.timestamp)}</span>
        </div>
        {(detection.speed || detection.vehicle_type) && (
          <div className="flex items-center gap-4 mt-2 pt-2 border-t border-slate-700/50">
            {detection.vehicle_type && (
              <div className="flex items-center gap-1.5">
                <Activity size={14} />
                <span className="capitalize">{detection.vehicle_type.toLowerCase()}</span>
              </div>
            )}
            {detection.speed && (
              <div className="flex items-center gap-1.5">
                <Gauge size={14} />
                <span>{Math.round(detection.speed)} km/h</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
