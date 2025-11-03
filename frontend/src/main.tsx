import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// 1. Importujemy globalnie CSS (to jest poprawne)
import 'leaflet/dist/leaflet.css'; 

// --- OSTATECZNA POPRAWKA IKON LEAFLET ---
import L from 'leaflet'; // Importujemy całą bibliotekę Leaflet jako 'L'

// 2. Ręcznie importujemy ścieżki do obrazów
import markerIconUrl from 'leaflet/dist/images/marker-icon.png';
import markerIconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import markerShadowUrl from 'leaflet/dist/images/marker-shadow.png';

// 3. Usuwamy starą, wadliwą konfigurację domyślną
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;

// 4. Tworzymy nową, kompletną definicję ikony
const DefaultIcon = L.icon({
    iconUrl: markerIconUrl,
    iconRetinaUrl: markerIconRetinaUrl,
    shadowUrl: markerShadowUrl,
    iconSize: [25, 41], // Domyślny rozmiar ikony
    iconAnchor: [12, 41], // Punkt, w którym ikona "dotyka" mapy
    popupAnchor: [1, -34], // Gdzie ma się pojawiać popup
    tooltipAnchor: [16, -28],
    shadowSize: [41, 41] // Rozmiar cienia
});

// 5. Ustawiamy naszą nową ikonę jako domyślną dla wszystkich markerów
L.Marker.prototype.options.icon = DefaultIcon;
// --- KONIEC POPRAWKI ---

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)