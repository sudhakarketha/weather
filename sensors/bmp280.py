#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - BMP280 Sensor Module

This module provides a class for reading temperature, pressure, and altitude data
from the BMP280 barometric pressure sensor.
"""

import time
import board
import busio
import adafruit_bmp280
from config import BMP280_ADDRESS, SEA_LEVEL_PRESSURE

class BMP280Sensor:
    """Class for interfacing with the BMP280 barometric pressure sensor."""
    
    def __init__(self, address=BMP280_ADDRESS, sea_level_pressure=SEA_LEVEL_PRESSURE):
        """Initialize the BMP280 sensor.
        
        Args:
            address: I2C address of the BMP280 sensor (usually 0x76 or 0x77).
            sea_level_pressure: Current sea level pressure in hPa for altitude calculation.
        """
        self.address = address
        self.sea_level_pressure = sea_level_pressure
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.sensor = None
        self.connected = False
        
        # Last valid readings (used as fallback if reading fails)
        self.last_temperature = None
        self.last_pressure = None
        self.last_altitude = None
        
        # Try to connect to the sensor
        self._connect()
    
    def _connect(self):
        """Attempt to connect to the BMP280 sensor."""
        try:
            self.sensor = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c, address=self.address)
            self.sensor.sea_level_pressure = self.sea_level_pressure
            self.connected = True
            print(f"BMP280 sensor connected at address 0x{self.address:02x}")
        except ValueError:
            # Try alternative address
            alt_address = 0x77 if self.address == 0x76 else 0x76
            try:
                self.sensor = adafruit_bmp280.Adafruit_BMP280_I2C(self.i2c, address=alt_address)
                self.sensor.sea_level_pressure = self.sea_level_pressure
                self.address = alt_address
                self.connected = True
                print(f"BMP280 sensor connected at alternative address 0x{self.address:02x}")
            except ValueError:
                print("BMP280 sensor not found. Check connections and I2C address.")
                self.connected = False
        except Exception as e:
            print(f"Error connecting to BMP280 sensor: {e}")
            self.connected = False
    
    def read(self):
        """Read temperature, pressure, and altitude data from the sensor.
        
        Returns:
            tuple: (temperature in °C, pressure in hPa, altitude in meters)
                   Returns (None, None, None) if sensor is not connected or reading fails.
        """
        if not self.connected:
            # Try to reconnect
            self._connect()
            if not self.connected:
                return self.last_temperature, self.last_pressure, self.last_altitude
        
        try:
            temperature = self.sensor.temperature
            pressure = self.sensor.pressure
            altitude = self.sensor.altitude
            
            # Update last valid readings
            self.last_temperature = temperature
            self.last_pressure = pressure
            self.last_altitude = altitude
            
            return temperature, pressure, altitude
            
        except Exception as e:
            print(f"BMP280 reading error: {e}")
            return self.last_temperature, self.last_pressure, self.last_altitude
    
    def read_temperature(self):
        """Read only temperature from the sensor.
        
        Returns:
            float: Temperature in °C or None if reading fails.
        """
        temperature, _, _ = self.read()
        return temperature
    
    def read_pressure(self):
        """Read only pressure from the sensor.
        
        Returns:
            float: Pressure in hPa or None if reading fails.
        """
        _, pressure, _ = self.read()
        return pressure
    
    def read_altitude(self):
        """Read only altitude from the sensor.
        
        Returns:
            float: Altitude in meters or None if reading fails.
        """
        _, _, altitude = self.read()
        return altitude
    
    def set_sea_level_pressure(self, pressure):
        """Set the sea level pressure for accurate altitude calculations.
        
        Args:
            pressure: Current sea level pressure in hPa.
        """
        self.sea_level_pressure = pressure
        if self.connected:
            self.sensor.sea_level_pressure = pressure