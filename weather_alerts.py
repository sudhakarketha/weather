#!/usr/bin/env python3

"""
Raspberry Pi Weather Station - Weather Alerts Module

This module provides functionality to detect significant weather changes
and send alerts via various methods (console, email, etc.).
"""

import time
import datetime
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
from config import (
    ALERTS_ENABLED, TEMP_HIGH_THRESHOLD, TEMP_LOW_THRESHOLD,
    HUMIDITY_HIGH_THRESHOLD, PRESSURE_CHANGE_THRESHOLD, LOG_FILE
)

class WeatherAlerts:
    """Class for detecting and sending weather alerts."""
    
    def __init__(self, email_config=None):
        """Initialize the weather alerts system.
        
        Args:
            email_config: Dictionary containing email configuration:
                - smtp_server: SMTP server address
                - smtp_port: SMTP server port
                - username: Email account username
                - password: Email account password
                - sender: Sender email address
                - recipients: List of recipient email addresses
        """
        self.enabled = ALERTS_ENABLED
        self.email_config = email_config
        self.last_alert_time = {}
        self.alert_cooldown = 3600  # 1 hour between repeated alerts
        
        # Load historical data for trend analysis
        self.historical_data = self._load_historical_data()
    
    def _load_historical_data(self):
        """Load historical weather data for trend analysis.
        
        Returns:
            pandas.DataFrame: Historical weather data or empty DataFrame if not available
        """
        if not os.path.exists(LOG_FILE):
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(LOG_FILE)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Error loading historical data for alerts: {e}")
            return pd.DataFrame()
    
    def check_alerts(self, current_data):
        """Check for alert conditions based on current weather data.
        
        Args:
            current_data: Dictionary containing current weather data:
                - timestamp: Current timestamp
                - temperature_dht: Temperature from DHT22 sensor (°C)
                - humidity: Humidity from DHT22 sensor (%)
                - temperature_bmp: Temperature from BMP280 sensor (°C)
                - pressure: Barometric pressure from BMP280 sensor (hPa)
                - altitude: Altitude from BMP280 sensor (m)
        
        Returns:
            list: List of alert messages if any conditions are met
        """
        if not self.enabled:
            return []
        
        alerts = []
        
        # Update historical data
        self._update_historical_data()
        
        # Check temperature alerts
        if current_data.get('temperature_dht') is not None:
            temp = current_data['temperature_dht']
            if temp > TEMP_HIGH_THRESHOLD:
                alert = f"High temperature alert: {temp:.1f}°C exceeds threshold of {TEMP_HIGH_THRESHOLD}°C"
                if self._check_cooldown('high_temp'):
                    alerts.append(alert)
            elif temp < TEMP_LOW_THRESHOLD:
                alert = f"Low temperature alert: {temp:.1f}°C below threshold of {TEMP_LOW_THRESHOLD}°C"
                if self._check_cooldown('low_temp'):
                    alerts.append(alert)
        
        # Check humidity alerts
        if current_data.get('humidity') is not None:
            humidity = current_data['humidity']
            if humidity > HUMIDITY_HIGH_THRESHOLD:
                alert = f"High humidity alert: {humidity:.1f}% exceeds threshold of {HUMIDITY_HIGH_THRESHOLD}%"
                if self._check_cooldown('high_humidity'):
                    alerts.append(alert)
        
        # Check pressure change alerts
        if current_data.get('pressure') is not None and not self.historical_data.empty:
            pressure = current_data['pressure']
            pressure_change = self._calculate_pressure_change(pressure)
            if abs(pressure_change) > PRESSURE_CHANGE_THRESHOLD:
                direction = "rising" if pressure_change > 0 else "falling"
                alert = f"Significant pressure change: {direction} by {abs(pressure_change):.1f}hPa in the last hour"
                if self._check_cooldown('pressure_change'):
                    alerts.append(alert)
        
        # Send alerts if any
        if alerts:
            self._send_alerts(alerts)
        
        return alerts
    
    def _update_historical_data(self):
        """Update historical data from the log file."""
        if os.path.exists(LOG_FILE):
            try:
                df = pd.read_csv(LOG_FILE)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                self.historical_data = df
            except Exception as e:
                print(f"Error updating historical data: {e}")
    
    def _calculate_pressure_change(self, current_pressure):
        """Calculate pressure change over the last hour.
        
        Args:
            current_pressure: Current barometric pressure in hPa
        
        Returns:
            float: Pressure change in hPa over the last hour
        """
        if self.historical_data.empty:
            return 0
        
        # Get data from the last hour
        one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
        hour_data = self.historical_data[self.historical_data['timestamp'] > one_hour_ago]
        
        if hour_data.empty:
            return 0
        
        # Get the oldest pressure reading in the last hour
        oldest_pressure = hour_data.iloc[0]['pressure']
        
        # Calculate change
        return current_pressure - oldest_pressure
    
    def _check_cooldown(self, alert_type):
        """Check if enough time has passed since the last alert of this type.
        
        Args:
            alert_type: Type of alert to check cooldown for
        
        Returns:
            bool: True if alert should be sent, False if still in cooldown
        """
        current_time = time.time()
        
        if alert_type not in self.last_alert_time:
            self.last_alert_time[alert_type] = current_time
            return True
        
        time_since_last = current_time - self.last_alert_time[alert_type]
        
        if time_since_last > self.alert_cooldown:
            self.last_alert_time[alert_type] = current_time
            return True
        
        return False
    
    def _send_alerts(self, alerts):
        """Send alerts via configured methods.
        
        Args:
            alerts: List of alert messages to send
        """
        # Always print to console
        for alert in alerts:
            print(f"[ALERT] {alert}")
        
        # Send email if configured
        if self.email_config:
            self._send_email_alert(alerts)
    
    def _send_email_alert(self, alerts):
        """Send alerts via email.
        
        Args:
            alerts: List of alert messages to send
        """
        if not self.email_config:
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender']
            msg['To'] = ", ".join(self.email_config['recipients'])
            msg['Subject'] = "Weather Station Alert"
            
            # Create message body
            body = "The following weather alerts have been detected:\n\n"
            body += "\n".join([f"- {alert}" for alert in alerts])
            body += "\n\nThis is an automated message from your Raspberry Pi Weather Station."
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to server and send
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Email alert sent to {', '.join(self.email_config['recipients'])}")
            
        except Exception as e:
            print(f"Error sending email alert: {e}")

# Example usage
def main():
    """Test the weather alerts system."""
    # Example email configuration (replace with your own values)
    email_config = {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'your.email@gmail.com',
        'password': 'your-app-password',  # Use app password for Gmail
        'sender': 'your.email@gmail.com',
        'recipients': ['recipient@example.com']
    }
    
    # Initialize alerts system (without email for testing)
    alerts = WeatherAlerts()
    
    # Test with some example data
    test_data = {
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'temperature_dht': 35.0,  # High temperature to trigger alert
        'humidity': 85.0,  # High humidity to trigger alert
        'temperature_bmp': 34.8,
        'pressure': 1000.0,
        'altitude': 110.0
    }
    
    # Check for alerts
    triggered_alerts = alerts.check_alerts(test_data)
    
    if triggered_alerts:
        print("\nTest alerts triggered:")
        for alert in triggered_alerts:
            print(f"- {alert}")
    else:
        print("\nNo test alerts triggered.")

if __name__ == "__main__":
    main()