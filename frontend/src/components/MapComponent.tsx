// --- NOWY IMPORT ---
import { useEffect } from 'react';
// --- KONIEC IMPORTU ---

import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from 'react-leaflet';
import { type LatLngExpression, LatLngBounds } from 'leaflet';

// Definiujemy typ dla naszych punktów
interface MapPoint {
  address: string;
  lat: number;
  lon: number;
}

interface MapProps {
  stops: MapPoint[]; // Oczekujemy listy poprawnie zgeokodowanych przystanków
}

/**
 * Komponent pomocniczy, który automatycznie dopasowuje widok mapy
 * tak, aby wszystkie markery były widoczne.
 */
function FitMapToBounds({ bounds }: { bounds: LatLngBounds }) {
  const map = useMap();

  // --- ZMIENIONA LOGIKA ---
  // Używamy useEffect, aby mieć pewność, że ten kod uruchomi się
  // PO tym, jak div mapy uzyska już swoje wymiary (h-96 z Tailwind).
  useEffect(() => {
    // 1. To jest kluczowa komenda: zmusza mapę do ponownego
    //    sprawdzenia rozmiaru swojego kontenera.
    map.invalidateSize();
    
    // 2. Dopiero teraz bezpiecznie dopasowujemy widok.
    map.fitBounds(bounds, { padding: [50, 50] });
  }, [map, bounds]); // Uruchom ponownie, jeśli zmieni się mapa lub granice
  // --- KONIEC ZMIAN ---

  return null;
}

function MapComponent({ stops }: MapProps) {
  if (stops.length === 0) {
    return <div>Brak danych do wyświetlenia na mapie.</div>;
  }

  // Tworzymy listę współrzędnych dla linii (Polyline)
  const positions: LatLngExpression[] = stops.map(stop => [stop.lat, stop.lon]);

  // Obliczamy granice mapy, aby wycentrować widok
  const bounds = new LatLngBounds(positions);

  return (
    <MapContainer 
      center={[51.107, 17.038]} // Domyślne centrum (Wrocław), na wszelki wypadek
      zoom={13} 
      scrollWheelZoom={true} 
      style={{ height: '100%', width: '100%', borderRadius: '0.375rem' }}
    >
      {/* Używamy darmowych kafelków mapy z OpenStreetMap */}
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* Rysujemy linię łączącą wszystkie punkty */}
      <Polyline pathOptions={{ color: '#34D399', weight: 5 }} positions={positions} />

      {/* Dodajemy marker dla każdego przystanku */}
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

      {/* Komponent do automatycznego centrowania mapy */}
      <FitMapToBounds bounds={bounds} />
    </MapContainer>
  );
}

export default MapComponent;