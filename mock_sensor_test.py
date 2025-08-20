#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Mock Sensor Test

This script tests the mock sensors for development on non-Raspberry Pi systems.
It demonstrates how to use the mock sensors to simulate real sensor data.
"""

import os
import time
from datetime import datetime

# Set environment variable to use mock sensors
os.environ['USE_MOCK_SENSORS'] = 'true'

# Now import from sensors package, which will use mock sensors
from sensors import DHT22Sensor, BMP280Sensor

def test_mock_sensors():
    """Test the mock sensors by taking multiple readings."""
    print("Raspberry Pi Weather Station - Mock Sensor Test")
    print("==============================================\n")
    
    # Initialize mock sensors
    dht = DHT22Sensor(pin=4)
    bmp = BMP280Sensor(i2c_addr=0x76)
    
    print("Taking 5 readings at 2-second intervals...\n")
    
    for i in range(1, 6):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Read DHT22 sensor
        dht_temp, humidity = dht.read()
        
        # Read BMP280 sensor
        bmp_temp, pressure, altitude = bmp.read()
        
        # Display readings
        print(f"Reading #{i} at {timestamp}:")
        
        if dht_temp is not None and humidity is not None:
            print(f"  DHT22: {dht_temp:.1f}°C, {humidity:.1f}%")
        else:
            print("  DHT22: Reading failed (simulated error)")
        
        if bmp_temp is not None and pressure is not None and altitude is not None:
            print(f"  BMP280: {bmp_temp:.1f}°C, {pressure:.2f}hPa, {altitude:.2f}m")
        else:
            print("  BMP280: Reading failed (simulated error)")
        
        print("-" * 50)
        
        # Wait before next reading
        if i < 5:
            time.sleep(2)
    
    print("\nMock sensor test completed successfully.")
    print("You can now run the full weather station with mock sensors:")
    print("  python run_weather_station.py")

if __name__ == "__main__":
    test_mock_sensors()