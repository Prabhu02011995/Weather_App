from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)


# ========================================
# WEATHER CONDITION FUNCTION
# ========================================

def get_weather_details(code):

    if code == 0:
        return "Clear Sky ☀️", "clear"

    elif code in [1, 2, 3]:
        return "Cloudy 🌤️", "cloudy"

    elif code in [45, 48]:
        return "Fog 🌫️", "fog"

    elif code in [51, 53, 55, 56, 57]:
        return "Drizzle 🌦️", "rain"

    elif code in [61, 63, 65, 66, 67]:
        return "Rain 🌧️", "rain"

    elif code in [71, 73, 75, 77]:
        return "Snow ❄️", "snow"

    elif code in [80, 81, 82]:
        return "Rain Showers 🌦️", "rain"

    elif code in [95, 96, 99]:
        return "Thunderstorm ⛈️", "thunderstorm"

    else:
        return "Unknown", "clear"


# ========================================
# HOME PAGE
# ========================================

@app.route("/", methods=["GET", "POST"])
def home():

    weather = None
    forecast = None
    error = None

    background = "clear"

    city = ""

    # ====================================
    # WHEN USER SEARCHES
    # ====================================

    if request.method == "POST":

        city = request.form.get("city", "").strip()

        # Check empty city
        if not city:

            error = "Please enter a city name."

        else:

            try:

                # ====================================
                # STEP 1: FIND CITY
                # ====================================

                geocoding_url = (
                    "https://geocoding-api.open-meteo.com/"
                    "v1/search"
                )

                geocoding_params = {

                    "name": city,

                    "count": 1,

                    "language": "en",

                    "format": "json"
                }

                geocoding_response = requests.get(

                    geocoding_url,

                    params=geocoding_params,

                    timeout=10
                )

                geocoding_response.raise_for_status()

                geocoding_data = geocoding_response.json()


                # ====================================
                # CITY NOT FOUND
                # ====================================

                if not geocoding_data.get("results"):

                    error = "City not found. Try another city."

                else:

                    location = geocoding_data["results"][0]

                    city_name = location["name"]

                    latitude = location["latitude"]

                    longitude = location["longitude"]


                    # ====================================
                    # STEP 2: WEATHER API
                    # ====================================

                    weather_url = (
                        "https://api.open-meteo.com/"
                        "v1/forecast"
                    )

                    weather_params = {

                        "latitude": latitude,

                        "longitude": longitude,

                        "current": (
                            "temperature_2m,"
                            "relative_humidity_2m,"
                            "wind_speed_10m,"
                            "weather_code"
                        ),

                        "daily": (
                            "temperature_2m_max,"
                            "temperature_2m_min,"
                            "weather_code"
                        ),

                        "forecast_days": 5,

                        "timezone": "auto"
                    }

                    weather_response = requests.get(

                        weather_url,

                        params=weather_params,

                        timeout=10
                    )

                    weather_response.raise_for_status()

                    weather_data = weather_response.json()


                    # ====================================
                    # STEP 3: CURRENT WEATHER
                    # ====================================

                    current = weather_data["current"]

                    weather_code = current["weather_code"]

                    condition, background = (
                        get_weather_details(weather_code)
                    )


                    weather = {

                        "city": city_name,

                        "temperature":
                            current["temperature_2m"],

                        "humidity":
                            current["relative_humidity_2m"],

                        "wind_speed":
                            current["wind_speed_10m"],

                        "condition":
                            condition
                    }


                    # ====================================
                    # STEP 4: 5-DAY FORECAST
                    # ====================================

                    daily = weather_data["daily"]

                    forecast = []


                    for i in range(5):

                        # Get API date

                        date_text = daily["time"][i]


                        # Convert text into date

                        date_object = datetime.strptime(

                            date_text,

                            "%Y-%m-%d"
                        )


                        # First day = Today

                        if i == 0:

                            display_date = "Today"

                        else:

                            display_date = (
                                date_object.strftime("%A")
                            )


                        # Forecast weather condition

                        forecast_code = (
                            daily["weather_code"][i]
                        )

                        forecast_condition, _ = (
                            get_weather_details(
                                forecast_code
                            )
                        )


                        # Add forecast information

                        forecast.append({

                            "date": display_date,

                            "max_temp":
                                daily[
                                    "temperature_2m_max"
                                ][i],

                            "min_temp":
                                daily[
                                    "temperature_2m_min"
                                ][i],

                            "condition":
                                forecast_condition
                        })


            # ====================================
            # INTERNET / API ERROR
            # ====================================

            except requests.RequestException:

                error = (
                    "Unable to connect to the "
                    "weather service. Please try again."
                )


            # ====================================
            # DATA ERROR
            # ====================================

            except (
                KeyError,
                ValueError,
                TypeError
            ):

                error = (
                    "Weather information is unavailable. "
                    "Please try again."
                )


    # ========================================
    # SEND DATA TO HTML
    # ========================================

    return render_template(

        "index.html",

        weather=weather,

        forecast=forecast,

        error=error,

        background=background,

        city=city
    )


# ========================================
# START FLASK
# ========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        port=5001
    )