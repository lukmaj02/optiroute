import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import { type LatLngExpression, LatLngBounds } from 'leaflet';

interface MapPoint {
  address: string;
  lat: number;
  lon: number;
}

interface GeometryPoint {
  latitude: number;
  longitude: number;
}

interface MapProps {
  stops: MapPoint[]; 
  geometry: GeometryPoint[] | null; 
}

function FitMapToBounds({ bounds }: { bounds: LatLngBounds }) {
  const map = useMap();
  useEffect(() => {
    map.invalidateSize();
    map.fitBounds(bounds, { padding: [50, 50] });
  }, [map, bounds]);
  return null;
}

function MapComponent({ stops, geometry }: MapProps) {
  

  const routeLine: LatLngExpression[] = geometry 
    ? geometry.map(p => [p.latitude, p.longitude])
    : []; 


  const markerPositions: LatLngExpression[] = stops.map(stop => [stop.lat, stop.lon]);


  const boundsPoints = routeLine.length > 0 ? routeLine : markerPositions;
  
  if (boundsPoints.length === 0) {
    return <div>Brak danych do wyświetlenia na mapie.</div>;
  }

  const bounds = new LatLngBounds(boundsPoints);

  return (
    <MapContainer 
      center={[51.107, 17.038]}
      zoom={13} 
      scrollWheelZoom={true} 
      style={{ height: '100%', width: '100%', borderRadius: '0.375rem' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {/* Linia trasy  */}
      <Polyline 
        pathOptions={{ color: '#34D399', weight: 5 }} 
        positions={routeLine.length > 0 ? routeLine : markerPositions} 
      />

      {/* Markery  */}
      {stops.map((stop, index) => (
        <Marker key={index} position={[stop.lat, stop.lon]}>
          <Popup>
            <div className="font-sans">
              <strong className="text-base block">Przystanek {index + 1}</strong>
              {stop.address}
            </div>
          </Popup>
        </Marker>
      ))}

      <FitMapToBounds bounds={bounds} />
    </MapContainer>
  );
}

export default MapComponent;