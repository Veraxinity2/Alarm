import requests
import json
import os

CONFIG_PATH = os.path.expanduser("~/Desktop/alarm_app/config/weather.json")

class WeatherChecker:
    def __init__(self):
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
        self.api_key = config["api_key"]
        self.city = config["city"]

    def get_weather(self):
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={self.city}&appid={self.api_key}&units=metric"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            weather = data["weather"][0]["main"]
            temp = data["main"]["temp"]
            return weather, temp
        except Exception as e:
            print(f"[Weather Error] {e}")
            return None, None

    def should_alert(self, weather):
        return weather in ["Rain", "Snow", "Thunderstorm"]
