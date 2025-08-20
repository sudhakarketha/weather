/**
 * Raspberry Pi Weather Station - Charts and UI Interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-update current readings via API if on the index page
    if (document.querySelector('.current-weather')) {
        // Update readings every 30 seconds without full page refresh
        setInterval(updateCurrentReadings, 30000);
    }
});

/**
 * Updates the current weather readings via API call
 */
function updateCurrentReadings() {
    fetch('/api/current')
        .then(response => response.json())
        .then(data => {
            // Update timestamp
            document.querySelector('.timestamp').textContent = 'Last updated: ' + data.timestamp;
            
            // Update temperature readings
            const tempElements = document.querySelectorAll('.temperature .value');
            if (tempElements.length >= 2) {
                tempElements[0].textContent = data.temperature_dht;
                tempElements[1].textContent = data.temperature_bmp;
            }
            
            // Update humidity reading
            const humidityElement = document.querySelector('.humidity .value');
            if (humidityElement) {
                humidityElement.textContent = data.humidity;
            }
            
            // Update pressure reading
            const pressureElement = document.querySelector('.pressure .value');
            if (pressureElement) {
                pressureElement.textContent = data.pressure;
            }
            
            // Update altitude reading
            const altitudeElement = document.querySelector('.altitude .value');
            if (altitudeElement) {
                altitudeElement.textContent = data.altitude;
            }
        })
        .catch(error => {
            console.error('Error updating weather data:', error);
        });
}