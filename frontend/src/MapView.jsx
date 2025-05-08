import React from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon path
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
});

const MapView = ({ mission, currentIndex }) => {
  if (!mission || mission.length === 0) return null;

  // Filter only waypoints with valid coordinates
  const validWaypoints = mission.filter(
    wp => typeof wp.lat === 'number' && typeof wp.lng === 'number'
  );

  if (validWaypoints.length === 0) return null;

  const center = [validWaypoints[0].lat, validWaypoints[0].lng];

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ marginBottom: '0.5rem' }}>Mission Map</h3>
      <MapContainer center={center} zoom={16} style={{ height: "400px", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        <Polyline
          positions={validWaypoints.map(wp => [wp.lat, wp.lng])}
          color="blue"
        />

        {validWaypoints.map((wp, index) => (
          <Marker key={index} position={[wp.lat, wp.lng]}>
            <Popup>
              {wp.name}
              {index === currentIndex ? " (Current)" : ""}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default MapView;
