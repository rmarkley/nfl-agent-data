import requests
import json

NGS_PASSING_URL = "https://appapi.ngs.nfl.com/statboard/passing"

def get_ngs_passing(season, week=None):
    params = {"season": season, "seasonType": "REG"}
    if week:
        params["week"] = week
    r = requests.get(NGS_PASSING_URL, params=params)
    if r.status_code != 200:
        print(f"NGS request failed: {r.status_code}")
        return {}
    return r.json()

if __name__ == "__main__":
    data = get_ngs_passing(2025)
    with open('data/raw/ngs_passing.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("Saved Next Gen Stats passing data.")
