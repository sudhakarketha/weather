#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - LCD Display Module

This module provides functionality to display weather data on a 16x2 LCD display
connected to the Raspberry Pi via GPIO pins.
"""

import time
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
from config import (LCD_ENABLED, LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7, 
                    LCD_COLS, LCD_ROWS)
from sensors.dht22 import DHT22Sensor
from sensors.bmp280 import BMP280Sensor

class LCDDisplay:
    """Class for displaying weather data on a 16x2 LCD display."""
    
    def __init__(self):
        """Initialize the LCD display if enabled in config."""
        self.enabled = LCD_ENABLED
        self.lcd = None
        
        if not self.enabled:
            print("LCD display is disabled in config.py")
            return
        
        try:
            # Initialize LCD display
            rs = digitalio.DigitalInOut(getattr(board, f'D{LCD_RS}'))
            en = digitalio.DigitalInOut(getattr(board, f'D{LCD_EN}'))
            d4 = digitalio.DigitalInOut(getattr(board, f'D{LCD_D4}'))
            d5 = digitalio.DigitalInOut(getattr(board, f'D{LCD_D5}'))
            d6 = digitalio.DigitalInOut(getattr(board, f'D{LCD_D6}'))
            d7 = digitalio.DigitalInOut(getattr(board, f'D{LCD_D7}'))
            
            self.lcd = characterlcd.Character_LCD_Mono(
                rs, en, d4, d5, d6, d7, LCD_COLS, LCD_ROWS)
            
            # Clear the LCD
            self.lcd.clear()
            
            # Display startup message
            self.lcd.message = "Weather Station\nInitializing..."
            time.sleep(2)
            self.lcd.clear()
            
            print("LCD display initialized successfully")
            
        except Exception as e:
            print(f"Error initializing LCD display: {e}")
            self.enabled = False
    
    def display_weather_data(self, temp, humidity, pressure):
        """Display current weather data on the LCD.
        
        Args:
            temp: Temperature in °C
            humidity: Humidity in %
            pressure: Barometric pressure in hPa
        """
        if not self.enabled or self.lcd is None:
            return
        
        try:
            # Format temperature and humidity for top row
            if temp is not None and humidity is not None:
                row1 = f"T:{temp:.1f}C H:{humidity:.1f}%"
            else:
                row1 = "Temp/Hum: Error"
            
            # Format pressure for bottom row
            if pressure is not None:
                row2 = f"Press: {pressure:.1f}hPa"
            else:
                row2 = "Press: Error"
            
            # Update LCD
            self.lcd.clear()
            self.lcd.message = f"{row1}\n{row2}"
            
        except Exception as e:
            print(f"Error updating LCD display: {e}")
    
    def display_message(self, message):
        """Display a custom message on the LCD.
        
        Args:
            message: Message to display (max 32 characters, will be truncated if longer)
        """
        if not self.enabled or self.lcd is None:
            return
        
        try:
            self.lcd.clear()
            self.lcd.message = message[:32]  # Truncate if too long
        except Exception as e:
            print(f"Error displaying message on LCD: {e}")
    
    def clear(self):
        """Clear the LCD display."""
        if not self.enabled or self.lcd is None:
            return
        
        try:
            self.lcd.clear()
        except Exception as e:
            print(f"Error clearing LCD display: {e}")

# Example usage
def main():
    """Test the LCD display with sensor data."""
    # Initialize sensors
    dht_sensor = DHT22Sensor()
    bmp_sensor = BMP280Sensor()
    
    # Initialize LCD display
    lcd = LCDDisplay()
    
    try:
        while True:
            # Read sensor data
            temp, humidity = dht_sensor.read()
            _, pressure, _ = bmp_sensor.read()
            
            # Display on LCD
            lcd.display_weather_data(temp, humidity, pressure)
            
            # Wait before next update
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nLCD test interrupted by user.")
    finally:
        # Clean up
        lcd.clear()
        dht_sensor.cleanup()

if __name__ == "__main__":
    main()