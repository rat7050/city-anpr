import { useEffect, useState } from 'react';
import { apiService } from '../lib/api';
import { Alert } from '../types';
import { getAlertColor, formatDate } from '../lib/utils';
import { AlertTriangle, Check, X, ShieldAlert } from 'lucide-react';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const res = await apiService.getAlerts();
      setAlerts(res.data.alerts || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (id: string, status: string) => {
    try {
      await apiService.updateAlertStatus(id, status);
      setAlerts(alerts.map(a => a.id === id ? { ...a, status: status as any } : a));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
          <ShieldAlert className="text-red-500" /> System Alerts
        </h1>
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-400">Loading alerts...</div>
      ) : (
        <div className="space-y-4">
          {alerts.map(alert => (
            <div key={alert.id} className={`bg-surface border p-5 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4 ${getAlertColor(alert.severity)}`}>
              <div className="flex items-start gap-4">
                <div className="mt-1"><AlertTriangle size={20} /></div>
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="font-bold">{alert.alert_type}</h3>
                    <span className="text-xs px-2 py-0.5 rounded-full border bg-black/20 font-medium">
                      {alert.severity}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full border bg-black/20 font-medium">
                      {alert.status}
                    </span>
                  </div>
                  <p className="text-sm opacity-90">{alert.message}</p>
                  <div className="flex gap-4 mt-2 text-xs opacity-75 font-mono">
                    <span>PLATE: {alert.plate_number}</span>
                    <span>CAM: {alert.camera?.name || alert.camera_id}</span>
                    <span>TIME: {formatDate(alert.timestamp)}</span>
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2 shrink-0">
                {alert.status === 'ACTIVE' && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'ACKNOWLEDGED')} className="px-3 py-1.5 bg-black/20 hover:bg-black/40 rounded-lg text-sm font-medium transition-colors flex items-center gap-1">
                    <Check size={14} /> Acknowledge
                  </button>
                )}
                {(alert.status === 'ACTIVE' || alert.status === 'ACKNOWLEDGED') && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'RESOLVED')} className="px-3 py-1.5 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 rounded-lg text-sm font-medium transition-colors flex items-center gap-1">
                    <Check size={14} /> Resolve
                  </button>
                )}
                {alert.status !== 'DISMISSED' && alert.status !== 'RESOLVED' && (
                  <button onClick={() => handleStatusUpdate(alert.id, 'DISMISSED')} className="px-3 py-1.5 bg-black/20 hover:bg-black/40 rounded-lg text-sm font-medium transition-colors flex items-center gap-1">
                    <X size={14} /> Dismiss
                  </button>
                )}
              </div>
            </div>
          ))}
          {alerts.length === 0 && (
            <div className="text-center py-10 text-slate-400 bg-surface rounded-xl border border-slate-700/50">
              No alerts found.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
