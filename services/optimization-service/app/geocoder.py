import requests
from typing import Optional, Tuple
import time

def get_coords(address: str) -> Optional[Tuple[float, float]]:
    """
    Get coordinates from Nominatim (OpenStreetMap) for a given address.
    Includes rate limiting to comply with Nominatim usage policy.
    """
    try:
        # Rate limiting - Nominatim requires max 1 request per second
        time.sleep(1)
        
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": address,
                "format": "json",
                "limit": 1
            },
            headers={"User-Agent": "OptiRoute/1.0"}
        )
        response.raise_for_status()
        
        results = response.json()
        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            return (lat, lon)
        return None
    
    except Exception as e:
        print(f"Error geocoding address {address}: {str(e)}")
        return None