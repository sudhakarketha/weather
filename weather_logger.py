#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Weather Logger

This script reads data from the connected sensors (DHT22 and BMP280),
logs the data to a CSV file, and provides functions for data retrieval.
It also supports displaying data on an LCD screen and sending weather alerts.
On non-Raspberry Pi systems, it uses mock sensors for development.
"""

import time
import datetime
import csv
import os
import sys

# Check if we're using mock sensors
USE_MOCK_SENSORS = os.environ.get('USE_MOCK_SENSORS', 'false').lower() == 'true'

# Import appropriate sensor modules based on environment
if USE_MOCK_SENSORS:
    print("Using mock sensors for development")
    from sensors.mock_sensors import MockDHT22Sensor, MockBMP280Sensor
else:
    import board
    import adafruit_dht
    import adafruit_bmp280
    import busio

# Import custom modules
from config import LOG_INTERVAL, DATA_DIR, LOG_FILE
try:
    from lcd_display import LCDDisplay
    lcd_available = True
except ImportError:
    lcd_available = False
    print("LCD display module not available. Continuing without LCD support.")

try:
    from weather_alerts import WeatherAlerts
    alerts_available = True
except ImportError:
    alerts_available = False
    print("Weather alerts module not available. Continuing without alerts support.")

# Configuration is now imported from config.py

# DHT_PIN is now imported from config.py

# Import sensor configuration from config
from config import DHT_PIN, BMP280_ADDRESS

# Setup sensors based on environment
if USE_MOCK_SENSORS:
    # Setup mock DHT22 sensor
    try:
        dht = MockDHT22Sensor(pin=DHT_PIN)
        print(f"Mock DHT22 sensor initialized on pin {DHT_PIN}")
    except Exception as e:
        print(f"Error initializing mock DHT22 sensor: {e}")
        dht = None
    
    # Setup mock BMP280 sensor
    try:
        bmp280 = MockBMP280Sensor(i2c_addr=BMP280_ADDRESS)
        bmp280_found = True
        print(f"Mock BMP280 sensor initialized at address 0x{BMP280_ADDRESS:x}")
    except Exception as e:
        print(f"Error initializing mock BMP280 sensor: {e}")
        bmp280_found = False
else:
    # Setup real DHT22 sensor
    try:
        dht_pin = getattr(board, f"D{DHT_PIN}")  # Convert pin number to board.D* format
        dht = adafruit_dht.DHT22(dht_pin, use_pulseio=False)
        print(f"DHT22 sensor initialized on pin D{DHT_PIN}")
    except Exception as e:
        print(f"Error initializing DHT22 sensor: {e}")
        dht = None

    # Setup I2C for BMP280 sensor
    i2c = busio.I2C(board.SCL, board.SDA)

    # Setup BMP280 sensor
    try:
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=BMP280_ADDRESS)
        bmp280_found = True
        print(f"BMP280 sensor initialized at address 0x{BMP280_ADDRESS:x}")
    except ValueError:
        # Try alternative address if the configured one fails
        alt_address = 0x77 if BMP280_ADDRESS == 0x76 else 0x76
        try:
            bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=alt_address)
            bmp280_found = True
            print(f"BMP280 sensor initialized at alternative address 0x{alt_address:x}")
        except ValueError:
            print("BMP280 sensor not found. Check connections and I2C address.")
            bmp280_found = False

    if bmp280_found and not USE_MOCK_SENSORS:
        # Configure the sensor
        bmp280.sea_level_pressure = 1013.25  # Standard pressure at sea level in hPa

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize log file if it doesn't exist
def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'temperature_dht', 'humidity', 'temperature_bmp', 'pressure', 'altitude'])
        print(f"Created log file: {LOG_FILE}")

# Read data from DHT22 sensor
def read_dht22():
    if dht is None:
        return None, None
        
    try:
        if USE_MOCK_SENSORS:
            temperature, humidity = dht.read()
        else:
            temperature = dht.temperature
            humidity = dht.humidity
        return temperature, humidity
    except RuntimeError:
        # DHT22 sometimes fails to read, return None values
        return None, None
    except Exception as e:
        print(f"DHT22 error: {e}")
        return None, None

# Read data from BMP280 sensor
def read_bmp280():
    if not bmp280_found:
        return None, None, None
    
    try:
        if USE_MOCK_SENSORS:
            temperature, pressure, altitude = bmp280.read()
        else:
            temperature = bmp280.temperature
            pressure = bmp280.pressure
            altitude = bmp280.altitude
        return temperature, pressure, altitude
    except Exception as e:
        print(f"BMP280 error: {e}")
        return None, None, None

# Log sensor data to CSV file
def log_data(temp_dht=None, humidity=None, temp_bmp=None, pressure=None, altitude=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Read sensor data if not provided
    if temp_dht is None or humidity is None:
        temp_dht, humidity = read_dht22()
    
    if temp_bmp is None or pressure is None or altitude is None:
        temp_bmp, pressure, altitude = read_bmp280()
    
    # Log data to CSV
    with open(LOG_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, temp_dht, humidity, temp_bmp, pressure, altitude])
    
    # Print current readings
    print(f"[{timestamp}] Logged weather data:")
    if temp_dht is not None:
        print(f"  DHT22: {temp_dht:.1f}°C, {humidity:.1f}%")
    else:
        print("  DHT22: Reading failed")
    
    if temp_bmp is not None:
        print(f"  BMP280: {temp_bmp:.1f}°C, {pressure:.1f}hPa, {altitude:.1f}m")
    else:
        print("  BMP280: Reading failed or not connected")
        
    # Return the readings for use by other functions
    return temp_dht, humidity, temp_bmp, pressure, altitude

# Main function
def main():
    """Main function to run the weather logger."""
    # Access the global variables
    global lcd_available, alerts_available
    
    print("Raspberry Pi Weather Station - Data Logger")
    print("=========================================")
    
    # Initialize log file
    init_log_file()
    
    # Initialize LCD if available
    lcd = None
    if lcd_available:
        try:
            lcd = LCDDisplay()
            lcd.display_message("Weather Station", "Starting...")
        except Exception as e:
            print(f"LCD initialization error: {e}")
            lcd_available = False
    
    # Initialize weather alerts if available
    alerts = None
    if alerts_available:
        try:
            alerts = WeatherAlerts()
        except Exception as e:
            print(f"Weather alerts initialization error: {e}")
            alerts_available = False
    
    print(f"Logging data every {LOG_INTERVAL} seconds. Press Ctrl+C to stop.")
    
    try:
        while True:
            # Read sensor data and log it
            temp_dht, humidity, temp_bmp, pressure, altitude = log_data()
            
            # Update LCD if available
            if lcd_available and lcd:
                if temp_dht is not None and humidity is not None:
                    lcd.display_weather(temp_dht, humidity, pressure)
                elif temp_bmp is not None:
                    # Fallback to BMP280 temperature if DHT22 fails
                    lcd.display_weather(temp_bmp, humidity, pressure)
            
            # Check for weather alerts if available
            # Temporarily disable alerts functionality for development
            pass
            # Uncomment when alerts functionality is implemented
            # if alerts_available and alerts:
            #     if temp_dht is not None and humidity is not None:
            #         alerts.check_temperature(temp_dht)
            #         alerts.check_humidity(humidity)
            #     elif temp_bmp is not None:
            #         # Fallback to BMP280 temperature if DHT22 fails
            #         alerts.check_temperature(temp_bmp)
            #     
            #     if pressure is not None:
            #         alerts.check_pressure(pressure)
            
            time.sleep(LOG_INTERVAL)
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        print("Cleaning up...")
        if dht is not None and not USE_MOCK_SENSORS:
            try:
                dht.exit()
            except:
                pass
        
        # Clear LCD if available
        if 'lcd' in locals() and lcd is not None:
            try:
                lcd.clear()
                lcd.display_message("Weather Station", "Shutdown")
                time.sleep(2)
                lcd.clear()
            except:
                pass