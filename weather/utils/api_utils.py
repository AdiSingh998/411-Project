import os
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()
API_KEY: Optional[str] = os.getenv('APIKEY')

# Constants
BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_UNITS = "imperial"

# Initialize a requests session
session = requests.Session()

def getweather(location: str) -> Dict[str, Any]:
    """
    Fetch current weather data for a given city.

    Args:
        location (str): Name of the city.

    Returns:
        dict: Weather data or error message.
    """
    if not API_KEY:
        return {"error": "API Key is missing!"}

    endpoint = f"{BASE_URL}/weather"
    params = {
        "q": location,
        "appid": API_KEY,
        "units": DEFAULT_UNITS,
    }

    try:
        response = session.get(endpoint, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {"error": f"City '{location}' not found."}
        return {"error": f"HTTP error occurred: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request error: {req_err}"}

def display_weather_info(weather_data: Dict[str, Any], city: str) -> None:
    """
    Display weather information or error.

    Args:
        weather_data (dict): The weather API response.
        city (str): City name requested.
    """
    if "error" in weather_data:
        print(f"Error: {weather_data['error']}")
    else:
        temp = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"].capitalize()
        humidity = weather_data["main"]["humidity"]
        print(f"\nWeather in {city}:")
        print(f"Temperature: {temp}°F")
        print(f"Description: {description}")
        print(f"Humidity: {humidity}%")

if __name__ == "__main__":
    city = input("Enter a city: ").strip()
    if not city:
        print("City name cannot be empty.")
    else:
        weather_info = getweather(city)
        display_weather_info(weather_info, city)
