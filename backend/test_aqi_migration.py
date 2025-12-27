"""
Test script for Google Air Quality API integration.

Run this to verify the AQI service works correctly.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from services.aqi_service import AQIService
from core.config import settings


async def test_aqi_service():
    """Test the AQI service with various scenarios."""
    
    print("=" * 60)
    print("Google Air Quality API Integration Test")
    print("=" * 60)
    print()
    
    # Initialize service
    api_key = os.getenv("AIR_QUALITY_API_KEY") or settings.AIR_QUALITY_API_KEY
    service = AQIService(api_key)
    
    print(f"✓ Service initialized")
    print(f"  API Key: {'Set ✅' if api_key else 'Missing ❌'}")
    print(f"  Base URL: {service.base_url}")
    print()
    
    # Test 1: Mumbai coordinates
    print("Test 1: Mumbai (coordinates)")
    print("-" * 40)
    try:
        result = await service.get_aqi_by_location(19.0760, 72.8777)
        print(f"✓ Success!")
        print(f"  AQI: {result['aqi']}")
        print(f"  Quality: {result['quality']}")
        print(f"  Color: {result['color']}")
        print(f"  Category: {result['category']}")
        if 'dominant_pollutant' in result:
            print(f"  Dominant Pollutant: {result['dominant_pollutant']}")
        if 'cached' in result:
            print(f"  Cached: {result['cached']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
    
    # Test 2: City name (Mumbai)
    print("Test 2: Mumbai (city name)")
    print("-" * 40)
    try:
        result = await service.get_current_aqi(city="Mumbai")
        print(f"✓ Success!")
        print(f"  AQI: {result['aqi']}")
        print(f"  Quality: {result['quality']}")
        if 'cached' in result:
            print(f"  Cached: {result['cached']} (should be true on 2nd call)")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
    
    # Test 3: Delhi coordinates
    print("Test 3: Delhi (coordinates)")
    print("-" * 40)
    try:
        result = await service.get_aqi_by_location(28.7041, 77.1025)
        print(f"✓ Success!")
        print(f"  AQI: {result['aqi']}")
        print(f"  Quality: {result['quality']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
    
    # Test 4: Cache verification
    print("Test 4: Cache verification")
    print("-" * 40)
    try:
        # Call same location twice
        result1 = await service.get_aqi_by_location(19.0760, 72.8777)
        cached1 = result1.get('cached', False)
        
        result2 = await service.get_aqi_by_location(19.0760, 72.8777)
        cached2 = result2.get('cached', False)
        
        print(f"✓ First call cached: {cached1}")
        print(f"✓ Second call cached: {cached2}")
        print(f"  {'✅ Cache working!' if cached2 else '⚠️ Cache may not be working'}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
    
    # Test 5: Response structure validation
    print("Test 5: Response structure validation")
    print("-" * 40)
    try:
        result = await service.get_current_aqi(city="Mumbai")
        
        required_fields = ['aqi', 'quality', 'color', 'category', 'location', 'timestamp']
        optional_fields = ['dominant_pollutant', 'health_recommendations', 'cached']
        
        missing = [f for f in required_fields if f not in result]
        present_optional = [f for f in optional_fields if f in result]
        
        if missing:
            print(f"✗ Missing required fields: {missing}")
        else:
            print(f"✓ All required fields present")
        
        if present_optional:
            print(f"✓ Optional fields present: {present_optional}")
        
        print()
        print("Sample response:")
        print(f"  {result}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
    
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run tests
    asyncio.run(test_aqi_service())
