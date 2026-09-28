import requests

city = input("Enter your city: ")

geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

params = {
    "name": city,
    "count": 1,
    "language": "en",
    "format": "json"
}

response = requests.get(geocoding_url, params=params)
data = response.json()

if "results" not in data:
    print("City not found")
else:
    city_name = data["results"][0]["name"]
    latitude = data["results"][0]["latitude"]
    longitude = data["results"][0]["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    temperature = weather_data["current"]["temperature_2m"]
    humidity = weather_data["current"]["relative_humidity_2m"]
    wind_speed = weather_data["current"]["wind_speed_10m"]

    print()
    print("Weather Report")
    print("City:", city_name)
    print("Temperature:", temperature, "°C")
    print("Humidity:", humidity, "%")
    print("Wind Speed:", wind_speed, "km/h")