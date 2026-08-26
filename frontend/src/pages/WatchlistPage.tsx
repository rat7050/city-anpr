import { useEffect, useState } from 'react';
import { apiService } from '../lib/api';
import { WatchlistEntry } from '../types';
import { formatDate } from '../lib/utils';
import { Plus, Trash2, Shield } from 'lucide-react';

export default function WatchlistPage() {
  const [entries, setEntries] = useState<WatchlistEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPlate, setNewPlate] = useState('');
  const [newReason, setNewReason] = useState('');
  const [newPriority, setNewPriority] = useState('MEDIUM');

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const fetchWatchlist = async () => {
    try {
      const res = await apiService.getWatchlist();
      setEntries(res.data.entries || res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiService.addToWatchlist({
        plate_number: newPlate,
        reason: newReason,
        priority: newPriority
      });
      setNewPlate('');
      setNewReason('');
      fetchWatchlist();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Remove this vehicle from watchlist?')) return;
    try {
      await apiService.removeFromWatchlist(id);
      setEntries(entries.filter(e => e.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-3">
          <Shield className="text-primary-500" /> Vehicle Watchlist
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-surface rounded-xl border border-slate-700/50 p-5 h-fit">
          <h2 className="text-lg font-semibold mb-4 text-slate-200">Add to Watchlist</h2>
          <form onSubmit={handleAdd} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Plate Number</label>
              <input type="text" required value={newPlate} onChange={e => setNewPlate(e.target.value.toUpperCase())} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:border-primary-500 uppercase" placeholder="e.g. MH12AB1234" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Priority</label>
              <select value={newPriority} onChange={e => setNewPriority(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:border-primary-500">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1.5">Reason / Notes</label>
              <textarea required value={newReason} onChange={e => setNewReason(e.target.value)} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-slate-100 focus:border-primary-500 min-h-[100px]" placeholder="Reason for adding to watchlist..." />
            </div>
            <button type="submit" className="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 rounded-lg transition-colors flex items-center justify-center gap-2">
              <Plus size={18} /> Add Vehicle
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 bg-surface rounded-xl border border-slate-700/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-400">
              <thead className="text-xs text-slate-400 uppercase bg-slate-900/50 border-b border-slate-700/50">
                <tr>
                  <th className="px-6 py-4">Plate Number</th>
                  <th className="px-6 py-4">Priority</th>
                  <th className="px-6 py-4">Reason</th>
                  <th className="px-6 py-4">Added On</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {entries.map(entry => (
                  <tr key={entry.id} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4 font-mono font-bold text-slate-200">{entry.plate_number}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${entry.priority === 'HIGH' || entry.priority === 'CRITICAL' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : entry.priority === 'MEDIUM' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}>
                        {entry.priority}
                      </span>
                    </td>
                    <td className="px-6 py-4 max-w-[200px] truncate" title={entry.reason}>{entry.reason}</td>
                    <td className="px-6 py-4 text-xs">{formatDate(entry.created_at)}</td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => handleDelete(entry.id)} className="p-2 hover:bg-red-500/10 text-slate-400 hover:text-red-400 rounded transition-colors">
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {entries.length === 0 && !loading && (
                  <tr>
                    <td colSpan={5} className="px-6 py-10 text-center text-slate-500">Watchlist is empty</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
