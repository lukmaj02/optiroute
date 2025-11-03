from fastapi import FastAPI, HTTPException
import requests
import os
from typing import Dict, Any

app = FastAPI()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")

def get_weather_data(city: str) -> Dict[str, Any]:
    """Get weather data from OpenWeatherMap API"""
    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "q": city,
                "appid": OPENWEATHERMAP_API_KEY,
                "units": "metric"
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Calculate weather modifier based on conditions
        modifier = 1.0
        
        # Adjust for precipitation
        if "rain" in data:
            modifier *= 1.2  # 20% slower in rain
        if "snow" in data:
            modifier *= 1.3  # 30% slower in snow
            
        # Adjust for wind
        wind_speed = data.get("wind", {}).get("speed", 0)
        if wind_speed > 10:  # m/s
            modifier *= 1.1  # 10% slower in strong wind
            
        return {
            "conditions": data.get("weather", [{}])[0].get("main", "Unknown"),
            "modifier": modifier
        }
    except Exception as e:
        print(f"Weather API error: {str(e)}")
        return {"conditions": "Unknown", "modifier": 1.0}

def get_air_quality(city: str) -> Dict[str, Any]:
    """Get air quality data from OpenAQ API"""
    try:
        response = requests.get(
            "https://api.openaq.org/v2/latest",
            params={
                "city": city,
                "parameter": ["pm25", "pm10"],
                "limit": 1
            },
            headers={
                "X-API-Key": OPENAQ_API_KEY
            }
        )
        response.raise_for_status()
        data = response.json()
        
        # Calculate air quality modifier
        modifier = 1.0
        measurements = data.get("results", [{}])[0].get("measurements", [])
        
        for measurement in measurements:
            if measurement["parameter"] == "pm25" and measurement["value"] > 50:
                modifier *= 1.1  # 10% slower in poor air quality
            if measurement["parameter"] == "pm10" and measurement["value"] > 100:
                modifier *= 1.15  # 15% slower in very poor air quality
                
        return {
            "air_quality": "Poor" if modifier > 1.0 else "Good",
            "modifier": modifier
        }
    except Exception as e:
        print(f"Air Quality API error: {str(e)}")
        return {"air_quality": "Unknown", "modifier": 1.0}

@app.get("/api/v1/environment")
async def get_environment_data(city: str) -> Dict[str, Any]:
    """Get aggregated environmental data for a city"""
    if not city:
        raise HTTPException(status_code=400, detail="City parameter is required")
        
    weather_data = get_weather_data(city)
    air_quality_data = get_air_quality(city)
    
    # Combine modifiers
    total_modifier = weather_data["modifier"] * air_quality_data["modifier"]
    
    return {
        "weather_modifier": weather_data["modifier"],
        "conditions": weather_data["conditions"],
        "air_quality_modifier": air_quality_data["modifier"],
        "air_quality": air_quality_data["air_quality"],
        "total_modifier": total_modifier
    }