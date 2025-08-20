#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - DHT22 Sensor Module

This module provides a class for reading temperature and humidity data from the DHT22 sensor.
"""

import time
import board
import adafruit_dht
from config import DHT_PIN

class DHT22Sensor:
    """Class for interfacing with the DHT22 temperature and humidity sensor."""
    
    def __init__(self, pin=DHT_PIN):
        """Initialize the DHT22 sensor.
        
        Args:
            pin: GPIO pin number (BCM numbering) connected to the DHT22 sensor.
        """
        self.pin = pin
        self.dht_device = adafruit_dht.DHT22(getattr(board, f'D{pin}'), use_pulseio=False)
        self.last_read_time = 0
        self.read_interval = 2  # Minimum seconds between readings
        
        # Last valid readings (used as fallback if reading fails)
        self.last_temperature = None
        self.last_humidity = None
    
    def read(self):
        """Read temperature and humidity data from the sensor.
        
        Returns:
            tuple: (temperature in °C, humidity in %)
                   Returns (None, None) if reading fails.
        """
        current_time = time.time()
        
        # Ensure minimum time between readings
        if current_time - self.last_read_time < self.read_interval:
            time.sleep(self.read_interval - (current_time - self.last_read_time))
        
        try:
            temperature = self.dht_device.temperature
            humidity = self.dht_device.humidity
            
            # Update last valid readings
            self.last_temperature = temperature
            self.last_humidity = humidity
            
            self.last_read_time = time.time()
            return temperature, humidity
            
        except RuntimeError as e:
            # DHT22 sometimes fails to read, return last valid readings if available
            print(f"DHT22 reading error: {e}")
            return self.last_temperature, self.last_humidity
            
        except Exception as e:
            print(f"DHT22 sensor error: {e}")
            return self.last_temperature, self.last_humidity
    
    def read_temperature(self):
        """Read only temperature from the sensor.
        
        Returns:
            float: Temperature in °C or None if reading fails.
        """
        temperature, _ = self.read()
        return temperature
    
    def read_humidity(self):
        """Read only humidity from the sensor.
        
        Returns:
            float: Humidity in % or None if reading fails.
        """
        _, humidity = self.read()
        return humidity
    
    def cleanup(self):
        """Clean up resources used by the sensor."""
        self.dht_device.exit()