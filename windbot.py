import requests
import datetime
from config import TOKEN, CHAT_ID, WEATHER_API_KEY, CITY

# API
url = 'https://api.weatherapi.com/v1/forecast.json'

# Parameters
params = {
    'key': WEATHER_API_KEY,
    'q': CITY,
    'days': 2,
    'aqi': 'no',
    'alerts': 'no'
}

def decide_transportation(hourly_forecast):
    wind_direction = hourly_forecast['wind_dir']
    wind_speed = float(hourly_forecast['wind_kph'])
    gust_speed = float(hourly_forecast['gust_kph'])
    rain_mm = float(hourly_forecast['precip_mm'])

    if (wind_speed > 19 and gust_speed > 30) or (wind_speed > 22) or (gust_speed > 40):
        if 'N' in wind_direction or 'W' in wind_direction and wind_direction != 'SSW':
            return 'tram', wind_direction, wind_speed, gust_speed, rain_mm
    elif rain_mm > 1:
        return 'tram', wind_direction, wind_speed, gust_speed, rain_mm
    else:
        return 'bike', wind_direction, wind_speed, gust_speed, rain_mm

def send_message(message, wind_direction, wind_speed, gust_speed, rain_mm):
    # Define the API endpoint
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'

    # Additional info
    additional_info = f"\nWind Direction: {wind_direction}\nWind Speed: {wind_speed} km/h\nGust Speed: {gust_speed} km/h\nRain: {rain_mm} mm"

    # Parameters 
    params = {
        'chat_id': CHAT_ID,
        'text': message + additional_info
    }

    # Send 
    response = requests.post(url, params=params)

    # Check if success
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print("Failed to send message. Status code:", response.status_code)

# Check if it's before or after 8 am
if datetime.datetime.now().hour < 8:
    day = 0
else:
    day = 1

if datetime.datetime.now().weekday() not in [4, 5]:
    response = requests.get(url, params=params)

    # Check if successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()

        hourly_forecast = data['forecast']['forecastday'][day]['hour'][8]
        transport, wind_direction, wind_speed, gust_speed, rain_mm = decide_transportation(hourly_forecast)

        message = f"At 8 am, you should take the {transport}."
        send_message(message, wind_direction, wind_speed, gust_speed, rain_mm)
    else:
        print("Failed to retrieve data. Status code:", response.status_code)
