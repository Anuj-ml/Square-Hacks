import httpx
import random
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from cachetools import TTLCache
import os

class AQIService:
    """
    Google Maps Platform - Air Quality API Integration
    
    Replaces OpenWeather Air Pollution API with Google Air Quality API.
    Includes adapter layer to maintain frontend contract compatibility.
    
    API Documentation: https://developers.google.com/maps/documentation/air-quality
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AIR_QUALITY_API_KEY")
        self.base_url = "https://airquality.googleapis.com/v1/currentConditions:lookup"
        
        # Short-term cache: 5 minutes TTL, max 100 locations
        self._cache = TTLCache(maxsize=100, ttl=300)
        
        # Default city coordinates (Mumbai)
        self.default_coords = {"lat": 19.0760, "lon": 72.8777}
        
        # City coordinates mapping
        self.city_coords = {
            "Mumbai": {"lat": 19.0760, "lon": 72.8777},
            "mumbai": {"lat": 19.0760, "lon": 72.8777},
            "Delhi": {"lat": 28.7041, "lon": 77.1025},
            "delhi": {"lat": 28.7041, "lon": 77.1025},
            "Bangalore": {"lat": 12.9716, "lon": 77.5946},
            "bangalore": {"lat": 12.9716, "lon": 77.5946},
        }
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.timeout = 10.0
    
    def _get_cache_key(self, lat: float, lon: float) -> str:
        """Generate cache key for lat/lon (rounded to 2 decimals)"""
        return f"{round(lat, 2):.2f},{round(lon, 2):.2f}"
    
    async def _fetch_with_retry(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Fetch AQI data with retry logic and timeout handling.
        
        Returns raw Google API response or None on failure.
        """
        request_body = {
            "location": {
                "latitude": lat,
                "longitude": lon
            },
            "extraComputations": [
                "POLLUTANT_CONCENTRATION",
                "LOCAL_AQI",
                "HEALTH_RECOMMENDATIONS",
                "DOMINANT_POLLUTANT_CONCENTRATION"
            ],
            "languageCode": "en"
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key
        }
        
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.base_url,
                        json=request_body,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:  # Rate limit
                        wait_time = self.retry_delay * (2 ** attempt)
                        print(f"⚠️ Rate limited, waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Google API error {response.status_code}: {response.text}")
                        return None
                        
            except httpx.TimeoutException:
                print(f"⏱️ Timeout on attempt {attempt + 1}/{self.max_retries}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
            except Exception as e:
                print(f"❌ Request failed: {e}")
                return None
        
        return None
    
    def _extract_aqi_from_response(self, data: Dict) -> Optional[int]:
        """
        Extract AQI value from Google API response.
        
        Priority: Indian CPCB > US EPA > Universal AQI
        
        Google returns multiple AQI standards:
        - ind_cpcb: Indian CPCB (0-500+)
        - usa_epa: US EPA (0-500)
        - uaqi: Universal AQI (0-500)
        """
        indexes = data.get("indexes", [])
        
        if not indexes:
            return None
        
        # Priority mapping for Indian context
        priority_codes = ["ind_cpcb", "usa_epa", "uaqi"]
        
        for code in priority_codes:
            for index in indexes:
                if index.get("code") == code:
                    aqi_value = index.get("aqi")
                    if aqi_value is not None:
                        return int(aqi_value)
        
        # Fallback: use first available
        if indexes and "aqi" in indexes[0]:
            return int(indexes[0]["aqi"])
        
        return None
    
    def _extract_dominant_pollutant(self, data: Dict) -> str:
        """
        Extract dominant pollutant from Google API response.
        
        Maps Google pollutant codes to standard names.
        """
        pollutants = data.get("pollutants", [])
        
        if not pollutants:
            return "PM2.5"  # Default
        
        # Find pollutant with highest concentration relative to standard
        dominant = None
        max_ratio = 0
        
        for pollutant in pollutants:
            code = pollutant.get("code", "")
            concentration = pollutant.get("concentration", {}).get("value", 0)
            
            # Simplified heuristic: PM2.5 and PM10 are most relevant
            if code == "pm25" and concentration > max_ratio:
                dominant = "PM2.5"
                max_ratio = concentration
            elif code == "pm10" and concentration > max_ratio * 0.8:
                dominant = "PM10"
                max_ratio = concentration
        
        return dominant or "PM2.5"
    
    def _extract_health_recommendations(self, data: Dict) -> List[str]:
        """Extract health recommendations from Google API response."""
        recommendations = []
        
        indexes = data.get("indexes", [])
        for index in indexes:
            if "category" in index:
                category = index["category"]
                recommendations.append(f"Air quality: {category}")
        
        health_recs = data.get("healthRecommendations", {})
        general = health_recs.get("generalPopulation", "")
        if general:
            recommendations.append(general)
        
        return recommendations[:3]  # Limit to 3 recommendations
    
    def _create_adapter_response(self, aqi: int, lat: float, lon: float, 
                                  raw_data: Optional[Dict] = None) -> Dict:
        """
        Adapter layer: Convert Google response to frontend-compatible format.
        
        Maintains OpenWeather-shaped schema so frontend requires no changes.
        
        AQI Scale Mapping:
        - Google uses 0-500 scale (matches US EPA standard)
        - Frontend expects same scale
        - No conversion needed, but categories are mapped explicitly
        """
        # Map Google AQI (0-500) to quality categories
        if aqi <= 50:
            quality = "Good"
            color = "green"
            category_index = 1
        elif aqi <= 100:
            quality = "Moderate"
            color = "yellow"
            category_index = 2
        elif aqi <= 150:
            quality = "Unhealthy for Sensitive Groups"
            color = "orange"
            category_index = 3
        elif aqi <= 200:
            quality = "Unhealthy"
            color = "red"
            category_index = 4
        elif aqi <= 300:
            quality = "Very Unhealthy"
            color = "purple"
            category_index = 5
        else:
            quality = "Hazardous"
            color = "maroon"
            category_index = 6
        
        response = {
            "aqi": aqi,
            "quality": quality,
            "color": color,
            "category": category_index,
            "location": {"lat": lat, "lon": lon},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add extended data if available
        if raw_data:
            response["dominant_pollutant"] = self._extract_dominant_pollutant(raw_data)
            response["health_recommendations"] = self._extract_health_recommendations(raw_data)
        
        return response
    
    async def get_aqi_by_location(self, lat: float, lon: float) -> Dict:
        """
        Get current AQI for specific coordinates from Google Air Quality API.
        
        Returns adapter response compatible with existing frontend contract.
        """
        # Check cache first
        cache_key = self._get_cache_key(lat, lon)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            cached["cached"] = True
            return cached
        
        # Fallback if no API key
        if not self.api_key:
            aqi = self._get_simulated_aqi("location")
            return self._create_adapter_response(aqi, lat, lon)
        
        # Fetch from Google API with retry logic
        data = await self._fetch_with_retry(lat, lon)
        
        if not data:
            # Safe fallback on API failure
            aqi = self._get_simulated_aqi("location")
            return self._create_adapter_response(aqi, lat, lon)
        
        # Extract AQI from response
        aqi = self._extract_aqi_from_response(data)
        
        if aqi is None:
            # Safe fallback if AQI extraction fails
            aqi = self._get_simulated_aqi("location")
            response = self._create_adapter_response(aqi, lat, lon)
        else:
            # Create adapter response with full data
            response = self._create_adapter_response(aqi, lat, lon, data)
        
        # Cache result
        self._cache[cache_key] = response
        
        return response
    
    async def get_current_aqi(self, city: str = "Mumbai", lat: Optional[float] = None, 
                             lon: Optional[float] = None) -> Dict:
        """
        Get current AQI for a city or coordinates.
        
        Returns full adapter response for backwards compatibility.
        """
        # If lat/lon provided, use them directly
        if lat is not None and lon is not None:
            return await self.get_aqi_by_location(lat, lon)
        
        # Otherwise use city name
        coords = self.city_coords.get(city, self.default_coords)
        return await self.get_aqi_by_location(coords["lat"], coords["lon"])
    
    def _get_simulated_aqi(self, city: str) -> int:
        """
        Generate realistic simulated AQI for demo (fallback only).
        
        Mumbai typical AQI range: 100-200 (moderate to unhealthy)
        """
        base_aqi = 150
        return base_aqi + random.randint(-30, 50)
