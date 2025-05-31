import requests

def get_netflix_price_data(plan="Standard"):
    url = "https://github.com/William-165EGP/nf_price_comp/raw/refs/heads/main/static.json"
    resp = requests.get(url)
    raw_data = resp.json()

    result = []

    for code, info in raw_data.items():
        try:
            price = info["og_price"].get(plan, None)
            if price is not None:
                result.append({
                    "country": info["full_name"],
                    "currency": info["currency"],
                    "price": price
                })
        except:
            continue

    return result

