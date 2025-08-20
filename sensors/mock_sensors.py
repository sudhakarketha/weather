"""Mock sensor modules for development on non-Raspberry Pi systems.

This module provides mock implementations of the DHT22 and BMP280 sensors
for development and testing on systems where the actual hardware and
Raspberry Pi specific libraries are not available.
"""

import time
import random
from datetime import datetime


class MockDHT22Sensor:
    """Mock implementation of the DHT22 temperature and humidity sensor."""
    
    def __init__(self, pin):
        """Initialize the mock DHT22 sensor.
        
        Args:
            pin: The GPIO pin number (ignored in mock implementation)
        """
        self.pin = pin
        self.last_read_time = 0
        self.min_interval = 2  # Minimum seconds between reads
        self.last_temperature = 21.0
        self.last_humidity = 50.0
        print(f"Initialized Mock DHT22 sensor on pin {pin}")
    
    def read(self):
        """Read temperature and humidity data from the mock sensor.
        
        Returns:
            tuple: (temperature in °C, humidity in %)
        """
        current_time = time.time()
        
        # Enforce minimum read interval
        if current_time - self.last_read_time < self.min_interval:
            time.sleep(self.min_interval - (current_time - self.last_read_time))
        
        # Generate realistic random variations
        self.last_temperature = max(10, min(40, self.last_temperature + random.uniform(-0.5, 0.5)))
        self.last_humidity = max(20, min(90, self.last_humidity + random.uniform(-2, 2)))
        
        self.last_read_time = time.time()
        
        # Occasionally simulate a read error
        if random.random() < 0.05:  # 5% chance of error
            return None, None
            
        return self.last_temperature, self.last_humidity


# Define BMP280 constants for mock implementation
BMP280_ADDRESS = 0x76  # Default I2C address

class MockBMP280Sensor:
    """Mock implementation of the BMP280 temperature, pressure and altitude sensor."""
    
    def __init__(self, i2c_addr=BMP280_ADDRESS):
        """Initialize the mock BMP280 sensor.
        
        Args:
            i2c_addr: The I2C address (ignored in mock implementation)
        """
        self.i2c_addr = i2c_addr
        self.last_read_time = 0
        self.min_interval = 1  # Minimum seconds between reads
        self.last_temperature = 20.0
        self.last_pressure = 1013.25  # Standard pressure at sea level (hPa)
        self.last_altitude = 0.0
        print(f"Initialized Mock BMP280 sensor at I2C address 0x{i2c_addr:x}")
    
    def read(self):
        """Read temperature, pressure and altitude data from the mock sensor.
        
        Returns:
            tuple: (temperature in °C, pressure in hPa, altitude in meters)
        """
        current_time = time.time()
        
        # Enforce minimum read interval
        if current_time - self.last_read_time < self.min_interval:
            time.sleep(self.min_interval - (current_time - self.last_read_time))
        
        # Generate realistic random variations
        self.last_temperature = max(10, min(40, self.last_temperature + random.uniform(-0.3, 0.3)))
        self.last_pressure = max(950, min(1050, self.last_pressure + random.uniform(-1, 1)))
        
        # Calculate altitude based on pressure (simplified formula)
        self.last_altitude = 44330 * (1 - (self.last_pressure / 1013.25) ** 0.1903)
        
        self.last_read_time = time.time()
        
        # Occasionally simulate a read error
        if random.random() < 0.03:  # 3% chance of error
            return None, None, None
            
        return self.last_temperature, self.last_pressure, self.last_altitude


def get_mock_sensor_data():
    """Get a complete set of mock sensor readings.
    
    Returns:
        dict: Dictionary containing all sensor readings
    """
    dht = MockDHT22Sensor(pin=4)
    bmp = MockBMP280Sensor()
    
    dht_temp, humidity = dht.read()
    bmp_temp, pressure, altitude = bmp.read()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "timestamp": timestamp,
        "dht_temperature": dht_temp,
        "humidity": humidity,
        "bmp_temperature": bmp_temp,
        "pressure": pressure,
        "altitude": altitude
    }


if __name__ == "__main__":
    # Test the mock sensors
    print("Testing mock sensors...")
    
    dht = MockDHT22Sensor(pin=4)
    bmp = MockBMP280Sensor()
    
    for _ in range(5):
        dht_temp, humidity = dht.read()
        bmp_temp, pressure, altitude = bmp.read()
        
        print(f"DHT22: {dht_temp:.1f}°C, {humidity:.1f}%")
        print(f"BMP280: {bmp_temp:.1f}°C, {pressure:.2f}hPa, {altitude:.2f}m")
        print("-" * 40)
        time.sleep(1)