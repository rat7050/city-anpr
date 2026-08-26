import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import { Camera, Trajectory, HeatmapPoint, Detection } from '../types';
import { formatDate } from '../lib/utils';

interface MapViewProps {
  cameras?: Camera[];
  detections?: Detection[];
  trajectory?: Trajectory;
  heatmapData?: HeatmapPoint[];
  center?: [number, number];
  zoom?: number;
  height?: string;
}

const createIcon = (color: string) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const icons = {
  ONLINE: createIcon('green'),
  OFFLINE: createIcon('red'),
  MAINTENANCE: createIcon('yellow'),
  DETECTION: createIcon('blue')
};

const HeatmapLayer = ({ points }: { points: HeatmapPoint[] }) => {
  const map = useMap();
  useEffect(() => {
    if (!points || points.length === 0) return;
    const data = points.map(p => [p.latitude, p.longitude, p.intensity]);
    const layer = (L as any).heatLayer(data, { radius: 25, blur: 15, maxZoom: 17 }).addTo(map);
    return () => { map.removeLayer(layer); };
  }, [map, points]);
  return null;
};

export default function MapView({ cameras = [], detections = [], trajectory, heatmapData, center = [40.7128, -74.0060], zoom = 12, height = "400px" }: MapViewProps) {
  return (
    <div style={{ height }} className="w-full rounded-xl overflow-hidden border border-slate-700/50 z-0 relative">
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />
        
        {cameras.map(camera => (
          <Marker key={camera.id} position={[camera.latitude, camera.longitude]} icon={icons[camera.status]}>
            <Popup className="dark-popup">
              <div className="p-1">
                <h3 className="font-bold text-slate-800">{camera.name}</h3>
                <p className="text-sm text-slate-600">{camera.road} • {camera.zone}</p>
                <p className="text-sm text-slate-600 mt-1">Status: <span className="font-semibold">{camera.status}</span></p>
              </div>
            </Popup>
          </Marker>
        ))}

        {detections.map(det => det.camera && (
          <Marker key={det.id} position={[det.camera.latitude, det.camera.longitude]} icon={icons.DETECTION}>
            <Popup>
              <div className="p-1">
                <h3 className="font-bold text-slate-800">{det.plate_number}</h3>
                <p className="text-sm text-slate-600">{formatDate(det.timestamp)}</p>
                <p className="text-sm text-slate-600">Camera: {det.camera.name}</p>
              </div>
            </Popup>
          </Marker>
        ))}

        {trajectory && trajectory.points.length > 0 && (
          <Polyline 
            positions={trajectory.points.map(p => [p.latitude, p.longitude])}
            color="#3b82f6" 
            weight={4} 
            dashArray="10, 10" 
          />
        )}

        {heatmapData && heatmapData.length > 0 && <HeatmapLayer points={heatmapData} />}
      </MapContainer>
    </div>
  );
}
