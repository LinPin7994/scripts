import requests
import json

class Exchange():
    api_key = "<YOU API KEY>"
    
    def __init__(self, currency):
        self.currency = currency
        
    def send_request(self, url):
        req = requests.get(url=url)
        data = req.json()
        req.close()
        return data

    def get_currency_exchange(self):
        result = self.send_request(f"https://currate.ru/api/?get=rates&pairs={self.currency}&key={self.api_key}")
        result = result["data"][self.currency]
        return result
    
    def get_currency_usd(self):
        all_currency = self.send_request(self.api_exchange_url)
        usd = all_currency['rates']['USD']
        return usd
