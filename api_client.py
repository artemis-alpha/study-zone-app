import requests
import json

class ZenQuotesAPI:
    def __init__(self):
        self.base_url = "https://zenquotes.io/api/today"
    
    def get_thought_of_day(self):
        try:
            response = requests.get(self.base_url)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    quote = data[0]
                    return f"\"{quote['q']}\" - {quote['a']}"
            return "The best way to get started is to quit talking and begin doing. - Walt Disney"
        except:
            return "The future depends on what you do today. - Mahatma Gandhi"