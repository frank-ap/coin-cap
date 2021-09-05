import requests
response = requests.get('https://community-api.coinmetrics.io/v4/catalog/assets').json()
print(response)