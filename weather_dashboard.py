import requests
import json
import os
import sys
import time
from datetime import datetime , timedelta
from config import API_KEY

BASE_URL = "https://api.openweathermap.org/data/2.5"
CITIES_FILE = "data/cities.json"
WEATHER_ICONS = {
    'clear sky': '☀️',
    'few clouds': '🌤️',
    'scattered clouds': '⛅',
    'broken clouds': '☁️',
    'overcast clouds': '☁️',
    'light rain': '🌦️',
    'moderate rain': '🌧️',
    'heavy rain': '⛈️',
    'thunderstorm': '⛈️',
    'snow': '❄️',
    'mist': '🌫️',
    'fog': '🌫️'
}
cache = {}
CACHE_DURATION = 1800

def clear_screen():
    os.system('cls' if sys.platform == 'win32' else 'clear')

def get_current_weather(city):

    url = f"{BASE_URL}/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url , timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching current weather: {e}")
        return None

def display_weather(weather_data , unit = 'C'):

    if not weather_data:
        print("No weather data to display.")
        return
    temp = weather_data['main']['temp']
    feel_like = weather_data['main']['feels_like']
    if unit == 'F':
        temp = celcius_to_fahrenheit(temp)
        feel_like = celcius_to_fahrenheit(feel_like)
        unit_symbol = '°F'
    elif unit == 'K':
        temp = celcius_to_kelvin(temp) 
        feel_like = celcius_to_kelvin(feel_like)
        unit_symbol = 'K'
    else:
        unit_symbol = '°C'
    
    print(f"Weather for {weather_data['name']}, {weather_data['sys']['country']}")
    print(f"Conditions: {weather_data['weather'][0]['description'].title()}")
    print(f"Temperature: {temp}{unit_symbol}")
    print(f"Feels like: {feel_like}{unit_symbol}")
    print(f"Pressure: {weather_data['main']['pressure']}hpa/mBar")
    print(f"Humidity: {weather_data['main']['humidity']}%")
    print(f"Wind Speed: {weather_data['wind']['speed']} m/s")

def get_forecast_weather(city):

    url = f"{BASE_URL}/forecast?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url , timeout = 10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast weather: {e}")
        return None

def display_forecast(forecast_data):

    if not forecast_data:
        print("No forecast data to display.")
        return
    
    print("5-DAY FORECAST:")
    forecasts_by_day = {}

    for data in forecast_data['list']:
        date = datetime.fromtimestamp(data['dt']).strftime('%Y-%m-%d')
        if date not in forecasts_by_day:
            forecasts_by_day[date] = []
        forecasts_by_day[date].append(data)
    
    for date , forecasts in list(forecasts_by_day.items())[:5]:
        temps = [f["main"]["temp"] for f in forecasts]
        conditions = [f["weather"][0]["description"] for f in forecasts]

        print("\nDate: ", date)
        print(f"  High: {max(temps):.1f}°C, Low: {min(temps):.1f}°C")
        print(f"  Conditions: {max(set(conditions), key=conditions.count).title()}")

def get_cached_wether(city):
    cache_key = f"weather_{city}"

    if cache_key in cache:
        cached_data , cached_time = cache[cache_key]
        if datetime.now() - cached_time < timedelta(seconds=CACHE_DURATION):
            print("📦 Using cached data...")
            return cached_data
    
    data = get_current_weather(city)
    if data:
        cache[cache_key] = (data , datetime.now())
    return data

def load_cities():

    if not os.path.exists(CITIES_FILE):
        print("Cities file not found.")
        return []
    try:
        with open(CITIES_FILE , "r") as f:
            return json.load(f)
    except:
        print("Error loading cities from file.")
        return []

def save_city(city):
    
    cities = load_cities()
    if city.lower() not in [c.lower() for c in cities]:
        cities.append(city)
        
        os.makedirs(os.path.dirname(CITIES_FILE), exist_ok=True)
        with open(CITIES_FILE, 'w') as f:
            json.dump(cities, f, indent=2)
        
        print(f"✅ {city} saved to favorites!")

def remove_city(city):

    cities = load_cities()
    cities = [c for c in cities if c.lower() != city.lower()]
    with open(CITIES_FILE, 'w') as f:
        json.dump(cities, f, indent=2)
    print(f"❌ {city} removed from favorites.")

def show_saved_cities():

    cities = load_cities()
    if not cities:
        print("No saved cities.")
        return
    print("Saved Cities:")
    for city in cities:
        weather = get_current_weather(city)
        if weather:
            print(f"\n {city}: {weather['main']['temp']}°C - {weather['weather'][0]['description'].title()}")

def celcius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def celcius_to_kelvin(celsius):
    return celsius + 273.15

def main_menu():
    pass

if __name__ == "__main__":
    city = input("Enter the City Name: ")

    # weather_data = get_current_weather(city)
    # display_weather(weather_data)

    # forecast_data = get_forecast_weather(city)
    # display_forecast(forecast_data)