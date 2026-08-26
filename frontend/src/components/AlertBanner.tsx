import { AlertTriangle, X } from 'lucide-react';
import { Alert } from '../types';
import { getAlertColor, formatDate } from '../lib/utils';
import { useEffect, useState } from 'react';

export default function AlertBanner({ alert, onDismiss }: { alert: Alert, onDismiss: () => void }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(true);
    const timer = setTimeout(() => {
      setVisible(false);
      setTimeout(onDismiss, 300); // Wait for transition
    }, 10000);
    return () => clearTimeout(timer);
  }, [alert, onDismiss]);

  return (
    <div className={`fixed top-4 right-4 z-50 max-w-md w-full transition-all duration-300 transform ${visible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
      <div className={`p-4 rounded-xl border backdrop-blur-sm shadow-xl flex items-start gap-3 ${getAlertColor(alert.severity)}`}>
        <AlertTriangle className="shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="font-bold text-sm">{alert.alert_type} - {alert.severity}</h4>
          <p className="text-sm mt-1 opacity-90">{alert.message}</p>
          <div className="flex justify-between items-center mt-2 text-xs opacity-80 font-mono">
            <span>Plate: {alert.plate_number}</span>
            <span>{formatDate(alert.timestamp, 'HH:mm:ss')}</span>
          </div>
        </div>
        <button onClick={() => setVisible(false)} className="opacity-70 hover:opacity-100">
          <X size={18} />
        </button>
      </div>
    </div>
  );
}
