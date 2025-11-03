import requests
import os
from typing import List, Dict, Any
import json

TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")

def optimize_route(locations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Optimize route using TomTom Routing API.
    locations: List of dictionaries containing location data and modifiers
    """
    if not TOMTOM_API_KEY:
        raise ValueError("TOMTOM_API_KEY environment variable not set")

    # Format locations for TomTom API
    waypoints = []
    for loc in locations:
        lat, lon = loc['coords']
        waypoints.append({
            "point": {
                "latitude": lat,
                "longitude": lon
            },
            "timeWindow": {
                "start": "2024-01-01T09:00:00Z",  # Example time window
                "end": "2024-01-01T17:00:00Z"
            }
        })

    # Prepare request body
    request_body = {
        "vehicleCapacity": 1000,  # Example capacity
        "arrivalWindow": {
            "start": "2024-01-01T09:00:00Z",
            "end": "2024-01-01T17:00:00Z"
        },
        "waypoints": waypoints,
        "options": {
            "traffic": "live"
        }
    }

    try:
        response = requests.post(
            f"https://api.tomtom.com/routing/1/vrp?key={TOMTOM_API_KEY}",
            json=request_body
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Transform TomTom response into our format
        optimized_route = {
            "route": [],
            "total_distance": result.get("summary", {}).get("distance", 0),
            "total_time": result.get("summary", {}).get("time", 0)
        }
        
        # Extract ordered waypoints
        for stop in result.get("routes", [{}])[0].get("stops", []):
            point = stop.get("point", {})
            optimized_route["route"].append({
                "lat": point.get("latitude"),
                "lon": point.get("longitude"),
                "arrival_time": stop.get("arrival")
            })
        
        return optimized_route
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"TomTom API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Route optimization error: {str(e)}")