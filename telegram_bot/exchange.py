from locale import currency
from urllib import response
import requests
import json

class Exchange():
    api_exchange_url = "https://cdn.cur.su/api/latest.json"
    
    def __init__(self, currency):
        self.currency = currency
        self.currency_first = currency.split("/")[0]
        self.currency_second = currency.split("/")[1]

    def send_request(self, url):
        req = requests.get(url=url)
        data = req.json()
        req.close()
        return data

    def get_currency_exchange(self):
        all_currency = self.send_request(self.api_exchange_url)
        first_currency = all_currency['rates'][self.currency_first]
        second_currency = all_currency['rates'][self.currency_second]
        return first_currency, second_currency
    
    def get_currency_usd(self):
        all_currency = self.send_request(self.api_exchange_url)
        usd = all_currency['rates']['USD']
        return usd
