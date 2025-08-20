#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Main Runner

This script serves as the main entry point for the Raspberry Pi Weather Station.
It starts the data logging process and the web interface in separate threads.
It supports both Raspberry Pi hardware and development on Windows using mock sensors.
"""

import threading
import time
import os
import sys
import importlib.util
import platform

# Detect operating system
IS_RASPBERRY_PI = platform.system().lower() != 'windows' and os.path.exists('/sys/firmware/devicetree/base/model')

def check_module(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None

def check_dependencies():
    """Check if all required dependencies are installed."""
    if IS_RASPBERRY_PI:
        required_modules = [
            'adafruit_dht',
            'adafruit_bmp280',
            'board',
            'busio',
            'flask',
            'matplotlib'
        ]
    else:
        # For non-Raspberry Pi systems, we only need these modules
        required_modules = [
            'flask',
            'matplotlib'
        ]
    
    missing_modules = []
    for module in required_modules:
        if not check_module(module):
            missing_modules.append(module)
    
    if missing_modules:
        print("Error: Missing required Python modules:")
        for module in missing_modules:
            print(f"  - {module}")
        
        if IS_RASPBERRY_PI:
            print("\nPlease install the missing modules using:")
            print("pip install -r requirements.txt")
        else:
            print("\nPlease install the missing modules using:")
            print("pip install -r requirements-dev.txt")
        return False
    
    return True

def setup_environment():
    """Set up the environment based on the platform."""
    if not IS_RASPBERRY_PI:
        print("Running on non-Raspberry Pi system. Using mock sensors.")
        # Create a module-level variable to indicate mock mode
        os.environ['USE_MOCK_SENSORS'] = 'true'

def start_data_logger():
    """Start the weather data logger in a separate process."""
    print("Starting weather data logger...")
    import weather_logger
    weather_logger.main()

def start_web_interface():
    """Start the Flask web interface."""
    print("Starting web interface...")
    import app
    app.app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    """Main function to start the weather station."""
    print("Raspberry Pi Weather Station")
    print("===========================")
    
    # Set up environment based on platform
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Start data logger in a separate thread
    logger_thread = threading.Thread(target=start_data_logger)
    logger_thread.daemon = True
    logger_thread.start()
    
    # Give the logger a moment to initialize
    time.sleep(2)
    
    # Start web interface (this will block)
    start_web_interface()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWeather station stopped by user.")
    except Exception as e:
        print(f"Error: {e}")