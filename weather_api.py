import requests

url = "https://api.open-meteo.com/v1/forecast?latitude=13.08&longitude=80.27&current=temperature_2m"

response = requests.get(url)

print(response.status_code)

data = response.json()

print(data)