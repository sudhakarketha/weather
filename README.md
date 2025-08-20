# Raspberry Pi Weather Station

This project creates a personalized weather station using a Raspberry Pi and various sensors to collect and display weather data. It also supports development on Windows using mock sensors.

## Hardware Requirements

- Raspberry Pi (3B+ or 4 recommended)
- DHT22 temperature and humidity sensor
- BMP280 barometric pressure sensor
- Jumper wires
- Breadboard
- Optional: LCD display (16x2 or similar)

## Software Requirements

- Raspberry Pi OS (formerly Raspbian)
- Python 3.x
- Required Python libraries (install via pip):
  - Adafruit_DHT
  - adafruit-circuitpython-bmp280
  - Flask (for web interface)
  - RPi.GPIO
  - matplotlib (for data visualization)

## Hardware Setup

### DHT22 Connection

1. Connect DHT22 VCC pin to Raspberry Pi 3.3V or 5V (pin 2 or 4)
2. Connect DHT22 DATA pin to Raspberry Pi GPIO4 (pin 7)
3. Connect DHT22 GND pin to Raspberry Pi GND (pin 6)
4. Connect a 10K ohm resistor between VCC and DATA pins (pull-up resistor)

### BMP280 Connection (I2C)

1. Connect BMP280 VCC to Raspberry Pi 3.3V (pin 1)
2. Connect BMP280 GND to Raspberry Pi GND (pin 9)
3. Connect BMP280 SCL to Raspberry Pi SCL (pin 5)
4. Connect BMP280 SDA to Raspberry Pi SDA (pin 3)

## Software Installation

```bash
# Update your Raspberry Pi
sudo apt-get update
sudo apt-get upgrade

# Install required packages
sudo apt-get install python3-pip
sudo apt-get install i2c-tools
sudo apt-get install python3-smbus

# Enable I2C interface (for BMP280)
sudo raspi-config
# Navigate to Interfacing Options > I2C > Yes

# Install Python libraries
pip3 install Adafruit_DHT
pip3 install adafruit-circuitpython-bmp280
pip3 install flask
pip3 install matplotlib
pip3 install RPi.GPIO
```

## Project Structure

```
weather_station/
├── sensors/
│   ├── __init__.py
│   ├── dht22.py
│   └── bmp280.py
├── data/
│   └── weather_log.csv
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── charts.js
├── templates/
│   ├── index.html
│   └── history.html
├── app.py
├── weather_logger.py
└── config.py
```

## Getting Started

### On Raspberry Pi

1. Clone this repository to your Raspberry Pi
2. Set up the hardware connections as described above
3. Install the required software and libraries
4. Run the basic sensor test script to verify your setup

```bash
python3 sensor_test.py
```

5. Start the data logging script to begin collecting weather data

```bash
python3 run_weather_station.py
```

### On Windows (Development Mode)

This project supports development on Windows using mock sensors, which simulate the behavior of real sensors for testing and development purposes.

1. Clone this repository to your Windows machine
2. Install the required development dependencies:

```bash
pip install -r requirements-dev.txt
```

3. Test the mock sensors to verify they're working correctly:

```bash
python mock_sensor_test.py
```

4. Run the weather station in development mode:

```bash
python run_weather_station.py
```

5. If you need to use mock sensors with other scripts directly, set the environment variable first:

```bash
# On Windows PowerShell
$env:USE_MOCK_SENSORS="true"
python weather_logger.py

# On Windows Command Prompt
set USE_MOCK_SENSORS=true
python weather_logger.py
```

### Troubleshooting

If you encounter numpy/pandas compatibility issues like this:

```
ValueError: numpy.dtype size changed, may indicate binary incompatibility. Expected 96 from C header, got 88 from PyObject
```

Try installing specific versions of numpy and pandas:

```bash
pip install numpy==1.24.3 pandas==2.0.3
```

The application will automatically detect that it's running on Windows and use mock sensors instead of trying to access real hardware. This allows you to develop and test the web interface, data logging, and visualization features without needing the actual Raspberry Pi hardware.

## Development Notes

### Mock Sensors

The mock sensors (`sensors/mock_sensors.py`) simulate the behavior of real sensors by generating realistic random data. They include:

- `MockDHT22Sensor`: Simulates temperature and humidity readings
- `MockBMP280Sensor`: Simulates temperature, pressure, and altitude readings

These mock sensors follow the same interface as the real sensor classes, making it easy to switch between development and production environments.

### Platform Detection

The application automatically detects whether it's running on a Raspberry Pi or another platform (like Windows) and adjusts its behavior accordingly:

```python
# Detect if running on Raspberry Pi
IS_RASPBERRY_PI = platform.system().lower() != 'windows' and os.path.exists('/sys/firmware/devicetree/base/model')

# Use mock sensors if not on Raspberry Pi
if not IS_RASPBERRY_PI:
    os.environ['USE_MOCK_SENSORS'] = 'true'
```



6. Launch the web interface to view current and historical data

```bash
python3 app.py
```

7. Access the web interface by navigating to `http://[raspberry-pi-ip]:5000` in your browser

## Next Steps

- Add more sensors (rain gauge, anemometer, etc.)
- Implement weather predictions based on barometric trends
- Set up alerts for extreme weather conditions
- Create a mobile app interface
- Add solar power for outdoor deployment

## License

MIT




Would you like me to help you create mock sensor modules for Windows development, or would you prefer guidance on setting up remote development with your Raspberry Pi?