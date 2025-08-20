#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Configuration

This file contains configuration settings for the weather station project.
Edit these values to customize your setup.
"""

import os

# Sensor Configuration
DHT_PIN = 4  # GPIO pin for DHT22 sensor (BCM numbering)
BMP280_ADDRESS = 0x76  # I2C address for BMP280 (0x76 or 0x77)
SEA_LEVEL_PRESSURE = 1013.25  # Standard sea level pressure in hPa

# Data Logging Configuration
DATA_DIR = "data"  # Directory to store data files
LOG_FILE = os.path.join(DATA_DIR, "weather_log.csv")  # CSV file for weather data
LOG_INTERVAL = 300  # Logging interval in seconds (default: 5 minutes)

# Web Interface Configuration
WEB_HOST = "0.0.0.0"  # Listen on all interfaces
WEB_PORT = 5000  # Port for web server
DEBUG_MODE = True  # Enable/disable Flask debug mode

# Display Configuration (if using LCD display)
LCD_ENABLED = False  # Set to True if using an LCD display
LCD_RS = 27  # LCD RS pin (BCM numbering)
LCD_EN = 22  # LCD EN pin (BCM numbering)
LCD_D4 = 25  # LCD D4 pin (BCM numbering)
LCD_D5 = 24  # LCD D5 pin (BCM numbering)
LCD_D6 = 23  # LCD D6 pin (BCM numbering)
LCD_D7 = 18  # LCD D7 pin (BCM numbering)
LCD_COLS = 16  # LCD columns
LCD_ROWS = 2  # LCD rows

# Alert Configuration
ALERTS_ENABLED = False  # Enable/disable weather alerts
TEMP_HIGH_THRESHOLD = 30.0  # High temperature threshold in °C
TEMP_LOW_THRESHOLD = 0.0  # Low temperature threshold in °C
HUMIDITY_HIGH_THRESHOLD = 80.0  # High humidity threshold in %
PRESSURE_CHANGE_THRESHOLD = 3.0  # Pressure change threshold in hPa/hour