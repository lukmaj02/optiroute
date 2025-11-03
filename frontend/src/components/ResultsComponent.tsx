import MapComponent from './MapComponent';


interface ResultsProps {
  data: any; // Typ dowolny, ponieważ struktura może się różnić (błąd/sukces)
}

interface GeocodedStop {
  address: string;
  lat?: number;
  lon?: number;
  error?: string;
}

interface RouteSummary {
  lengthInMeters: number;
  travelTimeInSeconds: number;
  departureTime: string;
  arrivalTime: string;
}

interface OptimizationResult {
  optimizedOrder: number[];
  summary: {
    routeSummary: RouteSummary;
  };
}

function formatTime(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);

  let parts = [];
  if (hours > 0) {
    parts.push(`${hours} godz.`);
  }
  if (minutes > 0 || parts.length === 0) {
    parts.push(`${minutes} minut`);
  }
  return parts.join(' ');
}

function formatDistance(totalMeters: number): string {
  const kilometers = totalMeters / 1000;
  return `${kilometers.toFixed(2)} km`;
}

function ResultsComponent({ data }: ResultsProps) {
  
  // Scenariusz błędu (bez zmian)
  if (data.error) {
    return (
      <div>
        <h2 className="text-2xl font-semibold text-red-600 mb-4">
          Wystąpił błąd
        </h2>
        <p className="mb-2">Otrzymane dane z backendu:</p>
        <pre className="bg-gray-900 text-red-400 p-4 rounded-md overflow-x-auto">
          {data.error}
        </pre>
      </div>
    );
  }

  // Scenariusz sukcesu (bez zmian)
  const { geocoding_summary, optimization_result } = data;
  const resultData: OptimizationResult = optimization_result;

  if (!geocoding_summary || !resultData || !resultData.summary || !resultData.summary.routeSummary) {
    return <p>Otrzymano niekompletne dane z serwera.</p>;
  }

  const originalAddresses: GeocodedStop[] = geocoding_summary;
  const optimizedOrder: number[] = resultData.optimizedOrder;
  const summary: RouteSummary = resultData.summary.routeSummary;

  const sortedAddresses: GeocodedStop[] = optimizedOrder.map(index => {
    return originalAddresses[index];
  });
  
  // --- BRAKUJĄCA ZMIENNA ---
  // Filtrujemy listę przystanków, aby na mapie pokazać tylko te,
  // które mają poprawne współrzędne (lat/lon)
  const mapStops = sortedAddresses.filter(
    (stop): stop is { address: string; lat: number; lon: number } => 
      stop.lat !== undefined && stop.lon !== undefined
  );

  return (
    <div>
      <h2 className="text-2xl font-semibold text-green-600 mb-4">
        {data.message || 'Zlecenie Ukończone!'}
      </h2>
      
      <div className="bg-gray-900 p-4 rounded-md mb-6">
        <h3 className="text-xl font-medium text-white mb-3">
          Podsumowanie Trasy
        </h3>
        <div className="flex justify-around text-center">
          <div>
            {/* Poprawiłem też lekko etykiety dla jasności */}
            <span className="text-sm text-gray-400 block">Całkowity Czas: </span>
            <span className="text-2xl font-bold text-green-500">
              {formatTime(summary.travelTimeInSeconds)}
            </span>
          </div>
          <div>
            <span className="text-sm text-gray-400 block">Całkowity Dystans: </span>
            <span className="text-2xl font-bold text-green-500">
              {formatDistance(summary.lengthInMeters)}
            </span>
          </div>
        </div>
      </div>
      
      {/* Mapa z przystankami */}
      <div className="w-full mb-6" style={{ height: '400px' }}>
          <MapComponent stops={mapStops} />
      </div>
      {}
      
      <h3 className="text-xl font-medium text-white mb-3">
        Zoptymalizowana kolejność przystanków:
      </h3>
      
      <ol className="list-decimal list-inside bg-gray-900 p-4 rounded-md space-y-2">
        {sortedAddresses.map((stop, index) => (
          <li key={index} className="text-lg text-gray-200">
            {stop.address}
            {stop.error && (
              <span className="text-sm text-red-500 ml-2">({stop.error})</span>
            )}
          </li>
        ))}
      </ol>

      <details className="mt-6">
        <summary className="cursor-pointer text-gray-400">
          Pokaż pełną odpowiedź JSON z backendu
        </summary>
        <pre className="bg-gray-950 text-white p-4 rounded-md overflow-x-auto mt-2 text-sm">
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
      
    </div>
  );
}

export default ResultsComponent;