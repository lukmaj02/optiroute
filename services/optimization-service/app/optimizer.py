import httpx
import os
from typing import List, Dict, Any, Optional

# Adresy URL (bez zmian)
TOMTOM_OPTIMIZATION_URL = "https://api.tomtom.com/routing/waypointoptimization/1"
TOMTOM_ROUTING_URL = "https://api.tomtom.com/routing/1/calculateRoute"

def format_waypoints_for_optimization(stops: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Konwertuje przystanki na format dla 'Waypoint Optimization API'
    (oczekuje {"point": {...}})
    """
    locations = []
    for stop in stops:
        if "lat" in stop and "lon" in stop:
            locations.append({
                "point": {
                    "latitude": stop["lat"],
                    "longitude": stop["lon"]
                }
            })
    return locations

def format_waypoints_for_routing_url(stops: List[Dict[str, Any]]) -> str:
    """
    Konwertuje listę przystanków na JEDEN string w formacie:
    lat,lon:lat,lon:lat,lon
    """
    points = []
    for stop in stops:
        if "lat" in stop and "lon" in stop:
            points.append(f"{stop['lat']},{stop['lon']}")
    return ":".join(points) 

def get_route_geometry(job_id: str, api_key: str, sorted_stops: List[Dict[str, Any]]) -> (Dict[str, Any], List[Dict[str, Any]]):
    """
    DRUGIE ZAPYTANIE: Pobiera geometrię trasy (kształt ulic) za pomocą 'Routing API'.
    """
    print(f"[{job_id}] Wykonywanie drugiego zapytania (Routing API) o geometrię trasy...", flush=True)

    locations_string = format_waypoints_for_routing_url(sorted_stops)
    
    route_type = "fastest"
    travel_mode = "car"
    
    url = (
        f"{TOMTOM_ROUTING_URL}/{locations_string}/json?"
        f"key={api_key}&"
        f"routeType={route_type}&"
        f"travelMode={travel_mode}&"
        f"traffic=true"
    )


    print(f"[{job_id}] Wysyłanie zapytania GET po geometrię...", flush=True)

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url) 
            response.raise_for_status()
            data = response.json()
            
            routes = data.get("routes")
            if not routes:
                raise ValueError("Odpowiedź z Routing API nie zawiera klucza 'routes'.")
                
            summary = routes[0].get("summary")
            
            geometry = []
            for leg in routes[0].get("legs", []):
                geometry.extend(leg.get("points", []))
                
            if not summary or not geometry:
                raise ValueError("Odpowiedź z Routing API nie zawiera 'summary' lub 'legs[...].points'.")

            print(f"[{job_id}] Pomyślnie pobrano geometrię trasy (liczba punktów: {len(geometry)}).", flush=True)
            return summary, geometry

    except httpx.HTTPStatusError as e:
        print(f"[{job_id}] BŁĄD KRYTYCZNY (Zapytanie 2 - Geometria): {e.response.status_code}", flush=True)
        print(f"[{job_id}] Odpowiedź błędu: {e.response.text}", flush=True)
        return None, None
    except Exception as e:
        print(f"[{job_id}] BŁĄD KRYTYCZNY (Zapytanie 2 - Geometria): {e}", flush=True)
        return None, None


def optimize_route_with_tomtom(job_id: str, stops: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Główna funkcja: wykonuje 2 zapytania (optymalizacja + rysowanie trasy).
    """
    api_key = os.getenv("TOMTOM_API_KEY")
    if not api_key or api_key == "TWOJ_KLUCZ_API_WKLEJ_TUTAJ":
        print(f"[{job_id}] BŁĄD: Brak klucza TOMTOM_API_KEY w zmiennych środowiskowych.", flush=True)
        raise ValueError("Brak klucza TOMTOM_API_KEY. Sprawdź docker-compose.yml")

    if len(stops) < 2:
        print(f"[{job_id}] Błąd: Zbyt mało poprawnych punktów do optymalizacji ({len(stops)}).", flush=True)
        return {"error": "Zbyt mało poprawnych punktów do optymalizacji (wymagane min. 2)."}

    # --- ZAPYTANIE 1: Optymalizacja Kolejności ---
    print(f"[{job_id}] Wysyłanie {len(stops)} punktów do TomTom API (Waypoint Optimization)...", flush=True)
    
    opti_url = f"{TOMTOM_OPTIMIZATION_URL}?key={api_key}"
    opti_payload = {
        "waypoints": format_waypoints_for_optimization(stops),
        "options": {
            "travelMode": "car",
            "traffic": "live",
            "departAt": "now",
            "waypointConstraints": {
                "originIndex": -1,
                "destinationIndex": -1
            },
            "outputExtensions": ["travelTimes", "routeLengths"]
        }
    }

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(opti_url, json=opti_payload)
            response.raise_for_status()
            opti_data = response.json()
            
            print(f"[{job_id}] Otrzymano pomyślną odpowiedź z TomTom (Zapytanie 1).", flush=True)

    except httpx.HTTPStatusError as e:
        print(f"[{job_id}] BŁĄD KRYTYCZNY (Zapytanie 1 - Optymalizacja): {e.response.status_code}", flush=True)
        print(f"[{job_id}] Odpowiedź błędu: {e.response.text}", flush=True)
        raise ValueError(f"Błąd TomTom API (Optymalizacja): {e.response.text}")
    except Exception as e:
        print(f"[{job_id}] BŁĄD KRYTYCZNY (Zapytanie 1 - Optymalizacja): {e}", flush=True)
        raise ValueError(f"Nieoczekiwany błąd podczas optymalizacji: {e}")

    # --- Przetwarzanie odpowiedzi z Zapytania 1 ---
    optimized_order = opti_data.get("optimizedOrder")
    if optimized_order is None:
        raise ValueError("Odpowiedź z Waypoint Optimization API nie zawiera klucza 'optimizedOrder'.")

    sorted_stops = [stops[i] for i in optimized_order]

    # --- ZAPYTANIE 2: Pobranie Geometrii Trasy ---
    (route_summary, route_geometry) = get_route_geometry(job_id, api_key, sorted_stops)
    # --- Łączenie wyników obu zapytań ---
    final_summary = opti_data.get("summary", {}).get("routeSummary", {})
    
    
    if not final_summary and route_summary:
        final_summary = route_summary
    
    final_result = {
        "optimizedOrder": optimized_order,
        "summary": final_summary,
        "geometry": route_geometry 
    }
    
    return final_result