python
import requests
import json

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

def search_adverse_media(query, maxrecords=20):
    params = {
        "query": f'"{query}" (arrest OR suspended OR injury OR investigation OR lawsuit OR fine)',
        "mode": "artlist",
        "maxrecords": maxrecords,
        "format": "json"
    }
    r = requests.get(GDELT_URL, params=params)
    if r.status_code != 200:
        return []
    try:
        return r.json().get('articles', [])
    except json.JSONDecodeError:
        return []

if __name__ == "__main__":
    watchlist = ["Tyreek Hill"] # edit this list per your needs
    results = {name: search_adverse_media(name) for name in watchlist}
    with open('data/raw/adverse_media.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("Saved adverse media scan.")
