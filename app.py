#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Web Interface

This Flask application provides a web interface to view current and historical
weather data collected by the weather_logger.py script.
"""

import os
import csv
import datetime
import json
from flask import Flask, render_template, jsonify
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io
import base64

# Import sensor reading functions
from weather_logger import read_dht22, read_bmp280, LOG_FILE

app = Flask(__name__)

# Function to get current sensor readings
def get_current_readings():
    # Read sensor data
    temp_dht, humidity = read_dht22()
    temp_bmp, pressure, altitude = read_bmp280()
    
    # Format data for display
    readings = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'temperature_dht': f"{temp_dht:.1f}°C" if temp_dht is not None else "N/A",
        'humidity': f"{humidity:.1f}%" if humidity is not None else "N/A",
        'temperature_bmp': f"{temp_bmp:.1f}°C" if temp_bmp is not None else "N/A",
        'pressure': f"{pressure:.1f}hPa" if pressure is not None else "N/A",
        'altitude': f"{altitude:.1f}m" if altitude is not None else "N/A"
    }
    
    return readings

# Function to read historical data from CSV
def get_historical_data(hours=24):
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        # Read data from CSV file
        df = pd.read_csv(LOG_FILE)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter data for the specified time period
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=hours)
        df = df[df['timestamp'] > cutoff_time]
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        return df
    except Exception as e:
        print(f"Error reading historical data: {e}")
        return []

# Function to generate temperature chart
def generate_temperature_chart(hours=24):
    df = get_historical_data(hours)
    
    if len(df) == 0:
        return None
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['temperature_dht'], 'r-', label='DHT22')
    plt.plot(df['timestamp'], df['temperature_bmp'], 'b-', label='BMP280')
    plt.title('Temperature History')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

# Function to generate humidity chart
def generate_humidity_chart(hours=24):
    df = get_historical_data(hours)
    
    if len(df) == 0:
        return None
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['humidity'], 'g-')
    plt.title('Humidity History')
    plt.xlabel('Time')
    plt.ylabel('Humidity (%)')
    plt.grid(True)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

# Function to generate pressure chart
def generate_pressure_chart(hours=24):
    df = get_historical_data(hours)
    
    if len(df) == 0:
        return None
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['timestamp'], df['pressure'], 'b-')
    plt.title('Barometric Pressure History')
    plt.xlabel('Time')
    plt.ylabel('Pressure (hPa)')
    plt.grid(True)
    plt.tight_layout()
    
    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

# Routes
@app.route('/')
def index():
    current = get_current_readings()
    return render_template('index.html', current=current)

@app.route('/history')
def history():
    # Generate charts
    temp_chart = generate_temperature_chart()
    humidity_chart = generate_humidity_chart()
    pressure_chart = generate_pressure_chart()
    
    return render_template('history.html', 
                           temp_chart=temp_chart,
                           humidity_chart=humidity_chart,
                           pressure_chart=pressure_chart)

@app.route('/api/current')
def api_current():
    return jsonify(get_current_readings())

@app.route('/api/history/<int:hours>')
def api_history(hours=24):
    df = get_historical_data(hours)
    if len(df) == 0:
        return jsonify([])
    
    # Convert DataFrame to list of dictionaries
    records = df.to_dict('records')
    
    # Convert timestamps to strings
    for record in records:
        record['timestamp'] = record['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify(records)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create static directory if it doesn't exist
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)