import requests

response = requests.get("https://ipinfo.io/json", timeout=10)

print(response.json())