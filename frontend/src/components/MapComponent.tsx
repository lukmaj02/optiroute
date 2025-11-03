import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface Location {
  lat: number;
  lon: number;
  arrival_time?: string;
}

interface MapComponentProps {
  locations: Location[];
}

export const MapComponent: React.FC<MapComponentProps> = ({ locations }) => {
  const mapRef = useRef<L.Map | null>(null);

  useEffect(() => {
    if (mapRef.current && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map(loc => [loc.lat, loc.lon]));
      mapRef.current.fitBounds(bounds);
    }
  }, [locations]);

  if (locations.length === 0) {
    return <div>No route data available</div>;
  }

  const positions = locations.map(loc => [loc.lat, loc.lon] as [number, number]);

  return (
    <MapContainer
      ref={mapRef}
      center={[locations[0].lat, locations[0].lon]}
      zoom={13}
      style={{ height: '500px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {locations.map((loc, index) => (
        <Marker
          key={index}
          position={[loc.lat, loc.lon]}
          title={`Stop ${index + 1}${loc.arrival_time ? ` - ${loc.arrival_time}` : ''}`}
        />
      ))}
      <Polyline
        positions={positions}
        color="blue"
        weight={3}
        opacity={0.7}
      />
    </MapContainer>
  );
};