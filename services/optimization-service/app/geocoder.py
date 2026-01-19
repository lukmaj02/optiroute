import httpx
import time
import os
import json
import redis
from typing import Optional, Tuple

# URL do API Nominatim
NOMINATIM_API_URL = "https://nominatim.openstreetmap.org/search"
# Nominatim wymaga, abyśmy się przedstawili (User-Agent). Wpisz tu nazwę swojego projektu.
HEADERS = {"User-Agent": "OptiRoute-Project (wwada-studia)"}

# Redis cache
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis_client = redis.from_url(REDIS_URL) 

def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Zamienia adres tekstowy na współrzędne (latitude, longitude)
    używając API Nominatim z cache Redis.

    Zwraca (lat, lon) lub None, jeśli się nie uda.
    """
    cache_key = f"geocode:{address}"
    
    # Sprawdź cache
    cached = redis_client.get(cache_key)
    if cached:
        try:
            data = json.loads(cached)
            if data:
                return (data[0], data[1])
            else:
                return None
        except json.JSONDecodeError:
            pass  # Kontynuuj do API
    
    params = {
        'q': address,
        'format': 'json',
        'limit': 1
    }
    
    try:
        with httpx.Client(headers=HEADERS) as client:
            response = client.get(NOMINATIM_API_URL, params=params, timeout=10.0)
            
            # Rzuć błędem, jeśli API zwróciło 4xx lub 5xx
            response.raise_for_status() 
            
            data = response.json()
            
            if data:
                # Zwróć (latitude, longitude)
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                # Zapisz do cache na 24 godziny
                redis_client.setex(cache_key, 86400, json.dumps([lat, lon]))
                return (lat, lon)
            else:
                # Nie znaleziono adresu, zapisz None do cache
                redis_client.setex(cache_key, 86400, json.dumps(None))
                return None

    except httpx.HTTPStatusError as e:
        print(f"Błąd HTTP podczas geokodowania '{address}': {e.response.status_code}")
        return None
    except Exception as e:
        print(f"Nieoczekiwany błąd podczas geokodowania '{address}': {e}")
        return None

if __name__ == '__main__':
    # Szybki test, który możesz uruchomić ręcznie (jeśli chcesz)
    addr = "Krakowska 1, Wrocław"
    coords = geocode_address(addr)
    print(f"Adres: {addr}\nWspółrzędne: {coords}")
    
    time.sleep(1) # Czekamy 1s (polityka Nominatim)
    
    addr = "Nieistniejący Adres 12345"
    coords = geocode_address(addr)
    print(f"Adres: {addr}\nWspółrzędne: {coords}")
