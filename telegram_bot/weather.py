import requests
import json
import datetime

class Weather():
    openweather_key = "<openweather_key>"
    open_weather_url = "http://api.openweathermap.org/data/2.5/weather?q="

    def __init__(self, city):
        self.city = city

    def get_current_weather(self):
        full_url = f"{self.open_weather_url}{self.city}&appid={self.openweather_key}&units=metric"
        req = requests.get(url=full_url)
        weather_map = req.json()
        current_weather = weather_map["main"]["temp"]
        pressure = weather_map["main"]["pressure"]
        humidity = weather_map["main"]["humidity"]
        wind = weather_map["wind"]["speed"]
        sunrise = datetime.datetime.fromtimestamp(weather_map["sys"]["sunrise"])
        sunset = datetime.datetime.fromtimestamp(weather_map["sys"]["sunset"])
        message = f"""Погода в городе: {self.city}\nТемпература: {current_weather}C°\nВлажность: {humidity}%\nДавление: {pressure} мм.рт.ст.\nВетер: {wind} м/с\nРассвет: {sunrise}\nЗакат: {sunset}"""
        return message
