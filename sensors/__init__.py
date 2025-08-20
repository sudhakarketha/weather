# Raspberry Pi Weather Station - Sensors Package

import os
import sys

# Check if we're using mock sensors
USE_MOCK_SENSORS = os.environ.get('USE_MOCK_SENSORS', 'false').lower() == 'true'

# Import appropriate sensor modules based on environment
if USE_MOCK_SENSORS:
    # For development on non-Raspberry Pi systems
    try:
        from .mock_sensors import MockDHT22Sensor as DHT22Sensor
        from .mock_sensors import MockBMP280Sensor as BMP280Sensor
        print("Using mock sensors for development")
    except ImportError as e:
        print(f"Error importing mock sensors: {e}")
        sys.exit(1)
else:
    # For production on Raspberry Pi
    try:
        from .dht22 import DHT22Sensor
        from .bmp280 import BMP280Sensor
    except ImportError as e:
        print(f"Error importing sensor modules: {e}")
        print("If you're on a non-Raspberry Pi system, set USE_MOCK_SENSORS=true")
        print("You can do this by running: python run_weather_station.py")
        sys.exit(1)

# Export sensor classes
__all__ = ['DHT22Sensor', 'BMP280Sensor']