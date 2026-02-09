import requests
from geopy.geocoders import Nominatim

def coordFinder(city: str | None):
    geolocator = Nominatim(user_agent="TerminalWeatherApp")

    if city is None:
        city = "Monterrey, Nuevo Leon"

    location = geolocator.geocode(city)

    if not location:
        return None, None

    return location.latitude, location.longitude #pyright: ignore

    
# lat_,lon_ = coordFinder(None)

def weatherGetter(lat, lon):
    api_key = open('api_key.txt', 'r').read().strip()
    url = ("https://api.openweathermap.org/data/2.5/weather"f"?lat={lat}&lon={lon}&appid={api_key}&units=metric")

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return f"Error fetching weather ({response.status_code})"

    data = response.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    return f"🌡 {temp} °C\n☁ {desc.capitalize()}"


# weatherGetter(lat_,lon_)