#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Sensor Test Script

This script tests the connection and functionality of the DHT22 temperature/humidity
sensor and the BMP280 barometric pressure sensor.
"""

import time
import board
import adafruit_dht
import adafruit_bmp280
import busio

# Define GPIO pin for DHT22 sensor
DHT_PIN = board.D4  # GPIO4

# Setup DHT22 sensor
dht = adafruit_dht.DHT22(DHT_PIN, use_pulseio=False)

# Setup I2C for BMP280 sensor
i2c = busio.I2C(board.SCL, board.SDA)

# Setup BMP280 sensor
try:
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)  # Default address
    bmp280_found = True
except ValueError:
    try:
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)  # Alternative address
        bmp280_found = True
    except ValueError:
        print("BMP280 sensor not found. Check connections and I2C address.")
        bmp280_found = False

if bmp280_found:
    # Configure the sensor
    bmp280.sea_level_pressure = 1013.25  # Standard pressure at sea level in hPa

# Function to test DHT22 sensor
def test_dht22():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        print(f"DHT22 Sensor - Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
        return True
    except RuntimeError as e:
        print(f"DHT22 sensor error: {e}")
        return False
    except Exception as e:
        print(f"DHT22 sensor error: {e}")
        return False

# Function to test BMP280 sensor
def test_bmp280():
    if not bmp280_found:
        return False
    
    try:
        temperature = bmp280.temperature
        pressure = bmp280.pressure
        altitude = bmp280.altitude
        print(f"BMP280 Sensor - Temperature: {temperature:.1f}°C, Pressure: {pressure:.1f}hPa, Altitude: {altitude:.1f}m")
        return True
    except Exception as e:
        print(f"BMP280 sensor error: {e}")
        return False

# Main test function
def main():
    print("\nRaspberry Pi Weather Station - Sensor Test")
    print("===========================================\n")
    
    print("Testing sensors...\n")
    
    # Test each sensor multiple times
    for i in range(5):
        print(f"Test {i+1}/5:")
        
        dht_success = test_dht22()
        bmp_success = test_bmp280()
        
        if dht_success and bmp_success:
            print("All sensors working correctly!")
        elif dht_success:
            print("DHT22 sensor working, BMP280 sensor not working.")
        elif bmp_success:
            print("BMP280 sensor working, DHT22 sensor not working.")
        else:
            print("No sensors working. Check connections.")
        
        print("\nWaiting for next test...")
        time.sleep(2)  # DHT22 needs at least 2 seconds between readings
    
    print("\nSensor test complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    finally:
        # Clean up
        print("Cleaning up...")
        dht.exit()