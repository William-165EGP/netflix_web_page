import requests

def get_twd_exchange_rate():
    url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/twd.json"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("twd", {})  # {'usd': 32.5, 'eur': 34.1, ...}
    except:
        return {}
